"""Configurações do projeto. Altere aqui a localidade e o período."""

from pathlib import Path

# Localidade (coordenadas em https://open-meteo.com/en/docs ou no Google Maps)
CIDADE_ID = "sao_paulo_sp"        # identificador sem acentos nem espaços
CIDADE_NOME = "São Paulo - SP"
LATITUDE = -23.55
LONGITUDE = -46.63
FUSO_HORARIO = "America/Sao_Paulo"

# Período: 30 dias consecutivos
DATA_INICIO = "2026-09-01"
DATA_FIM = "2026-09-30"
TOTAL_DIAS = 30

# Três variáveis: temperatura mínima, temperatura máxima e precipitação
URL_API = "https://archive-api.open-meteo.com/v1/archive"
VARIAVEIS_API = ["temperature_2m_min", "temperature_2m_max", "precipitation_sum"]
UNIDADES_ESPERADAS = {
    "temperature_2m_min": "°C",
    "temperature_2m_max": "°C",
    "precipitation_sum": "mm",
}

# Faixas plausíveis para a localidade (ajuste se mudar a cidade).
# São Paulo: mínima histórica perto de -2 °C e máxima perto de 38 °C,
# então -5 a 45 °C dá folga sem aceitar valores absurdos.
TEMP_MIN_PLAUSIVEL = -5.0
TEMP_MAX_PLAUSIVEL = 45.0
PRECIP_MAX_PLAUSIVEL = 200.0   # mm em um dia

# Dia com chuva: precipitação de pelo menos 1 mm
LIMIAR_DIA_CHUVOSO_MM = 1.0

# Caminhos
RAIZ = Path(__file__).resolve().parent.parent
PASTA_BRUTOS = RAIZ / "dados" / "brutos"
PASTA_PROCESSADOS = RAIZ / "dados" / "processados"
ARQUIVO_BANCO = PASTA_PROCESSADOS / "observatorio.duckdb"
ARQUIVO_CSV = PASTA_PROCESSADOS / "clima_diario.csv"
ARQUIVO_QUALIDADE = PASTA_PROCESSADOS / "relatorio_qualidade.md"
ARQUIVO_RESULTADOS = PASTA_PROCESSADOS / "resultados_consultas.md"
ARQUIVO_SQL = RAIZ / "sql" / "consultas.sql"
