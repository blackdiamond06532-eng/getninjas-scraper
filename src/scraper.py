"""
Scraper Google Search para profissionais de guincho
"""
import asyncio
import random
import re
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
import config
from proxy_manager import ProxyManager


class GoogleSearchScraper:
    """Scraper para Google Search usando Playwright"""
    
    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    async def init_browser(self):
        """Inicializa navegador com proxy"""
        proxy_config = None  # DESABILITADO TEMPORARIAMENTE PARA TESTE
        
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
        """Scrape profissionais de guincho em uma cidade via Google Search"""
        city_name = city.replace("-", " ").title()
        search_query = f"guincho {city_name} {state.upper()} telefone"
        
        print(f"\n🏙️  Processando: {city_name}/{state.upper()}")
        print(f"   🔍 Busca: \"{search_query}\"")
        
        professionals = []
        
        try:
            # 1. Construir URL do Google Search
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&num=50&hl=pt-BR&gl=BR"
            
            # 2. Navegar
            await self.page.goto(search_url, wait_until='domcontentloaded', timeout=config.TIMEOUT_NAVIGATION)
            await asyncio.sleep(random.uniform(3, 5))
            
            # 3. Extrair resultados
            professionals = await self._extract_results(city_name, state.upper())
            
            print(f"   ✅ {len(professionals)} profissionais encontrados")
        
        except Exception as e:
            print(f"   ❌ Erro ao processar {city_name}: {e}")
        
        return professionals
    
    async def _extract_results(self, city: str, state: str) -> List[Dict]:
        """Extrai dados dos resultados do Google Search"""
        professionals = []
        
        try:
            await asyncio.sleep(2)
            
            # DEBUG: Verificar o que o Google retornou
            html_content = await self.page.content()
            
            # Verificar bloqueios
            if "detectado tráfego incomum" in html_content or "unusual traffic" in html_content:
                print(f"   🚫 CAPTCHA/Bloqueio detectado!")
                return []
            
            if "Before you continue" in html_content or "Antes de continuar" in html_content:
                print(f"   🍪 Página de consentimento detectada, tentando aceitar...")
                try:
                    # Tentar clicar em "Aceitar tudo" ou "Accept all"
                    accept_buttons = await self.page.query_selector_all('button')
                    for btn in accept_buttons:
                        text = await btn.inner_text()
                        if any(word in text.lower() for word in ['aceitar', 'accept', 'concordo', 'agree']):
                            await btn.click()
                            await asyncio.sleep(2)
                            break
                except:
                    pass
            
            # Seletores para resultados orgânicos do Google (atualizados 2026)
            result_selectors = [
                'div.g',                    # Seletor clássico
                'div[data-sokoban-container]',
                'div.Gx5Zad',
                'div[jscontroller]',
                'div.kvH3mc',               # Novo formato
                'div.MjjYud',               # Outro formato
            ]
            
            results = []
            for selector in result_selectors:
                results = await self.page.query_selector_all(selector)
                if len(results) > 0:
                    print(f"   📋 Usando seletor: '{selector}' - {len(results)} elementos")
                    break
            
            if not results:
                # DEBUG: Listar alguns elementos da página
                print(f"   ⚠️  Nenhum resultado com seletores conhecidos")
                print(f"   📄 Tamanho do HTML: {len(html_content)} chars")
                
                # Tentar encontrar qualquer div que pareça um resultado
                all_divs = await self.page.query_selector_all('div')
                print(f"   🔍 Total de divs na página: {len(all_divs)}")
                return []
            
            print(f"   📋 {len(results)} resultados encontrados, extraindo até {config.MAX_PROFESSIONALS_PER_CITY}...")
            
            # Limitar resultados
            results_to_process = results[:config.MAX_PROFESSIONALS_PER_CITY * 2]
            
            for idx, result in enumerate(results_to_process, 1):
                try:
                    # Extrair dados do resultado
                    prof_data = await self._extract_result_data(result, city, state)
                    
                    if prof_data and self._validate_professional(prof_data):
                        professionals.append(prof_data)
                        print(f"      ✓ {len(professionals)}. {prof_data['nome']} - {prof_data['telefone']}")
                        
                        if len(professionals) >= config.MAX_PROFESSIONALS_PER_CITY:
                            break
                    
                    await asyncio.sleep(config.DELAY_BETWEEN_EXTRACTIONS)
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"   ❌ Erro na extração: {e}")
        
        return professionals
    
    async def _extract_result_data(self, result_element, city: str, state: str) -> Optional[Dict]:
        """Extrai dados de um resultado do Google Search"""
        try:
            # Pegar TODO o texto do elemento
            full_text = await result_element.inner_text()
            
            # Extrair título
            title_selectors = ['h3', 'div[role="heading"]', 'span[role="heading"]', 'div.BNeawe']
            nome = None
            for selector in title_selectors:
                title_el = await result_element.query_selector(selector)
                if title_el:
                    nome = await title_el.inner_text()
                    break
            
            if not nome:
                # Usar primeira linha do texto como nome
                lines = full_text.split('\n')
                nome = lines[0] if lines else None
            
            if not nome:
                return None
            
            # Buscar telefone no texto completo
            telefone = self._extract_phone_from_text(full_text)
            
            if not telefone:
                return None
            
            # Extrair URL
            url = ""
            link_el = await result_element.query_selector('a')
            if link_el:
                url = await link_el.get_attribute('href') or ""
            
            # Categoria
            categoria = "Guincho"
            text_lower = full_text.lower()
            if "reboque" in text_lower:
                categoria = "Guincho e Reboque"
            elif "24" in full_text or "24h" in text_lower:
                categoria = "Guincho 24h"
            
            return {
                "nome": nome.strip()[:100],  # Limitar tamanho
                "telefone": telefone,
                "cidade": city,
                "estado": state,
                "categoria": categoria,
                "avaliacao_nota": None,
                "avaliacao_total": 0,
                "servicos_negociados": 0,
                "tempo_getninjas": "N/A",
                "url_perfil": url,
                "data_coleta": datetime.now().strftime(config.DATE_FORMAT)
            }
        
        except Exception as e:
            return None
    
    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extrai telefone de um texto"""
        if not text:
            return None
        
        # Padrões de telefone brasileiros
        patterns = [
            r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}',
            r'\d{2}\s?\d{4,5}[-\s]?\d{4}',
            r'\d{10,11}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                phone = re.sub(r'\D', '', match)
                if len(phone) >= 10 and len(phone) <= 11:
                    if phone[:2].isdigit() and 11 <= int(phone[:2]) <= 99:
                        return phone
        
        return None
    
    def _validate_professional(self, data: Dict) -> bool:
        """Valida se tem campos obrigatórios"""
        for field in config.REQUIRED_FIELDS:
            if not data.get(field) or data.get(field) == "":
                return False
        return True


async def scrape_city_wrapper(proxy_manager: ProxyManager, city: str, state: str) -> List[Dict]:
    """Wrapper para scraping de uma cidade"""
    scraper = GoogleSearchScraper(proxy_manager)
    
    try:
        await scraper.init_browser()
        professionals = await scraper.scrape_city(city, state)
        return professionals
    finally:
        await scraper.cleanup()
