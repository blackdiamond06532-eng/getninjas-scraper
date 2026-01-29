"""
Configurações centralizadas do scraper GetNinjas
"""

# URLs Base
BASE_URL_GETNINJAS = "https://www.getninjas.com.br/automoveis/guincho"

# Limites de scraping
MAX_PROFESSIONALS_PER_CITY = 5
SCROLL_ATTEMPTS = 3
MAX_CITIES_PER_RUN = 20

# Delays (em segundos)
DELAY_MIN = 10
DELAY_MAX = 30
DELAY_BETWEEN_SCROLLS = 2
DELAY_AFTER_CLICK = 1

# Timeouts (em milissegundos)
TIMEOUT_NAVIGATION = 60000  # 60 segundos
TIMEOUT_ELEMENT = 10000     # 10 segundos

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
