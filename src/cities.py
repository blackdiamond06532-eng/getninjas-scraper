"""
Lista de 100 cidades brasileiras para scraping rotativo
Divididas em 5 grupos de 20 cidades cada
"""

# Lista completa de 100 cidades brasileiras (cidade, UF)
CITIES_LIST = [
    # Grupo 1 - Dia 1-20: São Paulo Capital + Grande SP + RJ + MG
    ("sao-paulo", "sp"),
    ("guarulhos", "sp"),
    ("sao-bernardo-do-campo", "sp"),
    ("santo-andre", "sp"),
    ("osasco", "sp"),
    ("sao-caetano-do-sul", "sp"),
    ("maua", "sp"),
    ("diadema", "sp"),
    ("barueri", "sp"),
    ("cotia", "sp"),
    ("rio-de-janeiro", "rj"),
    ("niteroi", "rj"),
    ("sao-goncalo", "rj"),
    ("duque-de-caxias", "rj"),
    ("nova-iguacu", "rj"),
    ("belo-horizonte", "mg"),
    ("contagem", "mg"),
    ("betim", "mg"),
    ("uberlandia", "mg"),
    ("juiz-de-fora", "mg"),
    
    # Grupo 2 - Dia 21-40: Interior SP + Sul
    ("campinas", "sp"),
    ("sao-jose-dos-campos", "sp"),
    ("ribeirao-preto", "sp"),
    ("sorocaba", "sp"),
    ("santos", "sp"),
    ("sao-jose-do-rio-preto", "sp"),
    ("piracicaba", "sp"),
    ("bauru", "sp"),
    ("jundiai", "sp"),
    ("franca", "sp"),
    ("curitiba", "pr"),
    ("londrina", "pr"),
    ("maringa", "pr"),
    ("ponta-grossa", "pr"),
    ("cascavel", "pr"),
    ("porto-alegre", "rs"),
    ("caxias-do-sul", "rs"),
    ("pelotas", "rs"),
    ("canoas", "rs"),
    ("santa-maria", "rs"),
    
    # Grupo 3 - Dia 41-60: Nordeste
    ("salvador", "ba"),
    ("feira-de-santana", "ba"),
    ("vitoria-da-conquista", "ba"),
    ("camacari", "ba"),
    ("itabuna", "ba"),
    ("fortaleza", "ce"),
    ("caucaia", "ce"),
    ("juazeiro-do-norte", "ce"),
    ("maracanau", "ce"),
    ("sobral", "ce"),
    ("recife", "pe"),
    ("jaboatao-dos-guararapes", "pe"),
    ("olinda", "pe"),
    ("caruaru", "pe"),
    ("petrolina", "pe"),
    ("natal", "rn"),
    ("mossoro", "rn"),
    ("parnamirim", "rn"),
    ("sao-luis", "ma"),
    ("imperatriz", "ma"),
    
    # Grupo 4 - Dia 61-80: Norte + Centro-Oeste
    ("manaus", "am"),
    ("belem", "pa"),
    ("ananindeua", "pa"),
    ("santarem", "pa"),
    ("macapa", "ap"),
    ("palmas", "to"),
    ("araguaina", "to"),
    ("porto-velho", "ro"),
    ("rio-branco", "ac"),
    ("boa-vista", "rr"),
    ("brasilia", "df"),
    ("goiania", "go"),
    ("aparecida-de-goiania", "go"),
    ("anapolis", "go"),
    ("rio-verde", "go"),
    ("cuiaba", "mt"),
    ("varzea-grande", "mt"),
    ("rondonopolis", "mt"),
    ("campo-grande", "ms"),
    ("dourados", "ms"),
    
    # Grupo 5 - Dia 81-100: Cidades médias complementares
    ("florianopolis", "sc"),
    ("joinville", "sc"),
    ("blumenau", "sc"),
    ("sao-jose", "sc"),
    ("criciuma", "sc"),
    ("vitoria", "es"),
    ("vila-velha", "es"),
    ("serra", "es"),
    ("cariacica", "es"),
    ("cachoeiro-de-itapemirim", "es"),
    ("maceio", "al"),
    ("aracaju", "se"),
    ("joao-pessoa", "pb"),
    ("campina-grande", "pb"),
    ("teresina", "pi"),
    ("parnaiba", "pi"),
    ("petropolis", "rj"),
    ("volta-redonda", "rj"),
    ("campos-dos-goytacazes", "rj"),
    ("marilia", "sp"),
]


def get_weekly_cities(week_number):
    """
    Retorna 20 cidades baseado no número da semana ISO
    
    Args:
        week_number: Número da semana (1-53)
    
    Returns:
        Lista de tuplas (cidade, uf) com 20 cidades
    """
    # Calcular qual grupo usar (semanas 1-5, depois repete)
    group_index = ((week_number - 1) % 5)
    
    # Cada grupo tem 20 cidades
    start_index = group_index * 20
    end_index = start_index + 20
    
    cities = CITIES_LIST[start_index:end_index]
    
    print(f"📍 Semana {week_number} - Grupo {group_index + 1}")
    print(f"🏙️  Cidades selecionadas: {len(cities)}")
    
    return cities


def build_
