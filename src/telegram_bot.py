"""
Cliente para envio de resultados via Telegram Bot API
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict


class TelegramBot:
    """Cliente para envio de arquivos e mensagens via Telegram"""
    
    def __init__(self):
        """Inicializa com credenciais das variáveis de ambiente"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            raise ValueError(
                "❌ Variáveis TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID são obrigatórias!"
            )
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        print("✅ Telegram Bot inicializado")
    
    def send_json_file(self, professionals_list: List[Dict]) -> bool:
        """
        Converte lista de profissionais para JSON e envia via Telegram
        
        Args:
            professionals_list: Lista de dicionários com dados dos profissionais
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Gerar nome do arquivo com data atual
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"guincho_{date_str}.json"
            
            # Converter para JSON com formatação
            json_content = json.dumps(
                professionals_list,
                indent=2,
                ensure_ascii=False
            )
            
            # Criar resumo para caption
            total = len(professionals_list)
            cities = len(set(p.get('cidade', '') for p in professionals_list))
            date_today = datetime.now().strftime("%d/%m/%Y")
            
            caption = (
                f"🚗 Scraping GetNinjas - Guincho\n"
                f"📅 Data: {date_today}\n"
                f"👥 Total: {total} profissionais\n"
                f"🏙️  Cidades: {cities}\n"
                f"✅ Coleta finalizada com sucesso!"
            )
            
            # Preparar requisição
            url = f"{self.base_url}/sendDocument"
            
            data = {
                'chat_id': self.chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            
            files = {
                'document': (filename, json_content.encode('utf-8'), 'application/json')
            }
            
            # Enviar documento
            print(f"📤 Enviando arquivo {filename} para Telegram...")
            response = requests.post(url, data=data, files=files, timeout=30)
            
            if response.status_code == 200:
                print("✅ Arquivo enviado com sucesso!")
                return True
            else:
                print(f"❌ Erro ao enviar: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Erro ao enviar arquivo para Telegram: {e}")
            return False
    
    def send_summary_message(self, total: int, cities_count: int, date: str) -> bool:
        """
        Envia mensagem de texto com resumo da coleta
        
        Args:
            total: Total de profissionais coletados
            cities_count: Número de cidades processadas
            date: Data da coleta (formato YYYY-MM-DD)
        
        Returns:
            True se enviado com sucesso
        """
        try:
            message = (
                f"📊 <b>Resumo da Coleta GetNinjas</b>\n\n"
                f"📅 <b>Data:</b> {date}\n"
                f"👥 <b>Profissionais:</b> {total}\n"
                f"🏙️  <b>Cidades:</b> {cities_count}\n"
                f"📈 <b>Média:</b> {total/cities_count:.1f} por cidade\n\n"
                f"✅ <i>Scraping concluído com sucesso!</i>"
            )
            
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                print("✅ Mensagem resumo enviada!")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Envia notificação de erro
        
        Args:
            error_message: Mensagem de erro
        
        Returns:
            True se enviado com sucesso
        """
        try:
            message = f"⚠️ <b>Erro no Scraper GetNinjas</b>\n\n{error_message}"
            
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=30)
            return response.status_code == 200
        
        except Exception:
            return False
