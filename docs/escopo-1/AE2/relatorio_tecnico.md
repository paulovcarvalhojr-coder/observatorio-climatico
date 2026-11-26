---
title: "Relatório técnico e analítico: Observatório Climático Local"
subtitle: "Atividade de Estudo: coleta, tratamento, armazenamento e análise inicial"
author: "Paulo [sobrenome] · Projeto Integrador Extensionista 2 · Prof. Luiz Henrique"
date: "Novembro de 2026"
lang: pt-BR
---

> **Antes de entregar:** o projeto já foi executado e os números abaixo vêm de `dados/processados/resultados_consultas.md` e `relatorio_qualidade.md`. Ainda faltam: os prints marcados com `[INSERIR PRINT]`, o link do repositório no GitHub (seção 6), os ajustes em relação à AE1 (seção 1) e a avaliação dos critérios de sucesso da AE1 (seção 4), que dependem do que foi escrito na atividade anterior. Apague este aviso ao concluir.

# 1. Contextualização e continuidade da AE1

O projeto atende à **comunidade escolar** (estudantes, professores de Educação Física e coordenação) de uma escola pública de São Paulo, que precisa planejar atividades ao ar livre considerando calor, variação de temperatura e chuva. O objetivo é transformar dados meteorológicos históricos em informações simples sobre como foi o tempo em um mês.

- **Localidade:** São Paulo - SP (latitude -23,55; longitude -46,63).
- **Período:** 01/09/2026 a 30/09/2026 (30 dias consecutivos).
- **Variáveis:** temperatura mínima diária (°C), temperatura máxima diária (°C) e precipitação diária acumulada (mm).
- **Perguntas analíticas:** (P1) qual foi a maior temperatura e em que dia; (P2) quais foram os dias mais chuvosos; (P3) quais dias tiveram a maior diferença entre mínima e máxima.
- **Indicadores:** média das temperaturas máximas (°C), precipitação total (mm) e número de dias com chuva (≥ 1 mm).
- **Ajustes em relação à AE1:** [descrever, se houver. Ex.: a umidade foi trocada pela temperatura mínima, variável sugerida no enunciado, para permitir a análise de amplitude térmica.]

# 2. Fonte e coleta dos dados

- **Fonte:** API histórica Open-Meteo (`https://archive-api.open-meteo.com/v1/archive`), gratuita e sem chave de acesso. <https://open-meteo.com/>
- **Acesso:** script `src/coleta.py`, em Python, com a biblioteca Requests (`requests.get` com tempo limite de 30 s e verificação de erro HTTP).
- **Parâmetros:** `latitude=-23.55`, `longitude=-46.63`, `start_date=2026-09-01`, `end_date=2026-09-30`, `daily=temperature_2m_min,temperature_2m_max,precipitation_sum`, `timezone=America/Sao_Paulo`.
- **Data da coleta:** 26/11/2026 09:59, registrada automaticamente no JSON.
- **Arquivos gerados:** `dados/brutos/openmeteo_sao_paulo_sp_2026-09-01_2026-09-30.json`, que preserva a resposta original da API sem alterações, junto com os parâmetros e a data da coleta. Esse arquivo é a base para qualquer reprocessamento.

[INSERIR PRINT: terminal executando `python src/coleta.py`, mostrando "30 dias recebidos".]

# 3. Tratamento e qualidade dos dados

O script `src/banco.py` lê o JSON original e executa, com pandas:

1. **Padronização dos nomes:** `time` → `data`, `temperature_2m_min` → `temperatura_min`, `temperature_2m_max` → `temperatura_max`, `precipitation_sum` → `precipitacao`.
2. **Conversão de tipos:** datas com `pd.to_datetime` (formato AAAA-MM-DD, erros viram nulos e são detectados); variáveis com `pd.to_numeric`.
3. **Inclusão de identificação:** `cidade_id`, `cidade_nome`, latitude e longitude devolvidas pela API e `data_coleta`.
4. **Checagens de qualidade** antes da carga:

| # | Checagem | Tipo | Resultado |
|---|---|---|---|
| 1 | Duplicidade de (cidade_id, data) | Crítica | [OK] |
| 2 | Campos obrigatórios preenchidos | Crítica | [OK] |
| 3 | Datas válidas e dentro do recorte | Crítica | [OK] |
| 4 | Cobertura dos 30 dias consecutivos | Crítica | [OK: 30 de 30] |
| 5 | Ausências nas variáveis | Alerta | [OK: 0 dias sem dado] |
| 6 | Temperatura mínima ≤ máxima | Crítica | [OK] |
| 7 | Precipitação não negativa | Crítica | [OK] |
| 8 | Unidades compatíveis (°C, °C, mm) | Crítica | [OK] |
| 9 | Faixas plausíveis (-5 a 45 °C; até 200 mm) | Alerta | [OK] |

Falhas críticas cancelam a carga; alertas são registrados. **Valores ausentes não são trocados por zero:** ficam como nulos e são excluídos dos cálculos, porque "sem dado" não é o mesmo que "não choveu".

**Problemas encontrados e decisões:** nenhuma inconsistência encontrada. As 9 checagens do plano de qualidade passaram sem falhas nem alertas: os 30 dias do recorte vieram completos, sem duplicidade, sem valores ausentes e dentro das faixas plausíveis para São Paulo.

[INSERIR PRINT: saída das checagens no terminal ou do arquivo `relatorio_qualidade.md`.]

# 4. Armazenamento e análise inicial

**Tabela principal `clima_diario` (DuckDB):**

| Campo | Tipo | Significado |
|---|---|---|
| cidade_id (PK) | VARCHAR | Identificador da localidade |
| data (PK) | DATE | Dia do registro |
| cidade_nome | VARCHAR | Nome da localidade |
| latitude, longitude | DOUBLE | Ponto da grade usado pela API |
| temperatura_min | DOUBLE | Temperatura mínima do dia (°C) |
| temperatura_max | DOUBLE | Temperatura máxima do dia (°C) |
| precipitacao | DOUBLE | Chuva acumulada no dia (mm) |
| data_coleta | TIMESTAMP | Momento da coleta |

**Carga:** os dados validados são inseridos com `INSERT OR REPLACE`. Como a chave primária é (cidade_id, data), executar o processo de novo substitui os registros em vez de duplicá-los. Após duas execuções, a tabela mantém 30 registros.

[INSERIR PRINT: tabela carregada, por exemplo o resultado de `SELECT * FROM clima_diario LIMIT 10`.]

**Consultas SQL** (`sql/consultas.sql`):

```sql
-- P1: maior temperatura e dia
SELECT data, temperatura_max FROM clima_diario
WHERE temperatura_max IS NOT NULL
ORDER BY temperatura_max DESC LIMIT 1;

-- P2: dias mais chuvosos
SELECT data, precipitacao FROM clima_diario
WHERE precipitacao >= 1 ORDER BY precipitacao DESC LIMIT 5;

-- P3: dias de maior amplitude térmica
SELECT data, temperatura_min, temperatura_max,
       ROUND(temperatura_max - temperatura_min, 1) AS amplitude_c
FROM clima_diario
WHERE temperatura_min IS NOT NULL AND temperatura_max IS NOT NULL
ORDER BY amplitude_c DESC LIMIT 5;
```

**Resultados:**

- P1: a maior temperatura foi 32,0 °C, em 29/09/2026.
- P2: os dias mais chuvosos foram 12/09 (37,1 mm), 14/09 (27,1 mm), 10/09 (25,0 mm), 01/09 (22,7 mm) e 22/09 (19,8 mm).
- P3: a maior amplitude foi em 26/09, com 15,1 °C entre a mínima e a máxima. A amplitude média do mês foi 8,7 °C.

**Indicadores:**

| Indicador | Definição e cálculo | Unidade | Resultado | Interpretação |
|---|---|---|---|---|
| Média das máximas | `AVG(temperatura_max)` | °C | 23,3 | As tardes de setembro foram, em média, amenas, mas com dias de calor mais forte na última semana (máximas acima de 30 °C) |
| Precipitação total | `SUM(precipitacao)` | mm | 237,8 | Mês chuvoso, com chuva concentrada na primeira quinzena |
| Dias com chuva | `COUNT` de dias com `precipitacao >= 1` | dias | 16 de 30 | Em mais da metade dos dias (16 de 30) a chuva poderia afetar atividades ao ar livre |

[INSERIR PRINT: resultados das consultas (`resultados_consultas.md` ou terminal).]

**Avaliação preliminar dos critérios de sucesso da AE1:** [listar os critérios da AE1.] Já é possível verificar que os dados cobrem os 30 dias, que as três perguntas têm resposta e que os indicadores são calculáveis. Dependem das próximas etapas o painel em Streamlit e a validação com o público, ou seja, saber se as informações são compreensíveis e úteis para a escola.

# 5. Relevância extensionista e limitações

**Como apoia o público:** os resultados mostram quantos dias do mês tiveram chuva, como foram as temperaturas máximas e em quais dias a diferença entre manhã e tarde foi maior. Com isso, a escola pode discutir alternativas para aulas ao ar livre (horários, locais cobertos, hidratação e roupas em camadas) com base no que de fato aconteceu.

**Limitações:**

- **Fonte:** a Open-Meteo fornece estimativas de modelos e reanálises para um ponto da grade (aprox. -23,514938, -46,610504). **Não são medições diretas de uma estação local**, e podem diferir do que foi sentido na escola.
- **Período:** 30 dias são insuficientes para falar em tendência ou mudança climática e não representam outros meses.
- **Dados:** dias sem dado ficam ausentes e reduzem a precisão dos totais.
- **Histórico não é previsão:** a análise descreve o passado. Para decisões do dia a dia, a escola deve consultar a previsão oficial (INMET, Defesa Civil).

**Cuidados éticos:** o projeto não coleta dados pessoais. Na devolutiva, nomes, fotos e opiniões de participantes só serão registrados com autorização, de forma anônima quando possível, e nenhum dado sensível ou credencial é publicado no GitHub (o `.gitignore` exclui `.env` e o ambiente virtual).

# 6. Repositório e reprodução

Repositório: [inserir link do GitHub]. O professor tem acesso como colaborador.

Para reproduzir: criar o ambiente virtual, `pip install -r requirements.txt`, depois `python src/coleta.py`, `python src/banco.py` e, opcionalmente, `streamlit run src/app.py`. Os passos completos estão no README.
