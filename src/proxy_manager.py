"""
Gerenciador de 11 proxies com rotação automática
"""
import os
from typing import List, Optional


class ProxyManager:
    """Gerencia rotação de 11 proxies residenciais"""
    
    def __init__(self):
        """Inicializa carregando 11 proxies das variáveis de ambiente"""
        self.proxies = self._load_proxies()
        self.current_index = 0
        
        if not self.proxies:
            print("⚠️  AVISO: Nenhum proxy configurado!")
        else:
            print(f"✅ {len(self.proxies)} proxies carregados")
    
    def _load_proxies(self) -> List[str]:
        """
        Carrega 11 proxies das variáveis de ambiente PROXY_1 até PROXY_11
        Formato esperado: http://usuario:senha@ip:porta
        """
        proxies = []
        
        for i in range(1, 12):  # PROXY_1 até PROXY_11
            proxy_key = f"PROXY_{i}"
            proxy = os.getenv(proxy_key)
            
            if proxy:
                if proxy.startswith("http://") or proxy.startswith("https://"):
                    proxies.append(proxy)
                    print(f"  ✓ {proxy_key} carregado")
                else:
                    print(f"  ✗ {proxy_key} formato inválido")
            else:
                print(f"  - {proxy_key} não configurado")
        
        return proxies
    
    def get_next_proxy(self) -> Optional[str]:
        """Retorna próximo proxy da rotação sequencial"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return proxy
    
    def get_proxy_config(self) -> Optional[dict]:
        """Retorna configuração do proxy no formato Playwright"""
        proxy_url = self.get_next_proxy()
        
        if not proxy_url:
            return None
        
        try:
            if "@" in proxy_url:
                protocol_auth, server = proxy_url.split("@")
                protocol, auth = protocol_auth.split("://")
                username, password = auth.split(":")
                
                return {
                    "server": f"http://{server}",
                    "username": username,
                    "password": password
                }
            else:
                return {"server": proxy_url}
        
        except Exception as e:
            print(f"❌ Erro ao processar proxy: {e}")
            return None
    
    def get_total_proxies(self) -> int:
        """Retorna quantidade de proxies disponíveis"""
        return len(self.proxies)
