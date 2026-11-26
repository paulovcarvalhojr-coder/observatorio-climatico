"""Painel do Observatório Climático Local.

Uso: streamlit run src/app.py  (rode depois de coleta.py e banco.py)
"""

import streamlit as st

from banco import conectar, executar
from config import CIDADE_NOME, DATA_FIM, DATA_INICIO, LATITUDE, LONGITUDE

st.set_page_config(page_title="Observatório Climático Local", layout="wide")

con = conectar(somente_leitura=True)
kpis = executar(con, "kpis").iloc[0]
registros = executar(con, "registros")
p1 = executar(con, "p1_temperatura_maxima").iloc[0]
p2 = executar(con, "p2_dias_mais_chuvosos")
p3 = executar(con, "p3_amplitude_termica")
con.close()

inicio = registros["data"].min().strftime("%d/%m/%Y")
fim = registros["data"].max().strftime("%d/%m/%Y")

st.title("Observatório Climático Local")
st.caption(f"{CIDADE_NOME} (lat. {LATITUDE}, long. {LONGITUDE}) · {inicio} a {fim} · "
           "Fonte: API histórica Open-Meteo")

# Três indicadores
c1, c2, c3 = st.columns(3)
c1.metric("Média das temperaturas máximas", f"{kpis.kpi1_media_max_c:.1f} °C")
c2.metric("Precipitação total", f"{kpis.kpi2_precipitacao_total_mm:.1f} mm")
c3.metric("Dias com chuva (≥ 1 mm)", f"{int(kpis.kpi3_dias_com_chuva)} de {len(registros)}")

# Dois gráficos
serie = registros.set_index("data")
g1, g2 = st.columns(2)
with g1:
    st.subheader("Temperatura mínima e máxima diária (°C)")
    st.line_chart(serie[["temperatura_min", "temperatura_max"]].rename(
        columns={"temperatura_min": "Mínima", "temperatura_max": "Máxima"}))
with g2:
    st.subheader("Precipitação diária (mm)")
    st.bar_chart(serie["precipitacao"])

# Perguntas analíticas
st.header("Perguntas analíticas")
st.markdown("**1. Qual foi a maior temperatura do período e em qual dia?**")
st.write(f"{p1.temperatura_max_c:.1f} °C, em {p1.data:%d/%m/%Y}.")

st.markdown("**2. Quais foram os dias mais chuvosos?**")
if p2.empty:
    st.write("Nenhum dia com pelo menos 1 mm de chuva no período.")
else:
    st.dataframe(p2.assign(data=p2["data"].dt.strftime("%d/%m/%Y"))
                 .rename(columns={"data": "Dia", "precipitacao_mm": "Chuva (mm)"}), hide_index=True)

st.markdown("**3. Quais dias tiveram a maior diferença entre mínima e máxima?**")
st.write(f"Amplitude térmica média do período: {kpis.amplitude_media_c:.1f} °C.")
st.dataframe(p3.assign(data=p3["data"].dt.strftime("%d/%m/%Y"))
             .rename(columns={"data": "Dia", "min_c": "Mínima (°C)", "max_c": "Máxima (°C)",
                              "amplitude_c": "Amplitude (°C)"}), hide_index=True)

# Tabela de registros
st.header("Registros diários")
st.dataframe(registros.assign(data=registros["data"].dt.strftime("%d/%m/%Y")).rename(columns={
    "data": "Data", "temperatura_min": "Mínima (°C)", "temperatura_max": "Máxima (°C)",
    "precipitacao": "Precipitação (mm)"}), hide_index=True, use_container_width=True)

# Limitações
st.header("Como ler estes dados")
st.info(
    "- Os dados são **históricos** e descrevem o que já aconteceu. Não são previsão do tempo.\n"
    "- A Open-Meteo estima os valores a partir de modelos e reanálises para um ponto da grade, "
    "não de uma estação meteorológica instalada no bairro. Pode haver diferença em relação ao local exato.\n"
    "- O recorte é de apenas 30 dias, curto para falar em tendência climática.\n"
    "- Dias sem dado aparecem em branco: ausência de dado não é o mesmo que zero."
)
