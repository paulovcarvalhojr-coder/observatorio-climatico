# Issues para o GitHub

Copie cada bloco como uma issue nova (título + descrição). Responsável: Paulo.

---

## 1. Implementar a coleta pela API

**Descrição:** criar `src/coleta.py` usando Requests para chamar a API histórica Open-Meteo com latitude, longitude, período (01/09/2026 a 30/09/2026), variáveis `temperature_2m_min`, `temperature_2m_max`, `precipitation_sum` e fuso `America/Sao_Paulo`.

**Critério de conclusão:** o script roda sem erro e informa que recebeu 30 dias.

---

## 2. Preservar a resposta original em JSON

**Descrição:** salvar a resposta da API sem alterações em `dados/brutos/`, junto com os parâmetros usados e a data e hora da coleta.

**Critério de conclusão:** o arquivo JSON existe, abre corretamente e contém `metadados` e `resposta_api`.

---

## 3. Implementar o tratamento e as checagens de qualidade

**Descrição:** em `src/banco.py`, converter o JSON em DataFrame, padronizar nomes e tipos e executar as 9 checagens do plano de qualidade (AE2-2, seção 3). Valores ausentes não podem ser trocados por zero.

**Critério de conclusão:** `dados/processados/relatorio_qualidade.md` é gerado com o resultado de cada checagem, e falhas críticas cancelam a carga.

---

## 4. Criar a tabela e a carga no DuckDB

**Descrição:** criar a tabela `clima_diario` com PK (`cidade_id`, `data`) e carregar os dados tratados com `INSERT OR REPLACE`.

**Critério de conclusão:** depois de rodar `python src/banco.py` duas vezes, `SELECT COUNT(*) FROM clima_diario` continua retornando 30.

---

## 5. Implementar as consultas e os indicadores

**Descrição:** escrever em `sql/consultas.sql` as consultas das perguntas P1, P2 e P3 e dos KPIs (média das máximas, precipitação total, dias com chuva).

**Critério de conclusão:** as consultas rodam no DuckDB e os resultados são salvos em `dados/processados/resultados_consultas.md`.

---

## 6. Construir o dashboard em Streamlit

**Descrição:** criar `src/app.py` seguindo o wireframe: título, localidade e período, fonte, 3 KPIs, 2 gráficos, respostas às perguntas, tabela de registros e quadro de limitações.

**Critério de conclusão:** `streamlit run src/app.py` abre o painel com todos os elementos do wireframe.

---

## 7. Revisar a documentação e preparar a devolutiva

**Descrição:** atualizar o README (objetivo, público, execução, limitações) e preparar o roteiro da apresentação para a comunidade escolar (`docs/devolutiva.md`).

**Critério de conclusão:** outra pessoa consegue rodar o projeto só lendo o README, e o roteiro da devolutiva está pronto.
