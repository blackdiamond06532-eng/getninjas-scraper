"""
Configurações centralizadas do scraper Google Maps para guinchos
"""

# URLs Base
# URLs Base
BASE_URL_GOOGLE = "https://www.google.com/search"  # MUDANÇA: Search ao invés de Maps

# Limites de scraping
MAX_PROFESSIONALS_PER_CITY = 20  # 20 por cidade
MAX_CITIES_PER_DAY = 5  # 5 cidades por dia = 100 profissionais/dia
SCROLL_ATTEMPTS = 15  # Mais scrolls para carregar 20 profissionais

# Delays (em segundos) - MAIS LENTOS para evitar bloqueio
DELAY_MIN = 30  # 30 segundos mínimo entre cidades
DELAY_MAX = 60  # 60 segundos máximo entre cidades
DELAY_BETWEEN_SCROLLS = 3  # 3 segundos entre scrolls
DELAY_AFTER_CLICK = 2  # 2 segundos após clicar
DELAY_BETWEEN_EXTRACTIONS = 1.5  # Delay entre extrair cada profissional

# Timeouts (em milissegundos)
TIMEOUT_NAVIGATION = 90000  # 90 segundos
TIMEOUT_ELEMENT = 15000     # 15 segundos

# Termo de busca
SEARCH_QUERY_TEMPLATE = "guincho {city} {state}"  # Ex: "guincho Campinas SP"

# User Agent realista
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Configurações do navegador
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process',
]

# Viewport padrão
VIEWPORT = {
    'width': 1920,
    'height': 1080
}

# Campos obrigatórios
REQUIRED_FIELDS = ['nome', 'telefone']

# Formato de data
DATE_FORMAT = "%Y-%m-%d"

# Seletores Google Maps (podem mudar)
SELECTORS = {
    'search_box': 'input#searchboxinput',
    'search_button': 'button#searchbox-searchbutton',
    'results_panel': 'div[role="feed"]',
    'result_items': 'div.Nv2PK',
    'business_name': 'div.qBF1Pd',
    'rating': 'span.MW4etd',
    'review_count': 'span.UY7F9',
    'category': 'button[jsaction*="category"]',
    'phone': 'button[data-tooltip*="Copiar número"]',
    'website': 'a[data-tooltip="Abrir website"]',
    'address': 'button[data-item-id="address"]',
}
