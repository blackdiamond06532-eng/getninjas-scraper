#!/usr/bin/env python3
"""
Módulo de scraping para GetNinjas
Coleta dados de profissionais de guincho
"""
import asyncio
import random
import re
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser, Playwright
from playwright_stealth import stealth_async
import config
from cities import build_city_url


class GetNinjasScraper:
    """Scraper para coletar dados de profissionais do GetNinjas"""
    
    def __init__(self, proxy: Optional[str] = None):
        """
        Inicializa o scraper
        
        Args:
            proxy: URL do proxy no formato http://user:pass@ip:port
        """
        self.proxy = proxy
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def setup(self):
        """Inicializa o navegador Playwright"""
        print("   🌐 Iniciando navegador...")
        
        # Configurações do navegador
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
        ]
        
        # Configurar proxy se fornecido
        proxy_config = None
        if self.proxy:
            # Extrair credenciais do proxy
            proxy_parts = self.proxy.replace('http://', '').split('@')
            if len(proxy_parts) == 2:
                auth, server = proxy_parts
                username, password = auth.split(':')
                proxy_config = {
                    'server': f'http://{server}',
                    'username': username,
                    'password': password
                }
            else:
                proxy_config = {'server': self.proxy}
        
        # Iniciar Playwright
        self.playwright = await async_playwright().start()
        
        # Lançar navegador
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=browser_args,
            proxy=proxy_config
        )
        
        # Criar contexto e página
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=config.USER_AGENT
        )
        
        self.page = await context.new_page()
        
        # Aplicar stealth mode
        try:
            await stealth_async(self.page)
        except Exception as e:
            print(f"   ⚠️  Stealth mode falhou: {e}")
        
        print("   ✓ Navegador iniciado")
    
    async def cleanup(self):
        """Fecha recursos do Playwright"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"   ⚠️  Erro ao fechar navegador: {e}")
    
    async def scrape_city(self, city: str, state: str) -> List[Dict]:
        """
        Scrape profissionais de uma cidade específica
        
        Args:
            city: Nome da cidade
            state: Sigla do estado
        
        Returns:
            Lista de dicionários com dados dos profissionais
        """
        print(f"   🔍 Acessando: {city}/{state}")
        
        # Construir URL
        url = build_city_url(city, state)
        
        try:
            # Acessar página
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"   ✓ Página carregada")
            
            # Aguardar carregamento
            await asyncio.sleep(random.uniform(2, 4))
            
            # Scroll para carregar lazy loading
            await self._scroll_page()
            
            # Extrair profissionais
            professionals = await self._extract_professionals(city, state)
            
            print(f"   ✓ {len(professionals)} profissionais encontrados")
            return professionals
        
        except Exception as e:
            print(f"   ❌ Erro ao acessar {city}: {e}")
            return []
    
    async def _scroll_page(self):
        """Faz scroll na página para carregar conteúdo lazy"""
        try:
            for _ in range(3):
                await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Erro no scroll: {e}")
    
    async def _extract_professionals(self, city: str, state: str) -> List[Dict]:
        """
        Extrai dados de profissionais da página
        
        Args:
            city: Nome da cidade
            state: Sigla do estado
        
        Returns:
            Lista de dicionários com dados dos profissionais
        """
        professionals = []
        
        try:
            # Seletores possíveis para cards de profissionais
            selectors = [
                'div[data-testid*="professional"]',
                'div[class*="professional-card"]',
                'div[class*="ProfessionalCard"]',
                'article[class*="professional"]',
                'div[class*="ninja-card"]',
            ]
            
            # Tentar cada seletor
            professional_cards = []
            for selector in selectors:
                cards = await self.page.query_selector_all(selector)
                if cards:
                    professional_cards = cards
                    print(f"   📋 Usando seletor: {selector}")
                    break
            
            if not professional_cards:
                # Fallback: buscar por estrutura genérica
                print("   ⚠️  Seletores específicos não encontrados, tentando fallback...")
                professional_cards = await self.page.query_selector_all('div[class*="card"]')
            
            # Limitar ao máximo configurado
            cards_to_process = professional_cards[:config.MAX_PROFESSIONALS_PER_CITY]
            
            for idx, card in enumerate(cards_to_process, 1):
                try:
                    professional_data = await self._extract_professional_data(card, city, state)
                    
                    # Validar campos obrigatórios
                    if professional_data and self._validate_professional(professional_data):
                        professionals.append(professional_data)
                        print(f"      ✓ Profissional {idx}: {professional_data['nome']}")
                    
                    # Delay entre extrações
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                
                except Exception as e:
                    print(f"      ✗ Erro ao extrair profissional {idx}: {e}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Erro ao extrair profissionais: {e}")
        
        return professionals
    
    async def _extract_professional_data(self, card_element, city: str, state: str) -> Optional[Dict]:
        """
        Extrai dados de um card de profissional
        
        Args:
            card_element: Elemento HTML do card
            city: Nome da cidade
            state: Sigla do estado
        
        Returns:
            Dicionário com dados do profissional ou None
        """
        try:
            # Extrair texto do card
            card_text = await card_element.inner_text()
            
            # Nome
            nome = await self._extract_field(card_element, [
                'h2', 'h3', '[class*="name"]', '[class*="title"]', 'strong'
            ])
            
            # Telefone
            telefone = self._extract_phone_from_text(card_text)
            
            # Categoria/Serviço
            categoria = await self._extract_field(card_element, [
                '[class*="category"]', '[class*="service"]', 'span'
            ]) or "Guincho"
            
            # Avaliação
            avaliacao_nota = self._extract_rating_from_text(card_text)
            
            # Total de avaliações
            avaliacao_total = self._extract_number_from_text(card_text, ['avaliações', 'avaliacao'])
            
            # Serviços negociados
            servicos_negociados = self._extract_number_from_text(card_text, ['serviços', 'negociados', 'jobs'])
            
            # Tempo no GetNinjas
            tempo_getninjas = self._extract_time_from_text(card_text)
            
            # URL do perfil
            url_perfil = await self._extract_profile_url(card_element)
            
            # Data de coleta
            data_coleta = datetime.now().strftime(config.DATE_FORMAT)
            
            return {
                "nome": nome or "Nome não disponível",
                "telefone": telefone or "",
                "cidade": city,
                "estado": state,
                "categoria": categoria,
                "avaliacao_nota": avaliacao_nota,
                "avaliacao_total": avaliacao_total,
                "servicos_negociados": servicos_negociados,
                "tempo_getninjas": tempo_getninjas,
                "url_perfil": url_perfil or "",
                "data_coleta": data_coleta
            }
        
        except Exception as e:
            print(f"        Erro detalhado na extração: {e}")
            return None
    
    async def _extract_field(self, element, selectors: List[str]) -> Optional[str]:
        """Tenta extrair texto usando múltiplos seletores"""
        for selector in selectors:
            try:
                field = await element.query_selector(selector)
                if field:
                    text = await field.inner_text()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extrai número de telefone do texto usando regex"""
        patterns = [
            r'\(?\d{2}\)?\s*9?\d{4}[-\s]?\d{4}',
            r'\d{2}\s*9\d{8}',
            r'\d{10,11}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = re.sub(r'\D', '', match.group())
                if len(phone) >= 10:
                    return phone
        
        return None
    
    def _extract_rating_from_text(self, text: str) -> Optional[float]:
        """Extrai nota de avaliação do texto"""
        match = re.search(r'(\d+[.,]\d+)\s*(?:estrelas?|stars?)?', text, re.IGNORECASE)
        if match:
            try:
                rating = float(match.group(1).replace(',', '.'))
                if 0 <= rating <= 5:
                    return rating
            except:
                pass
        return None
    
    def _extract_number_from_text(self, text: str, keywords: List[str]) -> int:
        """Extrai número associado a keywords do texto"""
        for keyword in keywords:
            pattern = f'(\d+)\s*{keyword}'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return 0
    
    def _extract_time_from_text(self, text: str) -> str:
        """Extrai informação de tempo no GetNinjas"""
        patterns = [
            r'Desde\s+\w+/\d{4}',
            r'\d+\s+(?:anos?|meses?|dias?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Não informado"
    
    async def _extract_profile_url(self, card_element) -> Optional[str]:
        """Extrai URL do perfil do profissional"""
        try:
            # Procurar por links no card
            link = await card_element.query_selector('a[href*="anuncios"], a[href*="profissional"]')
            if link:
                href = await link.get_attribute('href')
                if href:
                    # Garantir URL completa
                    if href.startswith('http'):
                        return href
                    else:
                        return f"https://www.getninjas.com.br{href}"
        except:
            pass
        
        return None
    
    def _validate_professional(self, professional: Dict) -> bool:
        """
        Valida se profissional tem campos obrigatórios
        
        Args:
            professional: Dicionário com dados do profissional
        
        Returns:
            True se válido, False caso contrário
        """
        for field in config.REQUIRED_FIELDS:
            value = professional.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                return False
        return True


# Função wrapper para usar em main.py
async def scrape_city_wrapper(proxy_manager, city: str, state: str) -> List[Dict]:
    """
    Wrapper para scraping de cidade com gerenciamento de recursos
    
    Args:
        proxy_manager: Instância do ProxyManager
        city: Nome da cidade
        state: Sigla do estado
    
    Returns:
        Lista de profissionais coletados
    """
    proxy = proxy_manager.get_next_proxy()
    scraper = GetNinjasScraper(proxy=proxy)
    
    try:
        await scraper.setup()
        professionals = await scraper.scrape_city(city, state)
        return professionals
    
    except Exception as e:
        print(f"   ❌ Erro fatal no scraping de {city}: {e}")
        return []
    
    finally:
        await scraper.cleanup()
