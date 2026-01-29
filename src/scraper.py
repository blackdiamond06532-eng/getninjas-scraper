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
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}&num=50"
            
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
            
            # Seletores para resultados orgânicos do Google
            result_selectors = [
                'div.g',  # Resultado padrão
                'div[data-sokoban-container]',  # Resultado alternativo
            ]
            
            results = []
            for selector in result_selectors:
                results = await self.page.query_selector_all(selector)
                if results:
                    break
            
            if not results:
                print("   ⚠️  Nenhum resultado encontrado")
                return []
            
            print(f"   📋 {len(results)} resultados encontrados, extraindo até {config.MAX_PROFESSIONALS_PER_CITY}...")
            
            # Limitar resultados
            results_to_process = results[:config.MAX_PROFESSIONALS_PER_CITY * 2]  # Pegar mais porque alguns não terão telefone
            
            for idx, result in enumerate(results_to_process, 1):
                try:
                    # Extrair dados do resultado
                    prof_data = await self._extract_result_data(result, city, state)
                    
                    if prof_data and self._validate_professional(prof_data):
                        professionals.append(prof_data)
                        print(f"      ✓ {len(professionals)}. {prof_data['nome']} - {prof_data['telefone']}")
                        
                        # Parar quando atingir o máximo
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
            # Extrair título
            title_selectors = ['h3', 'div[role="heading"]']
            nome = None
            for selector in title_selectors:
                title_el = await result_element.query_selector(selector)
                if title_el:
                    nome = await title_el.inner_text()
                    break
            
            if not nome:
                return None
            
            # Extrair snippet/descrição
            snippet_selectors = [
                'div.VwiC3b',
                'div[data-content-feature]',
                'span.aCOpRe',
            ]
            
            snippet_text = ""
            for selector in snippet_selectors:
                snippet_el = await result_element.query_selector(selector)
                if snippet_el:
                    snippet_text = await snippet_el.inner_text()
                    break
            
            # Extrair URL
            url = ""
            link_el = await result_element.query_selector('a')
            if link_el:
                url = await link_el.get_attribute('href') or ""
            
            # Buscar telefone no snippet ou título
            telefone = self._extract_phone_from_text(f"{nome} {snippet_text}")
            
            if not telefone:
                return None
            
            # Tentar extrair categoria
            categoria = "Guincho"
            if "reboque" in snippet_text.lower():
                categoria = "Guincho e Reboque"
            elif "24" in snippet_text or "24h" in snippet_text.lower():
                categoria = "Guincho 24h"
            
            return {
                "nome": nome.strip(),
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
            r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}',  # (11) 99999-9999 ou 11 99999-9999
            r'\d{2}\s?\d{4,5}[-\s]?\d{4}',        # 11999999999
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Limpar e validar
                phone = re.sub(r'\D', '', match.group())
                if len(phone) >= 10:
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
