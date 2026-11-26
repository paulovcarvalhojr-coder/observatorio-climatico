# Observatório Climático Local

Projeto Integrador Extensionista 2 · Prof. Luiz Henrique · Paulo [sobrenome]

## Objetivo e público-alvo

Transformar dados meteorológicos históricos em informações simples para a **comunidade escolar** (estudantes, professores de Educação Física e coordenação) de uma escola pública de São Paulo, que precisa planejar atividades ao ar livre considerando calor, variação de temperatura e chuva.

## Fonte, localidade, período e variáveis

- **Fonte:** [API histórica Open-Meteo](https://open-meteo.com/) (estimativas de modelo/reanálise, não estação local)
- **Localidade:** São Paulo - SP (lat. -23.55, long. -46.63)
- **Período:** 01/09/2026 a 30/09/2026 (30 dias consecutivos)
- **Variáveis:** temperatura mínima (°C), temperatura máxima (°C) e precipitação diária (mm)

**Perguntas:** (1) maior temperatura e dia; (2) dias mais chuvosos; (3) dias com maior amplitude térmica.
**Indicadores:** média das máximas (°C), precipitação total (mm), dias com chuva ≥ 1 mm.

## Estágio atual

- [x] Desenho da solução (AE2-2): dicionário, modelo lógico, plano de qualidade, wireframe
- [x] Coleta, tratamento, validação e carga no DuckDB
- [x] Consultas SQL e indicadores
- [x] Painel Streamlit (versão inicial)
- [ ] Devolutiva à comunidade
- [ ] Relatório final

## Estrutura dos arquivos

```
├── README.md
├── requirements.txt
├── .gitignore
├── dados/
│   ├── brutos/        # resposta original da API em JSON (gerada pela coleta)
│   └── processados/   # CSV tratado, banco DuckDB, relatórios de qualidade e resultados
├── src/
│   ├── config.py      # localidade, período, variáveis e limites de validação
│   ├── coleta.py      # coleta na API e preservação do JSON original
│   ├── banco.py       # tratamento, checagens de qualidade, carga e consultas
│   └── app.py         # painel Streamlit
├── sql/
│   └── consultas.sql  # perguntas analíticas e indicadores
└── docs/
    ├── escopo-1/AE2/    # relatório técnico da implementação
    ├── escopo-1/AE2-2/  # desenho da solução, diagramas, wireframe e issues
    ├── devolutiva.md
    └── relatorio_modelo.md
```

## Preparação do ambiente

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ordem de execução

```bash
python src/coleta.py      # 1. baixa os dados e salva o JSON em dados/brutos/
python src/banco.py       # 2. trata, valida, carrega no DuckDB e roda as consultas
streamlit run src/app.py  # 3. abre o painel no navegador
```

## Banco de dados

O banco `dados/processados/observatorio.duckdb` não vai para o GitHub: ele é recriado com `python src/banco.py`. A tabela `clima_diario` tem chave primária (`cidade_id`, `data`) e a carga usa `INSERT OR REPLACE`, então rodar de novo não duplica registros.

Para consultar direto em Python:

```python
import duckdb
con = duckdb.connect("dados/processados/observatorio.duckdb")
con.sql("SELECT * FROM clima_diario").show()
```

Após `banco.py`, também ficam disponíveis:
- `dados/processados/relatorio_qualidade.md`: resultado das 9 checagens
- `dados/processados/resultados_consultas.md`: respostas e indicadores

Para mudar localidade ou período, edite `src/config.py` e rode os passos de novo.

## Principais limitações

- Dados históricos: descrevem o passado e **não são previsão**.
- Estimativas da Open-Meteo para um ponto da grade, **não medições de estação local**.
- Apenas 30 dias: não permite falar em tendência climática.
- Dias sem dado ficam ausentes (não são tratados como zero).
