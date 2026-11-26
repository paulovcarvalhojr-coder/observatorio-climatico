"""Trata e valida os dados com pandas, carrega no DuckDB e executa as consultas.

Uso: python src/banco.py  (rode depois de coleta.py)
Gera: dados/processados/clima_diario.csv, observatorio.duckdb,
      relatorio_qualidade.md e resultados_consultas.md
"""

import json
import sys

import duckdb
import pandas as pd

from config import (ARQUIVO_BANCO, ARQUIVO_CSV, ARQUIVO_QUALIDADE,
                    ARQUIVO_RESULTADOS, ARQUIVO_SQL, CIDADE_ID, DATA_FIM,
                    DATA_INICIO, PASTA_BRUTOS, PRECIP_MAX_PLAUSIVEL,
                    TEMP_MAX_PLAUSIVEL, TEMP_MIN_PLAUSIVEL, TOTAL_DIAS,
                    UNIDADES_ESPERADAS)

NOMES_COLUNAS = {
    "time": "data",
    "temperature_2m_min": "temperatura_min",
    "temperature_2m_max": "temperatura_max",
    "precipitation_sum": "precipitacao",
}

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS clima_diario (
    cidade_id        VARCHAR   NOT NULL,
    cidade_nome      VARCHAR   NOT NULL,
    latitude         DOUBLE    NOT NULL,
    longitude        DOUBLE    NOT NULL,
    data             DATE      NOT NULL,
    temperatura_min  DOUBLE,
    temperatura_max  DOUBLE,
    precipitacao     DOUBLE,
    data_coleta      TIMESTAMP NOT NULL,
    PRIMARY KEY (cidade_id, data)
)
"""


# ---------- Leitura e tratamento ----------

def ler_bruto():
    arquivo = PASTA_BRUTOS / f"openmeteo_{CIDADE_ID}_{DATA_INICIO}_{DATA_FIM}.json"
    if not arquivo.exists():
        sys.exit(f"Arquivo {arquivo} não encontrado. Rode antes: python src/coleta.py")
    return json.loads(arquivo.read_text(encoding="utf-8"))


def tratar(bruto):
    """Converte o JSON em DataFrame com nomes e tipos padronizados.

    Valores ausentes continuam ausentes (NaN): não são trocados por zero.
    """
    meta, resposta = bruto["metadados"], bruto["resposta_api"]
    df = pd.DataFrame(resposta["daily"]).rename(columns=NOMES_COLUNAS)
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d", errors="coerce").dt.date
    for coluna in ["temperatura_min", "temperatura_max", "precipitacao"]:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df.insert(0, "cidade_id", meta["cidade_id"])
    df.insert(1, "cidade_nome", meta["cidade_nome"])
    df.insert(2, "latitude", resposta["latitude"])
    df.insert(3, "longitude", resposta["longitude"])
    df["data_coleta"] = pd.to_datetime(meta["data_coleta"])
    return df


# ---------- Checagens de qualidade ----------

def validar(df, unidades):
    """Executa as checagens do plano de qualidade.

    Devolve uma lista de (checagem, passou, detalhe, critica).
    Falha em checagem crítica impede a carga no banco.
    """
    r = []
    inicio, fim = pd.Timestamp(DATA_INICIO).date(), pd.Timestamp(DATA_FIM).date()

    dup = df.duplicated(subset=["cidade_id", "data"]).sum()
    r.append(("1. Duplicidade (cidade_id, data)", dup == 0, f"{dup} registros duplicados", True))

    obrig = df[["cidade_id", "data"]].isna().sum().sum()
    r.append(("2. Campos obrigatórios preenchidos", obrig == 0, f"{obrig} vazios", True))

    fora = df["data"].apply(lambda d: d is None or pd.isna(d) or not (inicio <= d <= fim)).sum()
    r.append(("3. Datas válidas e dentro do recorte", fora == 0, f"{fora} datas inválidas ou fora de {inicio} a {fim}", True))

    esperadas = set(pd.date_range(inicio, fim).date)
    faltando = sorted(esperadas - set(df["data"].dropna()))
    cobertura = len(esperadas) == TOTAL_DIAS and not faltando
    r.append(("4. Cobertura dos 30 dias consecutivos", cobertura,
              f"{len(set(df['data'].dropna()))} de {TOTAL_DIAS} dias; faltando: {faltando or 'nenhum'}", True))

    nulos = df[["temperatura_min", "temperatura_max", "precipitacao"]].isna().sum()
    r.append(("5. Ausências nas variáveis", nulos.sum() == 0,
              ", ".join(f"{c}: {n}" for c, n in nulos.items()) + " (mantidos como ausentes)", False))

    inv = (df["temperatura_min"] > df["temperatura_max"]).sum()
    r.append(("6. Temperatura mínima <= máxima", inv == 0, f"{inv} dias com mínima maior que máxima", True))

    neg = (df["precipitacao"] < 0).sum()
    r.append(("7. Precipitação não negativa", neg == 0, f"{neg} valores negativos", True))

    diverg = {k: unidades.get(k) for k, v in UNIDADES_ESPERADAS.items() if unidades.get(k) != v}
    r.append(("8. Unidades compatíveis com o dicionário", not diverg, f"divergentes: {diverg or 'nenhuma'}", True))

    temps = df[["temperatura_min", "temperatura_max"]]
    fora_temp = ((temps < TEMP_MIN_PLAUSIVEL) | (temps > TEMP_MAX_PLAUSIVEL)).sum().sum()
    fora_prec = (df["precipitacao"] > PRECIP_MAX_PLAUSIVEL).sum()
    r.append(("9. Faixas plausíveis", fora_temp + fora_prec == 0,
              f"{fora_temp} temperaturas fora de {TEMP_MIN_PLAUSIVEL} a {TEMP_MAX_PLAUSIVEL} °C; "
              f"{fora_prec} precipitações acima de {PRECIP_MAX_PLAUSIVEL} mm", False))
    return r


def situacao(ok, critica):
    return "OK" if ok else ("FALHOU" if critica else "ALERTA")


def salvar_relatorio_qualidade(resultados, df):
    linhas = ["# Relatório de qualidade dos dados", "",
              f"Registros tratados: {len(df)}", "",
              "| Checagem | Resultado | Detalhe | Crítica |", "|---|---|---|---|"]
    for nome, ok, detalhe, critica in resultados:
        linhas.append(f"| {nome} | {situacao(ok, critica)} | {detalhe} | {'sim' if critica else 'não'} |")
    ARQUIVO_QUALIDADE.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ---------- Banco e consultas ----------

def conectar(somente_leitura=False):
    return duckdb.connect(str(ARQUIVO_BANCO), read_only=somente_leitura)


def carregar(con, df):
    """Carga idempotente: rodar de novo substitui os registros, sem duplicar."""
    con.execute(CRIAR_TABELA)
    con.execute("INSERT OR REPLACE INTO clima_diario SELECT * FROM df")


def ler_consultas():
    """Lê sql/consultas.sql e devolve {nome: sql}. Cada consulta começa com '-- name:'."""
    consultas, nome = {}, None
    for linha in ARQUIVO_SQL.read_text(encoding="utf-8").splitlines(keepends=True):
        if linha.startswith("-- name:"):
            nome = linha.split(":", 1)[1].strip()
            consultas[nome] = ""
        elif nome:
            consultas[nome] += linha
    return {n: sql.strip() for n, sql in consultas.items()}


def executar(con, nome):
    return con.execute(ler_consultas()[nome]).df()


def main():
    bruto = ler_bruto()
    df = tratar(bruto)
    resultados = validar(df, bruto["resposta_api"].get("daily_units", {}))

    ARQUIVO_CSV.parent.mkdir(parents=True, exist_ok=True)
    salvar_relatorio_qualidade(resultados, df)
    print("Checagens de qualidade:")
    for nome, ok, detalhe, critica in resultados:
        print(f"  [{situacao(ok, critica)}] {nome}: {detalhe}")

    if any(not ok and critica for _, ok, _, critica in resultados):
        sys.exit(f"Carga cancelada por falha crítica. Veja {ARQUIVO_QUALIDADE}")

    df.to_csv(ARQUIVO_CSV, index=False)
    con = conectar()
    carregar(con, df)
    total = con.execute("SELECT COUNT(*) FROM clima_diario").fetchone()[0]
    print(f"\nTabela clima_diario com {total} registros.")

    saida = ["# Resultados das consultas", ""]
    for nome in ler_consultas():
        resultado = executar(con, nome)
        if "data" in resultado:
            resultado["data"] = resultado["data"].dt.strftime("%d/%m/%Y")
        tabela = resultado.to_markdown(index=False)
        print(f"\n== {nome} ==\n{tabela}")
        saida += [f"## {nome}", "", tabela, ""]
    ARQUIVO_RESULTADOS.write_text("\n".join(saida), encoding="utf-8")
    con.close()
    print(f"\nResultados salvos em {ARQUIVO_RESULTADOS}")


if __name__ == "__main__":
    main()
