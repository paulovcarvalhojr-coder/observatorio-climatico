-- Consultas analíticas sobre a tabela clima_diario.
-- Cada consulta começa com "-- name:" para ser usada por banco.py e app.py.
-- Valores ausentes (NULL) são ignorados por AVG, SUM, MAX e MIN.

-- ===== Perguntas analíticas =====

-- name: p1_temperatura_maxima
-- P1: qual foi a maior temperatura do período e em qual dia ocorreu?
SELECT data, temperatura_max AS temperatura_max_c
FROM clima_diario
WHERE temperatura_max IS NOT NULL
ORDER BY temperatura_max DESC
LIMIT 1;

-- name: p2_dias_mais_chuvosos
-- P2: quais foram os dias mais chuvosos (até 5 dias com pelo menos 1 mm)?
SELECT data, precipitacao AS precipitacao_mm
FROM clima_diario
WHERE precipitacao >= 1
ORDER BY precipitacao DESC
LIMIT 5;

-- name: p3_amplitude_termica
-- P3: quais dias tiveram a maior diferença entre a mínima e a máxima?
SELECT data, temperatura_min AS min_c, temperatura_max AS max_c,
       ROUND(temperatura_max - temperatura_min, 1) AS amplitude_c
FROM clima_diario
WHERE temperatura_min IS NOT NULL AND temperatura_max IS NOT NULL
ORDER BY amplitude_c DESC
LIMIT 5;

-- ===== Indicadores (KPIs) =====

-- name: kpis
SELECT
    ROUND(AVG(temperatura_max), 1)                    AS kpi1_media_max_c,
    ROUND(SUM(precipitacao), 1)                       AS kpi2_precipitacao_total_mm,
    COUNT(*) FILTER (WHERE precipitacao >= 1)         AS kpi3_dias_com_chuva,
    ROUND(AVG(temperatura_max - temperatura_min), 1)  AS amplitude_media_c,
    COUNT(*) FILTER (WHERE precipitacao IS NULL)      AS dias_sem_dado_chuva
FROM clima_diario;

-- ===== Tabela para os gráficos e a consulta dos registros =====

-- name: registros
SELECT data, temperatura_min, temperatura_max, precipitacao
FROM clima_diario
ORDER BY data;
