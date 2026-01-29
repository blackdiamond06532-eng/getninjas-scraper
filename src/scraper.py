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
        
        self.context = await self.browser.new_context(
            viewport=config.VIEWPORT,
            user_agent=config.USER_AGENT,
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
            proxy=proxy_config
        )
        
        self.page = await self.context.new_page()
        
        # Stealth mode (ignorar se falhar)
        try:
            from playwright_stealth import stealth_async
            await stealth_async(self.page)
        except Exception as e:
            print(f"   ⚠️  Stealth mode falhou: {e}")
        
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
            await self.page.goto(config.BASE_URL_GOOGLE_MAPS, wait_until='networkidle', timeout=config.TIMEOUT_NAVIGATION)
            await asyncio.sleep(random.uniform(3, 5))
            
            # 2. Fazer busca
            search_box = await self.page.wait_for_selector(config.SELECTORS['search_box'], timeout=config.TIMEOUT_ELEMENT)
            await search_box.fill(search_query)
            await search_box.press("Enter")
            await asyncio.sleep(random.uniform(5, 7))
            
            # 3. Scroll para carregar resultados
            await self._scroll_results_feed()
            
            # 4. Extrair profissionais
            professionals = await self._extract_professionals(city_name, state.upper())
            
            print(f"   ✅ {len(professionals)} profissionais encontrados")
        
        except Exception as e:
            print(f"   ❌ Erro ao processar {city_name}: {e}")
        
        return professionals
    
    async def _scroll_results_feed(self):
        """Scroll no painel de resultados para carregar mais empresas"""
        try:
            feed = await self.page.wait_for_selector(config.SELECTORS['results_feed'], timeout=config.TIMEOUT_ELEMENT)
            
            for i in range(config.SCROLL_ATTEMPTS):
                await self.page.evaluate('(el) => el.scrollTop = el.scrollHeight', feed)
                await asyncio.sleep(config.DELAY_BETWEEN_SCROLLS)
                
                # Scroll de volta um pouco (comportamento humano)
                await self.page.evaluate('(el) => el.scrollTop -= 200', feed)
                await asyncio.sleep(0.5)
            
            print(f"   📜 {config.SCROLL_ATTEMPTS} scrolls realizados")
        
        except Exception as e:
            print(f"   ⚠️  Erro ao fazer scroll: {e}")
    async def _extract_professionals(self, city: str, state: str) -> List[Dict]:
        """Extrai dados dos cards de resultados do Google Maps"""
        professionals = []
        
        try:
            # Aguardar cards carregarem
            await asyncio.sleep(3)
            
            # Buscar todos os cards
            cards = await self.page.query_selector_all(config.SELECTORS['result_cards'])
            
            if not cards:
                print("   ⚠️  Nenhum card encontrado")
                return []
            
            print(f"   📋 {len(cards)} cards encontrados, extraindo até {config.MAX_PROFESSIONALS_PER_CITY}...")
            
            # Limitar ao máximo configurado
            cards_to_process = cards[:config.MAX_PROFESSIONALS_PER_CITY]
            
            for idx, card in enumerate(cards_to_process, 1):
                try:
                    # Clicar no card para expandir detalhes
                    await card.click()
                    await asyncio.sleep(config.DELAY_AFTER_CLICK)
                    
                    # Extrair dados
                    prof_data = await self._extract_business_data(card, city, state)
                    
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
    
    async def _extract_business_data(self, card_element, city: str, state: str) -> Optional[Dict]:
        """Extrai dados de um negócio do Google Maps"""
        try:
            # Nome
            nome = await self._safe_extract_text(card_element, config.SELECTORS['business_name'])
            
            # Telefone - clicar no botão de telefone se existir
            telefone = await self._extract_phone()
            
            # Categoria
            categoria = await self._safe_extract_text(card_element, config.SELECTORS['category']) or "Guincho"
            
            # Avaliação
            avaliacao_nota = await self._extract_rating(card_element)
            
            # Total de avaliações
            avaliacao_total = await self._extract_review_count(card_element)
            
            # URL do perfil (URL atual da página)
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
    
    async def _safe_extract_text(self, element, selector: str) -> Optional[str]:
        """Extrai texto de um elemento com tratamento de erro"""
        try:
            el = await element.query_selector(selector)
            if el:
                text = await el.inner_text()
                return text.strip() if text else None
        except:
            pass
        return None
    
    async def _extract_phone(self) -> Optional[str]:
        """Extrai telefone clicando no botão de telefone"""
        try:
            # Procurar botão de telefone
            phone_button = await self.page.query_selector(config.SELECTORS['phone_button'])
            
            if phone_button:
                # Obter aria-label que geralmente contém o telefone
                aria_label = await phone_button.get_attribute('aria-label')
                
                if aria_label:
                    # Extrair números
                    phone = re.sub(r'\D', '', aria_label)
                    if len(phone) >= 10:
                        return phone
        except:
            pass
        
        return None
    
    async def _extract_rating(self, card_element) -> Optional[float]:
        """Extrai nota de avaliação"""
        try:
            rating_el = await card_element.query_selector(config.SELECTORS['rating_stars'])
            if rating_el:
                aria_label = await rating_el.get_attribute('aria-label')
                if aria_label:
                    match = re.search(r'([\d,\.]+)', aria_label)
                    if match:
                        rating = float(match.group(1).replace(',', '.'))
                        return rating if 0 <= rating <= 5 else None
        except:
            pass
        return None
    
    async def _extract_review_count(self, card_element) -> int:
        """Extrai total de avaliações"""
        try:
            review_el = await card_element.query_selector(config.SELECTORS['review_count'])
            if review_el:
                text = await review_el.inner_text()
                match = re.search(r'([\d\.]+)', text)
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
