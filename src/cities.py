#!/usr/bin/env python3
"""
Módulo de cidades para scraping do GetNinjas
Gerencia rotação semanal de 100 cidades brasileiras
"""
from datetime import date
from typing import List, Tuple

# Lista de 100 cidades brasileiras com maior demanda de guincho
CITIES = [
    # Grupo 1: SP Capital + Grande SP + Principais RJ/MG (20 cidades)
    ("São Paulo", "SP"),
    ("Guarulhos", "SP"),
    ("Osasco", "SP"),
    ("Santo André", "SP"),
    ("São Bernardo do Campo", "SP"),
    ("Mauá", "SP"),
    ("Diadema", "SP"),
    ("Carapicuíba", "SP"),
    ("Barueri", "SP"),
    ("Cotia", "SP"),
    ("Taboão da Serra", "SP"),
    ("Embu das Artes", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Niterói", "RJ"),
    ("São Gonçalo", "RJ"),
    ("Duque de Caxias", "RJ"),
    ("Belo Horizonte", "MG"),
    ("Contagem", "MG"
    ("Betim", "MG"),
    ("Ribeirão das Neves", "MG"),
    
    # Grupo 2: Interior SP + Sul (20 cidades)
    ("Campinas", "SP"),
    ("São José dos Campos", "SP"),
    ("Sorocaba", "SP"),
    ("Ribeirão Preto", "SP"),
    ("Santos", "SP"),
    ("São José do Rio Preto", "SP"),
    ("Mogi das Cruzes", "SP"),
    ("Jundiaí", "SP"),
    ("Piracicaba", "SP"),
    ("Bauru", "SP"),
    ("Curitiba", "PR"),
    ("Londrina", "PR"),
    ("Maringá", "PR"),
    ("Ponta Grossa", "PR"),
    ("Cascavel", "PR"),
    ("Porto Alegre", "RS"),
    ("Caxias do Sul", "RS"),
    ("Canoas", "RS"),
    ("Pelotas", "RS"),
    ("Florianópolis", "SC"),
    
    # Grupo 3: Nordeste (20 cidades)
    ("Salvador", "BA"),
    ("Feira de Santana", "BA"),
    ("Vitória da Conquista", "BA"),
    ("Camaçari", "BA"),
    ("Fortaleza", "CE"),
    ("Caucaia", "CE"),
    ("Juazeiro do Norte", "CE"),
    ("Recife", "PE"),
    ("Jaboatão dos Guararapes", "PE"),
    ("Olinda", "PE"),
    ("Caruaru", "PE"),
    ("Natal", "RN"),
    ("Mossoró", "RN"),
    ("São Luís", "MA"),
    ("Imperatriz", "MA"),
    ("Teresina", "PI"),
    ("Maceió", "AL"),
    ("Aracaju", "SE"),
    ("João Pessoa", "PB"),
    ("Campina Grande", "PB"),
    
    # Grupo 4: Norte + Centro-Oeste (20 cidades)
    ("Brasília", "DF"),
    ("Goiânia", "GO"),
    ("Aparecida de Goiânia", "GO"),
    ("Anápolis", "GO"),
    ("Rio Verde", "GO"),
    ("Cuiabá", "MT"),
    ("Várzea Grande", "MT"),
    ("Rondonópolis", "MT"),
    ("Campo Grande", "MS"),
    ("Dourados", "MS"),
    ("Manaus", "AM"),
    ("Belém", "PA"),
    ("Ananindeua", "PA"),
    ("Santarém", "PA"),
    ("Porto Velho", "RO"),
    ("Macapá", "AP"),
    ("Palmas", "TO"),
    ("Boa Vista", "RR"),
    ("Rio Branco", "AC"),
    ("Ji-Paraná", "RO"),
    
    # Grupo 5: Cidades médias complementares (20 cidades)
    ("Uberlândia", "MG"),
    ("Juiz de Fora", "MG"),
    ("Montes Claros", "MG"),
    ("Uberaba", "MG"),
    ("Joinville", "SC"),
    ("Blumenau", "SC"),
    ("Chapecó", "SC"),
    ("Vitória", "ES"),
    ("Vila Velha", "ES"),
    ("Cariacica", "ES"),
    ("Campos dos Goytacazes", "RJ"),
    ("Volta Redonda", "RJ"),
    ("Nova Iguaçu", "RJ"),
    ("Franca", "SP"),
    ("Limeira", "SP"),
    ("Suzano", "SP"),
    ("Americana", "SP"),
    ("Praia Grande", "SP"),
    ("Guarujá", "SP"),
    ("Taubaté", "SP"),
]


def get_weekly_cities(week_number: int) -> List[Tuple[str, str]]:
    """
    Retorna 20 cidades para scraping baseado no número da semana
    
    Rotação de 5 semanas, cobrindo 100 cidades (20 por semana)
    Após semana 5, reinicia do grupo 1
    
    Args:
        week_number: Número da semana ISO (1-53)
    
    Returns:
        Lista de tuplas (cidade, estado) para scraping
    
    Examples:
        >>> get_weekly_cities(1)  # Semana 1 = Grupo 1
        [("São Paulo", "SP"), ("Guarulhos", "SP"), ...]
        
        >>> get_weekly_cities(6)  # Semana 6 = Grupo 1 novamente
        [("São Paulo", "SP"), ("Guarulhos", "SP"), ...]
    """
    # Determinar qual grupo (ciclo de 5 semanas)
    group_index = ((week_number - 1) % 5)
    
    # Cada grupo tem 20 cidades
    start_index = group_index * 20
    end_index = start_index + 20
    
    selected_cities = CITIES[start_index:end_index]
    
    return selected_cities


def build_city_url(city: str, state: str) -> str:
    """
    Constrói URL do GetNinjas para uma cidade específica
    
    Args:
        city: Nome da cidade (ex: "São Paulo", "Rio de Janeiro")
        state: Sigla do estado (ex: "SP", "RJ")
    
    Returns:
        URL completa para busca de guincho na cidade
    
    Examples:
        >>> build_city_url("Campinas", "SP")
        'https://www.getninjas.com.br/automoveis/guincho/campinas-sp'
        
        >>> build_city_url("São Paulo", "SP")
        'https://www.getninjas.com.br/automoveis/guincho/sao-paulo-sp'
    """
    # Normalizar nome da cidade
    city_normalized = city.lower()
    
    # Remover acentos
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c'
    }
    
    for accented, normal in replacements.items():
        city_normalized = city_normalized.replace(accented, normal)
    
    # Substituir espaços por hífens
    city_normalized = city_normalized.replace(' ', '-')
    
    # Remover caracteres especiais (manter apenas letras, números e hífens)
    city_normalized = ''.join(c for c in city_normalized if c.isalnum() or c == '-')
    
    # Normalizar estado para minúsculas
    state_normalized = state.lower()
    
    # Construir URL
    url = f"https://www.getninjas.com.br/automoveis/guincho/{city_normalized}-{state_normalized}"
    
    return url
