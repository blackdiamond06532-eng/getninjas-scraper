def get_daily_cities() -> list:
    """
    Retorna 5 cidades para scraping diário (meta: 100 profissionais/dia)
    Rotaciona através das 100 cidades
    
    Returns:
        Lista de 5 tuplas (cidade, uf)
    """
    import datetime
    
    # Usar dia do ano para rotação (1-365)
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


def get_daily_cities() -> list:
    """
    Retorna 5 cidades para scraping diário (meta: 100 profissionais/dia)
    Rotaciona através das 100 cidades
    
    Returns:
        Lista de 5 tuplas (cidade, uf)
    """
    import datetime
    
    # Usar dia do ano para rotação (1-365)
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
