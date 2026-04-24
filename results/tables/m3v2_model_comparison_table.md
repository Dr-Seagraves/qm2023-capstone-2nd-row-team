# M3v2 Publication-Style Regression Table

| Term | (1) OLS full period | (2) OLS COVID only | (3) FE TWFE | (4) DiD TWFE |
| --- | --- | --- | --- | --- |
| Lagged Michigan sentiment | 0.028<br>(0.036) | 0.077<br>(0.174) |  |  |
| Lagged sentiment x small-firm exposure |  |  | 0.211**<br>(0.104) | 0.200*<br>(0.103) |
| Lagged sentiment x small-firm x post-GFC |  |  |  | 0.049<br>(0.044) |
| Lagged sentiment x small-firm x post-COVID |  |  |  | 0.054<br>(0.077) |
| Log assets | -0.798***<br>(0.266) | -1.212<br>(0.953) | -1.770<br>(2.389) | -1.798<br>(2.366) |
| Leverage | -0.012<br>(0.009) | -0.020<br>(0.017) | -0.005<br>(0.007) | -0.006<br>(0.008) |
| Profitability | 0.002<br>(0.004) | 0.022<br>(0.020) | 0.022<br>(0.018) | 0.022<br>(0.018) |
| Capex intensity | 1.520<br>(1.720) | 28.561<br>(33.932) | 16.118<br>(15.063) | 16.198<br>(15.151) |
| Cash ratio | 2.321<br>(3.160) | 21.339<br>(21.132) | 8.001<br>(5.550) | 8.367<br>(5.807) |
| R&D intensity | -0.002<br>(0.007) | 0.011<br>(0.011) | 0.033<br>(0.031) | 0.033<br>(0.031) |
| Firm FE | No | No | Yes | Yes |
| Time FE | No | No | Yes | Yes |
| Industry FE | Yes | Yes | No | No |
| Clustered SE | Clustered by firm | Clustered by firm | Clustered by firm | Clustered by firm |
| Observations | 52302 | 3127 | 52302 | 52302 |
| R-squared | 0.001 | 0.002 | -0.011 | -0.013 |
| Notes | Direct sentiment coefficient | Pandemic subsample | Sentiment x small-firm exposure | Shock interactions with sentiment exposure |