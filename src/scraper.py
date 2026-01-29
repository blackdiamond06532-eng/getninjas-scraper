"""
Scraper Google Maps para profissionais de guincho
"""
import asyncio
import random
import re
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
import config
from proxy_manager import ProxyManager


class GoogleMapsScraper:
    """Scraper para Google Maps usando Playwright"""
    
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    async def init_browser(self):
        """Inicializa navegador com proxy"""
        proxy_config = self.proxy_manager.get_proxy_config()
        
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=config.BROWSER_ARGS
        )
        
        context_options = {
            'viewport': config.VIEWPORT,
            'user_agent': config.USER_AGENT,
            'locale': 'pt-BR',
            'timezone_id': 'America/Sao_Paulo',
        }
        
        if proxy_config:
            context_options['proxy'] = proxy_config
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Stealth mode (ignorar se falhar)
        try:
            from playwright_stealth import stealth_async
            await stealth_async(self.page)
        except Exception as e:
            print(f"   ⚠️  Stealth mode não disponível: {e}")
        
        print(f"  🌐 Navegador iniciado {'com proxy' if proxy_config else 'sem proxy'}")
    
    async def cleanup(self):
        """Fecha recursos"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"   ⚠️  Erro ao fechar navegador: {e}")
    
    async def scrape_city(self, city: str, state: str) -> List[Dict]:
        """Scrape profissionais de guincho em uma cidade via Google Maps"""
        city_name = city.replace("-", " ").title()
        search_query = config.SEARCH_QUERY_TEMPLATE.format(city=city_name, state=state.upper())
        
        print(f"\n🏙️  Processando: {city_name}/{state.upper()}")
        print(f"   🔍 Busca: \"{search_query}\"")
        
        professionals = []
        
        try:
            # 1. Navegar para Google Maps
            await self.page.goto(config.BASE_URL_GOOGLE_MAPS, wait_until='domcontentloaded', timeout=config.TIMEOUT_NAVIGATION)
            await asyncio.sleep(random.uniform(3, 5))
            
            # 2. Fazer busca
            await self._perform_search(search_query)
            
            # 3. Scroll para carregar resultados
            await self._scroll_results_panel()
            
            # 4. Extrair profissionais
            professionals = await self._extract_professionals(city_name, state.upper())
            
            print(f"   ✅ {len(professionals)} profissionais encontrados")
        
        except Exception as e:
            print(f"   ❌ Erro ao processar {city_name}: {e}")
        
        return professionals
    
    async def _perform_search(self, query: str):
        """Realiza busca no Google Maps"""
        try:
            # Aguardar e preencher campo de busca
            search_box = await self.page.wait_for_selector(
                config.SELECTORS['search_box'], 
                timeout=config.TIMEOUT_ELEMENT,
                state='visible'
            )
            
            await search_box.click()
            await asyncio.sleep(0.5)
            await search_box.fill(query)
            await asyncio.sleep(1)
            await search_box.press("Enter")
            
            # Aguardar resultados carregarem
            await asyncio.sleep(random.uniform(5, 7))
            
        except Exception as e:
            print(f"   ⚠️  Erro na busca: {e}")
            raise
    
    async def _scroll_results_panel(self):
        """Scroll no painel de resultados para carregar mais empresas"""
        try:
            # Aguardar painel de resultados
            await self.page.wait_for_selector(
                config.SELECTORS['results_panel'], 
                timeout=config.TIMEOUT_ELEMENT
            )
            
            await asyncio.sleep(2)
            
            # Scroll múltiplas vezes
            for i in range(config.SCROLL_ATTEMPTS):
                await self.page.evaluate('''
                    () => {
                        const panel = document.querySelector('div[role="feed"]');
                        if (panel) {
                            panel.scrollTop = panel.scrollHeight;
                        }
                    }
                ''')
                
                await asyncio.sleep(config.DELAY_BETWEEN_SCROLLS)
                
                # Pequeno scroll para cima (comportamento humano)
                await self.page.evaluate('''
                    () => {
                        const panel = document.querySelector('div[role="feed"]');
                        if (panel) {
                            panel.scrollTop -= 200;
                        }
                    }
                ''')
                
                await asyncio.sleep(0.5)
            
            print(f"   📜 {config.SCROLL_ATTEMPTS} scrolls realizados")
        
        except Exception as e:
            print(f"   ⚠️  Erro ao fazer scroll: {e}")
    
    async def _extract_professionals(self, city: str, state: str) -> List[Dict]:
        """Extrai dados dos resultados do Google Maps"""
        professionals = []
        
        try:
            await asyncio.sleep(3)
            
            # Buscar todos os itens de resultado
            items = await self.page.query_selector_all(config.SELECTORS['result_items'])
            
            if not items:
                print("   ⚠️  Nenhum resultado encontrado")
                return []
            
            print(f"   📋 {len(items)} resultados encontrados, extraindo até {config.MAX_PROFESSIONALS_PER_CITY}...")
            
            # Limitar ao máximo configurado
            items_to_process = items[:config.MAX_PROFESSIONALS_PER_CITY]
            
            for idx, item in enumerate(items_to_process, 1):
                try:
                    # Clicar no item para expandir detalhes
                    await item.click()
                    await asyncio.sleep(config.DELAY_AFTER_CLICK)
                    
                    # Extrair dados
                    prof_data = await self._extract_business_data(city, state)
                    
                    if prof_data and self._validate_professional(prof_data):
                        professionals.append(prof_data)
                        print(f"      ✓ {idx}. {prof_data['nome']} - {prof_data['telefone']}")
                    else:
                        print(f"      ✗ {idx}. Dados incompletos (sem telefone)")
                    
                    await asyncio.sleep(config.DELAY_BETWEEN_EXTRACTIONS)
                
                except Exception as e:
                    print(f"      ✗ {idx}. Erro: {e}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Erro geral na extração: {e}")
        
        return professionals
    
    async def _extract_business_data(self, city: str, state: str) -> Optional[Dict]:
        """Extrai dados de um negócio do Google Maps"""
        try:
            # Aguardar detalhes carregarem
            await asyncio.sleep(2)
            
            # Nome
            nome = await self._extract_text(config.SELECTORS['business_name'])
            
            # Telefone
            telefone = await self._extract_phone()
            
            # Categoria
            categoria = await self._extract_text(config.SELECTORS['category']) or "Guincho"
            
            # Avaliação
            avaliacao_nota = await self._extract_rating()
            
            # Total de avaliações
            avaliacao_total = await self._extract_review_count()
            
            # URL do perfil
            url_perfil = self.page.url
            
            return {
                "nome": nome or "Nome não disponível",
                "telefone": telefone or "",
                "cidade": city,
                "estado": state,
                "categoria": categoria,
                "avaliacao_nota": avaliacao_nota,
                "avaliacao_total": avaliacao_total,
                "servicos_negociados": 0,  # Google Maps não fornece
                "tempo_getninjas": "N/A",  # Não aplicável
                "url_perfil": url_perfil,
                "data_coleta": datetime.now().strftime(config.DATE_FORMAT)
            }
        
        except Exception as e:
            print(f"        Erro na extração: {e}")
            return None
    
    async def _extract_text(self, selector: str) -> Optional[str]:
        """Extrai texto de um seletor"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=3000, state='visible')
            if element:
                text = await element.inner_text()
                return text.strip() if text else None
        except:
            pass
        return None
    
    async def _extract_phone(self) -> Optional[str]:
        """Extrai telefone da página de detalhes"""
        try:
            # Buscar por botão de telefone ou texto com telefone
            phone_patterns = [
                'button[data-tooltip*="Copiar"]',
                'button[data-item-id*="phone"]',
                'a[href^="tel:"]',
            ]
            
            for pattern in phone_patterns:
                try:
                    element = await self.page.wait_for_selector(pattern, timeout=2000)
                    if element:
                        # Tentar pegar do atributo ou texto
                        aria_label = await element.get_attribute('aria-label')
                        data_tooltip = await element.get_attribute('data-tooltip')
                        href = await element.get_attribute('href')
                        text = await element.inner_text()
                        
                        for content in [aria_label, data_tooltip, href, text]:
                            if content:
                                phone = re.sub(r'\D', '', content)
                                if len(phone) >= 10:
                                    return phone
                except:
                    continue
            
            # Buscar telefone no conteúdo da página
            content = await self.page.content()
            phone_match = re.search(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', content)
            if phone_match:
                phone = re.sub(r'\D', '', phone_match.group())
                if len(phone) >= 10:
                    return phone
        
        except:
            pass
        
        return None
    
    async def _extract_rating(self) -> Optional[float]:
        """Extrai nota de avaliação"""
        try:
            rating_text = await self._extract_text(config.SELECTORS['rating'])
            if rating_text:
                match = re.search(r'([\d,\.]+)', rating_text)
                if match:
                    rating = float(match.group(1).replace(',', '.'))
                    return rating if 0 <= rating <= 5 else None
        except:
            pass
        return None
    
    async def _extract_review_count(self) -> int:
        """Extrai total de avaliações"""
        try:
            review_text = await self._extract_text(config.SELECTORS['review_count'])
            if review_text:
                match = re.search(r'([\d\.]+)', review_text)
                if match:
                    return int(match.group(1).replace('.', ''))
        except:
            pass
        return 0
    
    def _validate_professional(self, data: Dict) -> bool:
        """Valida se tem campos obrigatórios (nome + telefone)"""
        for field in config.REQUIRED_FIELDS:
            if not data.get(field) or data.get(field) == "":
                return False
        return True


async def scrape_city_wrapper(proxy_manager: ProxyManager, city: str, state: str) -> List[Dict]:
    """Wrapper para scraping de uma cidade"""
    scraper = GoogleMapsScraper(proxy_manager)
    
    try:
        await scraper.init_browser()
        professionals = await scraper.scrape_city(city, state)
        return professionals
    finally:
        await scraper.cleanup()
