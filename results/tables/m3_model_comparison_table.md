# M3 Publication-Style Regression Table

| Term | (1) Michigan only | (2) AAII only | (3) Both sentiment | (4) + SMB | (5) + HML | (6) + RMW | (7) + CMA | (8) Lagged factors | (9) Entity TWFE | (10) DiD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lagged Michigan sentiment | -0.000<br>(0.026) |  | 0.000<br>(0.027) | -0.001<br>(0.027) | -0.001<br>(0.027) | -0.007<br>(0.027) | -0.007<br>(0.027) | -0.007<br>(0.027) |  |  |
| Lagged AAII bull-bear spread |  | -0.001<br>(0.019) | -0.001<br>(0.020) | 0.001<br>(0.020) | 0.001<br>(0.020) | -0.000<br>(0.020) | 0.000<br>(0.020) | 0.000<br>(0.020) |  |  |
| SMB |  |  |  | -0.056<br>(0.118) | -0.048<br>(0.118) | -0.155<br>(0.134) | -0.152<br>(0.132) | -0.152<br>(0.132) |  |  |
| HML |  |  |  |  | -0.043<br>(0.125) | -0.031<br>(0.121) | -0.043<br>(0.163) | -0.043<br>(0.163) |  |  |
| RMW |  |  |  |  |  | -0.320*<br>(0.193) | -0.319*<br>(0.194) | -0.319*<br>(0.194) |  |  |
| CMA |  |  |  |  |  |  | 0.032<br>(0.229) | 0.032<br>(0.229) |  |  |
| Sentiment group |  |  |  |  |  |  |  |  | 0.056<br>(0.051) |  |
| Post-2008 shock |  |  |  |  |  |  |  |  | -0.532<br>(0.437) |  |
| Post-COVID shock |  |  |  |  |  |  |  |  | 0.015<br>(0.146) |  |
| Sentiment group x Post-2008 |  |  |  |  |  |  |  |  |  | 0.201<br>(0.346) |
| Sentiment group x Post-COVID |  |  |  |  |  |  |  |  |  | -0.529**<br>(0.263) |
| Month-of-year FE | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | No | No |
| Entity FE | No | No | No | No | No | No | No | No | Yes | Yes |
| Time FE | No | No | No | No | No | No | No | No | Yes | Yes |
| Factor timing | None | None | None | Lagged | Lagged | Lagged | Lagged | Lagged | NA | NA |
| SE type | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Robust (HC1) | Clustered by variable | Clustered by variable |
| Observations | 251 | 251 | 251 | 251 | 251 | 251 | 251 | 251 | 3024 | 3024 |
| R-squared | 0.040 | 0.040 | 0.040 | 0.041 | 0.041 | 0.055 | 0.055 | 0.055 | 0.100 | 0.111 |
| Notes | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. | Standard errors in parentheses. * p<0.10, ** p<0.05, *** p<0.01. |