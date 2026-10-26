|   Step | Added feature                                                  | Kind    |   n_features |   Train RMSE |   Test RMSE | Test RMSE < baseline   |
|-------:|:---------------------------------------------------------------|:--------|-------------:|-------------:|------------:|:-----------------------|
|      1 | Dissolution pressure [MPa] * Flow speed (oxygen) [mL/min]      | product |            1 |      0.82487 |     0.90423 | False                  |
|      2 | (Flow speed (oxygen) [mL/min]) / (Discharge tube [m])          | ratio   |            2 |      0.71750 |     0.90868 | False                  |
|      3 | (Flow speed (water) [mL/min]) / (Dissolution pressure [MPa])   | ratio   |            3 |      0.71460 |     0.91173 | False                  |
|      4 | Discharge tube [m] * Water volume [mL]                         | product |            4 |      0.61875 |     0.84424 | True                   |
|      5 | Discharge tube [m] * Flow speed (oxygen) [mL/min]              | product |            5 |      0.61881 |     0.87310 | True                   |
|      6 | (Dissolve tube [m]) / (Flow speed (oxygen) [mL/min])           | ratio   |            6 |      0.61485 |     0.87984 | True                   |
|      7 | (Flow speed (water) [mL/min]) / (Flow speed (oxygen) [mL/min]) | ratio   |            7 |      0.61471 |     0.87831 | True                   |
|      8 | (Flow speed (water) [mL/min]) / (Dissolve tube [m])            | ratio   |            8 |      0.61341 |     0.88104 | True                   |
|      9 | (Water volume [mL]) / (Flow speed (water) [mL/min])            | ratio   |            9 |      0.61224 |     0.87934 | True                   |
|     10 | (Discharge tube [m]) / (Flow speed (oxygen) [mL/min])          | ratio   |           10 |      0.61237 |     0.87718 | True                   |
|     11 | Water volume [mL]                                              | base    |           11 |      0.61209 |     0.87932 | True                   |
|     12 | Dissolution pressure [MPa]                                     | base    |           12 |      0.61172 |     0.87925 | True                   |
|     13 | (Dissolution pressure [MPa]) / (Water volume [mL])             | ratio   |           13 |      0.61421 |     0.86980 | True                   |
|     14 | (Dissolution pressure [MPa]) / (Dissolve tube [m])             | ratio   |           14 |      0.61409 |     0.87978 | True                   |
|     15 | (Flow speed (water) [mL/min]) / (Discharge tube [m])           | ratio   |           15 |      0.61424 |     0.88935 | False                  |