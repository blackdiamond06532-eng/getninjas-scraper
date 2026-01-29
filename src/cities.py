"""
Lista de 100 cidades brasileiras para scraping rotativo
Divididas em grupos para rotacao diaria
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
    
    # Grupo 5 - Dia 81-100: Cidades medias complementares
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


def get_daily_cities():
    """
    Retorna 5 cidades para scraping diario (meta: 100 profissionais/dia)
    Rotaciona atraves das 100 cidades em 20 dias
    
    Returns:
        Lista de 5 tuplas (cidade, uf)
    """
    import datetime
    
    # Usar dia do ano para rotacao (1-365)
    day_of_year = datetime.date.today().timetuple().tm_yday
    
    # Cada grupo tem 5 cidades
    # 100 cidades / 5 = 20 grupos
    # Roda tudo em 20 dias, depois reinicia
    group_index = (day_of_year - 1) % 20
    
    start_index = group_index * 5
    end_index = start_index + 5
    
    cities = CITIES_LIST[start_index:end_index]
    
    print(f"📍 Dia {day_of_year} do ano - Grupo {group_index + 1}/20")
    print(f"🏙️  Cidades selecionadas: {len(cities)}")
    for city, state in cities:
        city_name = city.replace("-", " ").title()
        print(f"   • {city_name}/{state.upper()}")
    
    return cities


def get_all_cities():
    """Retorna todas as 100 cidades"""
    return CITIES_LIST
