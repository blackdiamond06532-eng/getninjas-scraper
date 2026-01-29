#!/usr/bin/env python3
"""
Gerenciador de proxies rotativos
Carrega proxies das variáveis de ambiente e rotaciona entre eles
"""
import os
from typing import List, Optional


class ProxyManager:
    """Gerencia rotação de proxies"""
    
    def __init__(self):
        """Inicializa o gerenciador carregando proxies das env vars"""
        self.proxies: List[str] = []
        self.current_index = 0
        self._load_proxies()
    
    def _load_proxies(self):
        """Carrega proxies das variáveis de ambiente PROXY_1 até PROXY_11"""
        # Carregar até 11 proxies
        for i in range(1, 12):
            proxy_var = f'PROXY_{i}'
            proxy = os.getenv(proxy_var, '').strip()
            
            if proxy:
                # Auto-fix: adicionar http:// se não tiver
                if not proxy.startswith('http://') and not proxy.startswith('https://'):
                    proxy = f'http://{proxy}'
                    print(f"🔧 {proxy_var}: adicionado http:// automaticamente")
                
                # Validar formato
                if self._validate_proxy(proxy):
                    self.proxies.append(proxy)
                    # Mostrar apenas IP:porta para não logar credenciais
                    display = proxy.replace('http://', '').replace('https://', '')[:30]
                    print(f"✓ {proxy_var} carregado: {display}...")
                else:
                    print(f"⚠️  {proxy_var} inválido após validação")
            else:
                print(f"- {proxy_var} não configurado")
        
        if not self.proxies:
            print("⚠️  AVISO: Nenhum proxy configurado!")
        else:
            print(f"✅ {len(self.proxies)} proxies carregados")
    
    def _validate_proxy(self, proxy: str) -> bool:
        """
        Valida formato do proxy
        
        Args:
            proxy: String do proxy (já com http://)
        
        Returns:
            True se válido, False caso contrário
        """
        if not proxy:
            return False
        
        # Deve começar com http:// ou https://
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            return False
        
        # Remover protocolo para validar o resto
        proxy_without_protocol = proxy.replace('http://', '').replace('https://', '')
        
        # Deve conter ":" para separar IP e porta
        if ':' not in proxy_without_protocol:
            return False
        
        # Validação básica de tamanho (mínimo 7 chars: 1.1.1.1:80)
        if len(proxy_without_protocol) < 9:
            return False
        
        return True
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Retorna o próximo proxy na rotação
        
        Returns:
            String do proxy ou None se não houver proxies
        """
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        
        # Avançar para o próximo (circular)
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return proxy
    
    def get_proxy_count(self) -> int:
        """
        Retorna quantidade de proxies carregados
        
        Returns:
            Número de proxies
        """
        return len(self.proxies)
