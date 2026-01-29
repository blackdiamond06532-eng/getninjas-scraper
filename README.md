# 🚗 Scraper GetNinjas -

Scraper automatizado para coleta de dados de profissionais de  plataforma GetNinjas, com execução semanal via GitHub Actions e envio de resultados via Telegram.

## 📋 Funcionalidades

- ✅ Scraping automatizado de 20 cidades por semana (100 cidades em rotação)
- ✅ Coleta de 11 campos por profissional
- ✅ Rotação automática de 4 proxies residenciais
- ✅ Anti-detecção com Playwright + playwright-stealth
- ✅ Execução semanal via GitHub Actions (segunda-feira 06:00 UTC)
- ✅ Envio de resultados JSON via Telegram Bot
- ✅ Remoção automática de duplicatas
- ✅ Validação de campos obrigatórios

## 📊 Dados Coletados

Cada profissional contém 11 campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `nome` | string | Nome completo do profissional/empresa |
| `telefone` | string | Número de telefone (apenas dígitos) |
| `cidade` | string | Nome da cidade |
| `estado` | string | Sigla UF (2 caracteres) |
| `categoria` | string | Tipo de serviço (ex: "xxxxxxx") |
| `avaliacao_nota` | float/null | Nota de 0 a 5 |
| `avaliacao_total` | integer | Quantidade de avaliações |
| `servicos_negociados` | integer | Jobs completados |
| `tempo_getninjas` | string | Tempo de cadastro |
| `url_perfil` | string | URL completa do perfil |
| `data_coleta` | string | Data da coleta (YYYY-MM-DD) |

## 🛠️ Stack Técnica

- **Python 3.11+**
- **Playwright** - Automação de navegador
- **playwright-stealth** - Anti-detecção
- **requests** - Telegram API
- **GitHub Actions** - CI/CD automático
- **Telegram Bot API** - Entrega de resultados



Vá em: **Settings → Secrets and variables → Actions → New repository secret**

Configure as seguintes secrets:

