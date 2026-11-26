"""Coleta os dados diários na API histórica Open-Meteo e preserva a resposta original.

Uso: python src/coleta.py
Gera: dados/brutos/openmeteo_<cidade>_<inicio>_<fim>.json
"""

import json
from datetime import datetime

import requests

from config import (CIDADE_ID, CIDADE_NOME, DATA_FIM, DATA_INICIO,
                    FUSO_HORARIO, LATITUDE, LONGITUDE, PASTA_BRUTOS, URL_API,
                    VARIAVEIS_API)


def montar_parametros():
    return {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": DATA_INICIO,
        "end_date": DATA_FIM,
        "daily": ",".join(VARIAVEIS_API),
        "timezone": FUSO_HORARIO,
    }


def solicitar_dados(parametros):
    """Faz a requisição à API e devolve o JSON da resposta, sem alterações."""
    resposta = requests.get(URL_API, params=parametros, timeout=30)
    resposta.raise_for_status()
    return resposta.json()


def salvar_bruto(resposta, parametros):
    """Salva a resposta original junto com os metadados da coleta."""
    PASTA_BRUTOS.mkdir(parents=True, exist_ok=True)
    arquivo = PASTA_BRUTOS / f"openmeteo_{CIDADE_ID}_{DATA_INICIO}_{DATA_FIM}.json"
    conteudo = {
        "metadados": {
            "cidade_id": CIDADE_ID,
            "cidade_nome": CIDADE_NOME,
            "fonte": URL_API,
            "parametros": parametros,
            "data_coleta": datetime.now().isoformat(timespec="seconds"),
        },
        "resposta_api": resposta,
    }
    arquivo.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


def main():
    parametros = montar_parametros()
    print(f"Coletando {CIDADE_NOME} de {DATA_INICIO} a {DATA_FIM}...")
    resposta = solicitar_dados(parametros)
    arquivo = salvar_bruto(resposta, parametros)
    dias = len(resposta["daily"]["time"])
    print(f"{dias} dias recebidos. Resposta original salva em {arquivo}")


if __name__ == "__main__":
    main()
