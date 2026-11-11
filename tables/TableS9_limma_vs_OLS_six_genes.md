**TableS9 limma vs OLS six genes**

Same probe-selection convention (smallest nominal p in the primary OLS) for both engines. BH across all probes on each platform.

| platform_dataset   | gene   |   n_probes | probe                      |     log2FC |         p_ols |      q_ols |       p_limma |    q_limma |   t_limma | sig_ols   | sig_limma   | status           |
|:-------------------|:-------|-----------:|:---------------------------|-----------:|--------------:|-----------:|--------------:|-----------:|----------:|:----------|:------------|:-----------------|
| GSE2378-GPL8300    | FGFR1  |          4 | 2056_at                    |   0.728934 |   0.00844111  |   0.353523 |   0.00893265  |   0.428801 |   3.05993 | False     | False       | OK               |
| GSE2378-GPL8300    | SMAD1  |          2 | 37280_at                   |   0.844961 |   0.00312214  |   0.290426 |   0.00321154  |   0.340775 |   3.58698 | False     | False       | OK               |
| GSE2378-GPL8300    | STAT1  |          8 | 33338_at                   |  -0.821042 |   0.0143424   |   0.433189 |   0.0121166   |   0.463014 |  -2.90272 | False     | False       | OK               |
| GSE2378-GPL8300    | TGFBR2 |          2 | 1815_g_at                  |   0.602682 |   0.000903491 |   0.227098 |   0.0033827   |   0.341406 |   3.56014 | False     | False       | OK               |
| GSE2378-GPL8300    | CASP1  |          2 | 39320_at                   |   1.92103  |   0.000737361 |   0.224052 |   0.000298389 |   0.194295 |   4.85046 | False     | False       | OK               |
| GSE2378-GPL8300    | CASP4  |          1 | 195_s_at                   |   0.783519 |   0.00305743  |   0.290226 |   0.00362354  |   0.346569 |   3.52461 | False     | False       | OK               |
| GSE45570           | FGFR1  |          0 |                            | nan        | nan           | nan        | nan           | nan        | nan       | False     | False       | probe not mapped |
| GSE45570           | SMAD1  |          0 |                            | nan        | nan           | nan        | nan           | nan        | nan       | False     | False       | probe not mapped |
| GSE45570           | STAT1  |          0 |                            | nan        | nan           | nan        | nan           | nan        | nan       | False     | False       | probe not mapped |
| GSE45570           | TGFBR2 |          0 |                            | nan        | nan           | nan        | nan           | nan        | nan       | False     | False       | probe not mapped |
| GSE45570           | CASP1  |          0 |                            | nan        | nan           | nan        | nan           | nan        | nan       | False     | False       | probe not mapped |
| GSE45570           | CASP4  |          0 |                            | nan        | nan           | nan        | nan           | nan        | nan       | False     | False       | probe not mapped |
| GSE9944-GPL571     | FGFR1  |          6 | 207937_x_at                |  -0.444689 |   0.0430668   |   0.237658 |   0.0344996   |   0.211372 |  -2.26677 | False     | False       | OK               |
| GSE9944-GPL571     | SMAD1  |          2 | 210993_s_at                |   0.8784   |   0.0535564   |   0.266847 |   0.0410645   |   0.232772 |   2.18186 | False     | False       | OK               |
| GSE9944-GPL571     | STAT1  |          6 | AFFX-HUMISGF3A/M97935_5_at |  -1.13191  |   0.028892    |   0.191214 |   0.0206529   |   0.159715 |  -2.51028 | False     | False       | OK               |
| GSE9944-GPL571     | TGFBR2 |          2 | 208944_at                  |   0.405278 |   0.22173     |   0.543582 |   0.19747     |   0.515171 |   1.33257 | False     | False       | OK               |
| GSE9944-GPL571     | CASP1  |          5 | 211367_s_at                |   1.07514  |   0.0179116   |   0.145467 |   0.0122364   |   0.116094 |   2.75066 | False     | False       | OK               |
| GSE9944-GPL571     | CASP4  |          2 | 209310_s_at                |   0.668978 |   0.0234626   |   0.170232 |   0.0170759   |   0.142153 |   2.59844 | False     | False       | OK               |
| GSE9944-GPL8300    | FGFR1  |          4 | 424_s_at                   |   0.440143 |   0.0312893   |   0.575541 |   0.021675    |   0.515293 |   2.54804 | False     | False       | OK               |
| GSE9944-GPL8300    | SMAD1  |          2 | 37280_at                   |   0.457574 |   0.0612305   |   0.679141 |   0.0437187   |   0.641389 |   2.19253 | False     | False       | OK               |
| GSE9944-GPL8300    | STAT1  |          8 | 32859_at                   |  -0.968248 |   0.00542342  |   0.42829  |   0.00242783  |   0.317887 |  -3.60462 | False     | False       | OK               |
| GSE9944-GPL8300    | TGFBR2 |          2 | 1815_g_at                  |   0.483707 |   0.0696043   |   0.691063 |   0.0496963   |   0.66332  |   2.1258  | False     | False       | OK               |
| GSE9944-GPL8300    | CASP1  |          2 | 574_s_at                   |   0.46675  |   0.00243169  |   0.355864 |   0.00165238  |   0.278132 |   3.78817 | False     | False       | OK               |
| GSE9944-GPL8300    | CASP4  |          1 | 195_s_at                   |   0.740171 |   0.0228196   |   0.542717 |   0.0131939   |   0.458109 |   2.79225 | False     | False       | OK               |
