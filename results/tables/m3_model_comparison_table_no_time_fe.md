# M3 Publication-Style Regression Table

| Term | (1) Michigan only | (2) AAII only | (3) Both sentiment | (4) + SMB | (5) + HML | (6) + RMW | (7) + CMA | (8) Lagged factors | (9) Entity FE, no time FE | (10) DiD, no time FE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lagged Michigan sentiment | -0.000<br>(0.026) |  | 0.000<br>(0.027) | -0.001<br>(0.027) | -0.001<br>(0.027) | -0.006<br>(0.027) | -0.005<br>(0.027) | -0.005<br>(0.027) |  |  |
| Lagged AAII bull-bear spread |  | -0.001<br>(0.018) | -0.001<br>(0.018) | 0.001<br>(0.019) | 0.002<br>(0.018) | 0.001<br>(0.018) | 0.001<br>(0.018) | 0.001<br>(0.018) |  |  |
| SMB |  |  |  | -0.042<br>(0.115) | -0.035<br>(0.115) | -0.114<br>(0.133) | -0.109<br>(0.130) | -0.109<br>(0.130) |  |  |
| HML |  |  |  |  | -0.056<br>(0.124) | -0.049<br>(0.122) | -0.071<br>(0.167) | -0.071<br>(0.167) |  |  |
| RMW |  |  |  |  |  | -0.240<br>(0.187) | -0.239<br>(0.187) | -0.239<br>(0.187) |  |  |
| CMA |  |  |  |  |  |  | 0.063<br>(0.225) | 0.063<br>(0.225) |  |  |
| Sentiment group |  |  |  |  |  |  |  |  | 0.010<br>(0.012) |  |
| Post-2008 shock |  |  |  |  |  |  |  |  | -0.125<br>(0.164) |  |
| Post-COVID shock |  |  |  |  |  |  |  |  | 0.019<br>(0.142) |  |
| Sentiment group x Post-2008 |  |  |  |  |  |  |  |  |  | -0.008<br>(0.261) |
| Sentiment group x Post-COVID |  |  |  |  |  |  |  |  |  | -0.289<br>(0.215) |
| Month-of-year FE | No | No | No | No | No | No | No | No | No | No |
| Entity FE | No | No | No | No | No | No | No | No | Yes | Yes |
| Time FE | No | No | No | No | No | No | No | No | No | No |
| Factor timing | None | None | None | Lagged | Lagged | Lagged | Lagged | Lagged | NA | NA |
| SE type | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Clustered by variable | Clustered by variable |
| Observations | 251 | 251 | 251 | 251 | 251 | 251 | 251 | 251 | 3024 | 3024 |
| R-squared | 0.000 | 0.000 | 0.000 | 0.001 | 0.002 | 0.010 | 0.011 | 0.011 | 0.003 | 0.006 |
| Notes | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. |