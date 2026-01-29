"""
Scraper principal para extração de dados de profissionais de guincho do GetNinjas
"""
import asyncio
import random
import re
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import stealth_async
import config
from proxy_manager import ProxyManager


class GetNinjasScraper:
    """Scraper para GetNinjas usando Playwright com stealth mode"""
    
    def __init__(self, proxy_manager: ProxyManager):
        """
        Inicializa o scraper
        
        Args:
            proxy_manager: Instância do ProxyManager para rotação de proxies
        """
        self.proxy_manager = proxy_manager
        self.professionals = []
        self.browser = None
        self.context = None
        self.page = None
    
    async def init_browser(self):
        """Inicializa navegador Playwright com configurações stealth"""
        proxy_config = self.proxy_manager.get_proxy_config()
        
        playwright = await async_playwright().start()
        
        # Argumentos do navegador para evitar detecção
        browser_args = config.BROWSER_ARGS.copy()
        
        # Iniciar navegador
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=browser_args,
            proxy=proxy_config
        )
        
        # Criar contexto com configurações realistas
        self.context = await self.browser.new_context(
            viewport=config.VIEWPORT,
            user_agent=config.USER_AGENT,
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
        )
        
        # Criar página
        self.page = await self.context.new_page()
        
        # Aplicar stealth mode
        await stealth_async(self.page)
        
        print(f"  🌐 Navegador iniciado {'com proxy' if proxy_config else 'sem proxy'}")
    
    async def close_browser(self):
        """Fecha navegador e libera recursos"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def scrape_city(self, city: str, state: str) -> List[Dict]:
        """
        Scrape profissionais de uma cidade específica
        
        Args:
            city: Nome da cidade (formato URL)
            state: Sigla do estado
        
        Returns:
            Lista de dicionários com dados dos profissionais
        """
        from cities import build_city_url
        
        url = build_city_url(city, state)
        city_name = city.replace("-", " ").title()
        
        print(f"\n🏙️  Processando: {city_name}/{state.upper()}")
        print(f"   URL: {url}")
        
        professionals = []
        
        try:
            # Navegar para página da cidade
            await self.page.goto(url, wait_until='networkidle', timeout=config.TIMEOUT_NAVIGATION)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Scroll para carregar profissionais (lazy loading)
            await self._scroll_page()
            
            # Extrair cards de profissionais
            professionals = await self._extract_professionals(city_name, state.upper())
            
            print(f"   ✅ {len(professionals)} profissionais encontrados")
        
        except Exception as e:
            print(f"   ❌ Erro ao processar {city_name}: {e}")
        
        return professionals
    
    async def _scroll_page(self):
        """Realiza scrolls progressivos para carregar conteúdo lazy loading"""
        for i in range(config.SCROLL_ATTEMPTS):
            # Scroll suave até o final da página
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(config.DELAY_BETWEEN_SCROLLS)
            
            # Scroll de volta um pouco (comportamento humano)
            await self.page.evaluate("window.scrollBy(0, -200)")
            await asyncio.sleep(0.5)
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
            # O GetNinjas pode ter diferentes estruturas HTML
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
            
            # Nome - geralmente está em h2, h3 ou tag com classe específica
            nome = await self._extract_field(card_element, [
                'h2', 'h3', '[class*="name"]', '[class*="title"]', 'strong'
            ])
            
            # Telefone - buscar padrões de telefone no texto
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
        # Padrões de telefone brasileiro
        patterns = [
            r'\(?\d{2}\)?\s*9?\d{4}[-\s]?\d{4}',  # (11) 99999-9999
            r'\d{2}\s*9\d{8}',  # 11999999999
            r'\d{10,11}',  # 1199999999 ou 11999999999
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # Remover caracteres não numéricos
                phone = re.sub(r'\D', '', match.group())
                if len(phone) >= 10:
                    return phone
        
        return None
    
    def _extract_rating_from_text(self, text: str) -> Optional[float]:
        """Extrai nota de avaliação do texto"""
        # Procurar por padrões como "4.5", "4,5", "5.0"
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
        # Padrões como "Desde dez/2024", "2 anos", etc
        patterns = [
            r'Desde\s+\w+/\d{4}',
            r'\d+\s+(?:anos?|meses?|dias?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return "Não informado"
    
    async def _extract_profile_url(self, element) -> Optional[str]:
        """Extrai URL do perfil do profissional"""
        try:
            # Procurar por link dentro do card
            link = await element.query_selector('a[href*="/anuncios/"]')
            if not link:
                link = await element.query_selector('a[href*="/profissionais/"]')
            
            if link:
                href = await link.get_attribute('href')
                if href:
                    # Se for URL relativa, completar
                    if href.startswith('/'):
                        return f"https://www.getninjas.com.br{href}"
                    return href
        except:
            pass
        
        return None
    
    def _validate_professional(self, data: Dict) -> bool:
        """
        Valida se profissional tem campos obrigatórios
        
        Args:
            data: Dicionário com dados do profissional
        
        Returns:
            True se válido, False caso contrário
        """
        for field in config.REQUIRED_FIELDS:
            if not data.get(field) or data.get(field) == "":
                return False
        return True


async def scrape_city_wrapper(proxy_manager: ProxyManager, city: str, state: str) -> List[Dict]:
    """
    Wrapper para scraping de uma cidade com gerenciamento de browser
    
    Args:
        proxy_manager: Instância do ProxyManager
        city: Nome da cidade
        state: Sigla do estado
    
    Returns:
        Lista de profissionais extraídos
    """
    scraper = GetNinjasScraper(proxy_manager)
    
    try:
        await scraper.init_browser()
        professionals = await scraper.scrape_city(city, state)
        return professionals
    
    finally:
        await scraper.close_browser()
