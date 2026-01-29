#!/usr/bin/env python3
"""
Arquivo de configuração do scraper GetNinjas
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env (local) ou secrets (GitHub Actions)
load_dotenv()

# Configurações de scraping
MAX_PROFESSIONALS_PER_CITY = 5
SCROLL_ATTEMPTS = 3
DELAY_BETWEEN_CITIES = (10, 30)  # segundos (min, max)
DELAY_BETWEEN_EXTRACTIONS = (0.5, 1.5)  # segundos
PAGE_TIMEOUT = 30000  # milissegundos (30s)

# User Agent realista
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)

# Campos obrigatórios
REQUIRED_FIELDS = ['nome', 'telefone']

# Formato de data
DATE_FORMAT = '%Y-%m-%d'

# Configuração de output
OUTPUT_DIR = 'output/results'
OUTPUT_FILENAME_TEMPLATE = 'guincho_{date}.json'

# Número de proxies configurados
MAX_PROXIES = 11  # Atualizado para 11 proxies
