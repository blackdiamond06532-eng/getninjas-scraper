"""
Gerenciador de 11 proxies com rotação automática
Suporta proxies com e sem autenticação
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
        
        Formatos aceitos:
        - http://usuario:senha@ip:porta
        - http://ip:porta
        - ip:porta (será convertido para http://ip:porta)
        """
        proxies = []
        
        for i in range(1, 12):  # PROXY_1 até PROXY_11
            proxy_key = f"PROXY_{i}"
            proxy = os.getenv(proxy_key)
            
            if proxy:
                # Normalizar formato
                normalized = self._normalize_proxy_format(proxy)
                
                if normalized:
                    proxies.append(normalized)
                    print(f"  ✓ {proxy_key} carregado")
                else:
                    print(f"  ✗ {proxy_key} formato inválido")
            else:
                print(f"  - {proxy_key} não configurado")
        
        return proxies
    
    def _normalize_proxy_format(self, proxy: str) -> Optional[str]:
        """
        Normaliza proxy para formato Playwright
        
        Aceita:
        - http://user:pass@ip:port
        - http://ip:port
        - ip:port
        
        Returns:
            Proxy normalizado ou None se inválido
        """
        proxy = proxy.strip()
        
        # Já está no formato correto
        if proxy.startswith("http://") or proxy.startswith("https://"):
            return proxy
        
        # Formato ip:porta simples
        if ":" in proxy and not proxy.startswith("http"):
            return f"http://{proxy}"
        
        return None
    
    def get_next_proxy(self) -> Optional[str]:
        """Retorna próximo proxy da rotação sequencial"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return proxy
    
    def get_proxy_config(self) -> Optional[dict]:
        """
        Retorna configuração do proxy no formato Playwright
        
        Returns:
            Dict com configuração ou None
        """
        proxy_url = self.get_next_proxy()
        
        if not proxy_url:
            return None
        
        try:
            # Proxy com autenticação: http://user:pass@ip:port
            if "@" in proxy_url:
                protocol_auth, server = proxy_url.split("@")
                protocol, auth = protocol_auth.split("://")
                username, password = auth.split(":")
                
                return {
                    "server": f"http://{server}",
                    "username": username,
                    "password": password
                }
            
            # Proxy sem autenticação: http://ip:port
            else:
                return {"server": proxy_url}
        
        except Exception as e:
            print(f"❌ Erro ao processar proxy: {e}")
            return None
    
    def get_total_proxies(self) -> int:
        """Retorna quantidade de proxies disponíveis"""
        return len(self.proxies)
    
    def reset_rotation(self):
        """Reseta o índice de rotação para o início"""
        self.current_index = 0
