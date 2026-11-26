# Relatório de qualidade dos dados

Registros tratados: 30

| Checagem | Resultado | Detalhe | Crítica |
|---|---|---|---|
| 1. Duplicidade (cidade_id, data) | OK | 0 registros duplicados | sim |
| 2. Campos obrigatórios preenchidos | OK | 0 vazios | sim |
| 3. Datas válidas e dentro do recorte | OK | 0 datas inválidas ou fora de 2026-09-01 a 2026-09-30 | sim |
| 4. Cobertura dos 30 dias consecutivos | OK | 30 de 30 dias; faltando: nenhum | sim |
| 5. Ausências nas variáveis | OK | temperatura_min: 0, temperatura_max: 0, precipitacao: 0 (mantidos como ausentes) | não |
| 6. Temperatura mínima <= máxima | OK | 0 dias com mínima maior que máxima | sim |
| 7. Precipitação não negativa | OK | 0 valores negativos | sim |
| 8. Unidades compatíveis com o dicionário | OK | divergentes: nenhuma | sim |
| 9. Faixas plausíveis | OK | 0 temperaturas fora de -5.0 a 45.0 °C; 0 precipitações acima de 200.0 mm | não |
