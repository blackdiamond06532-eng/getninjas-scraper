#!/usr/bin/env python3
"""
Script principal para orquestrar execução completa do scraper GetNinjas
"""
import os
import sys
import asyncio
import random
import json
from datetime import datetime, date
from typing import List, Dict

# Adicionar src ao path se necessário
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proxy_manager import ProxyManager
from telegram_bot import TelegramBot
from cities import get_weekly_cities
from scraper import scrape_city_wrapper
import config


def load_environment():
    """Carrega variáveis de ambiente necessárias"""
    print("🔧 Carregando configurações...")
    
    # Tentar carregar .env se existir (desenvolvimento local)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("  ✓ Arquivo .env carregado")
    except ImportError:
        print("  - python-dotenv não instalado (modo produção)")
    except:
        pass
    
    # Validar variáveis críticas
    required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"  ❌ Variáveis obrigatórias faltando: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ Configurações carregadas")
    return True


def get_current_week_number() -> int:
    """Retorna número da semana ISO atual"""
    week_num = date.today().isocalendar()[1]
    print(f"📅 Semana ISO atual: {week_num}")
    return week_num


def remove_duplicates(professionals: List[Dict]) -> List[Dict]:
    """
    Remove profissionais duplicados por telefone
    
    Args:
        professionals: Lista de profissionais
    
    Returns:
        Lista sem duplicatas
    """
    seen_phones = set()
    unique_professionals = []
    
    for prof in professionals:
        phone = prof.get('telefone', '')
        if phone and phone not in seen_phones:
            seen_phones.add(phone)
            unique_professionals.append(prof)
    
    duplicates_removed = len(professionals) - len(unique_professionals)
    if duplicates_removed > 0:
        print(f"🔄 {duplicates_removed} duplicatas removidas")
    
    return unique_professionals


def validate_professionals(professionals: List[Dict]) -> List[Dict]:
    """
    Valida e filtra profissionais com campos obrigatórios
    
    Args:
        professionals: Lista de profissionais
    
    Returns:
        Lista apenas com profissionais válidos
    """
    valid = []
    
    for prof in professionals:
        # Verificar campos obrigatórios
        if all(prof.get(field) for field in config.REQUIRED_FIELDS):
            valid.append(prof)
    
    invalid_count = len(professionals) - len(valid)
    if invalid_count > 0:
        print(f"⚠️  {invalid_count} profissionais inválidos removidos")
    
    return valid


def save_results_locally(professionals: List[Dict], output_dir: str = "output/results"):
    """
    Salva resultados em arquivo JSON local
    
    Args:
        professionals: Lista de profissionais
        output_dir: Diretório de saída
    
    Returns:
        Caminho do arquivo salvo
    """
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"guincho_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Salvar JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(professionals, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Resultados salvos: {filepath}")
    return filepath


async def main():
    """Função principal de execução"""
    print("=" * 60)
    print("🚗 SCRAPER GETNINJAS - GUINCHO")
    print("=" * 60)
    print()
    
    # 1. Setup inicial
    if not load_environment():
        print("❌ Erro na configuração. Abortando...")
        sys.exit(1)
    
    print()
    
    # 2. Inicializar componentes
    print("🔌 Inicializando componentes...")
    
    try:
        proxy_manager = ProxyManager()
        telegram_bot = TelegramBot()
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        sys.exit(1)
    
    print()
    
    # 3. Obter cidades da semana
    week_number = get_current_week_number()
    cities = get_weekly_cities(week_number)
    
    print()
    print("=" * 60)
    print(f"🎯 INICIANDO COLETA - {len(cities)} CIDADES")
    print("=" * 60)
    
    # 4. Loop de scraping
    all_professionals = []
    successful_cities = 0
    
    for idx, (city, state) in enumerate(cities, 1):
        print(f"\n[{idx}/{len(cities)}] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        try:
            # Scrape cidade
            professionals = await scrape_city_wrapper(proxy_manager, city, state)
            
            if professionals:
                all_professionals.extend(professionals)
                successful_cities += 1
            
            # Delay entre cidades (comportamento humano)
            if idx < len(cities):
                delay = random.uniform(
                    config.DELAY_BETWEEN_CITIES[0], 
                    config.DELAY_BETWEEN_CITIES[1]
                )
                print(f"   ⏳ Aguardando {delay:.1f}s antes da próxima cidade...")
                await asyncio.sleep(delay)
        
        except Exception as e:
            print(f"   ❌ Erro crítico na cidade: {e}")
            continue
    
    print()
    print("=" * 60)
    print("📊 PROCESSAMENTO FINAL")
    print("=" * 60)
    
    # 5. Pós-processamento
    print(f"\n📋 Total bruto coletado: {len(all_professionals)} profissionais")
    
    # Remover duplicatas
    all_professionals = remove_duplicates(all_professionals)
    print(f"📋 Após remover duplicatas: {len(all_professionals)}")
    
    # Validar dados
    all_professionals = validate_professionals(all_professionals)
    print(f"📋 Profissionais válidos: {len(all_professionals)}")
    
    # 6. Salvar localmente
    print()
    if all_professionals:
        save_results_locally(all_professionals)
    
    # 7. Estatísticas
    print()
    print("=" * 60)
    print("📈 ESTATÍSTICAS FINAIS")
    print("=" * 60)
    print(f"🏙️  Cidades processadas: {successful_cities}/{len(cities)}")
    print(f"👥 Total de profissionais: {len(all_professionals)}")
    
    if successful_cities > 0:
        avg_per_city = len(all_professionals) / successful_cities
        print(f"📊 Média por cidade: {avg_per_city:.1f}")
    
    # Distribuição por estado
    states_count = {}
    for prof in all_professionals:
        state = prof.get('estado', 'N/A')
        states_count[state] = states_count.get(state, 0) + 1
    
    print(f"\n🗺️  Distribuição por estado:")
    for state, count in sorted(states_count.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   {state}: {count} profissionais")
    
    # 8. Enviar para Telegram
    print()
    print("=" * 60)
    print("📤 ENVIANDO RESULTADOS")
    print("=" * 60)
    
    if all_professionals:
        # Enviar arquivo JSON
        success = telegram_bot.send_json_file(all_professionals)
        
        if success:
            # Enviar mensagem de resumo
            date_str = datetime.now().strftime("%d/%m/%Y")
            telegram_bot.send_summary_message(
                total=len(all_professionals),
                cities_count=successful_cities,
                date=date_str
            )
        
        print()
        print("✅ Scraping concluído com sucesso!")
        return 0
    
    else:
        error_msg = f"Nenhum profissional coletado. Cidades: {successful_cities}/{len(cities)}"
        print(f"\n⚠️  {error_msg}")
        
        # Notificar erro no Telegram
        telegram_bot.send_error_notification(error_msg)
        
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
