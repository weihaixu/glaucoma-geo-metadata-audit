# Re-analysis run report

## QC / design

| platform_dataset   |   n_arrays |   n_probes |   n_donors | scale                                                                   | log2_applied   | groups                         | races                                    |   race_known |   group_known | race_x_group                                                                                    |   n_glaucoma_donors |   n_control_donors | design_warning                                                                                                                                                                           | pca_array_pc1_3          | pca_donor_pc1_3          | adjustment_terms                            | model_status                                          |   M0_significant_probes |   M0_sig_still_q05_M2 |   M0_sig_direction_flipped_in_M2 | annotation_file           |   n_probes_mapped | scale_used   | scale_evidence                                                                            |   n_arrays_total_incl_OHT |   n_arrays_used_case_control |
|:-------------------|-----------:|-----------:|-----------:|:------------------------------------------------------------------------|:---------------|:-------------------------------|:-----------------------------------------|-------------:|--------------:|:------------------------------------------------------------------------------------------------|--------------------:|-------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------|:-------------------------|:--------------------------------------------|:------------------------------------------------------|------------------------:|----------------------:|---------------------------------:|:--------------------------|------------------:|:-------------|:------------------------------------------------------------------------------------------|--------------------------:|-----------------------------:|
| GSE2378-GPL8300    |         13 |      12625 |         13 | linear intensity -> log2 applied [observed range 0.02..62255.27]        | True           | {"glaucoma": 7, "control": 6}  | {"UNKNOWN": 13}                          |            0 |            13 | {"UNKNOWN": {"control": 6, "glaucoma": 7}}                                                      |                   7 |                  6 | none detected                                                                                                                                                                            | [0.3842, 0.1273, 0.0614] | [0.3842, 0.1273, 0.0614] | REJECTED (race unavailable)                 | PARTIAL: covariate-adjusted model could not be fitted |                     748 |                     2 |                                0 | GPL8300.annot.gz          |             12181 | linear       | linear MAS5-like intensities, no RMA statement; max 62255.3, median 149.1 -> log2 applied |                        13 |                           13 |
| GSE2378-GPL91      |          2 |      12626 |          2 | linear intensity -> log2 applied [observed range 0.02..13219.51]        | True           | {"glaucoma": 1, "control": 1}  | {"UNKNOWN": 2}                           |            0 |             2 | {"UNKNOWN": {"control": 1, "glaucoma": 1}}                                                      |                   1 |                  1 | only 1 glaucoma / 1 control donors - underpowered                                                                                                                                        | [1.0, 0.0]               | [1.0, 0.0]               | nan                                         | SKIPPED: only 2 labelled donors (>=4 required)        |                     nan |                   nan |                              nan | GPL91.annot.gz            |                 0 | linear       | linear MAS5-like intensities, no RMA statement; max 13219.5, median 171.2 -> log2 applied |                         2 |                            2 |
| GSE45570           |         12 |      22011 |         12 | ASSUMED already log2 (author must confirm) [observed range 1.73..13.98] | False          | {"glaucoma": 6, "control": 6}  | {"UNKNOWN": 12}                          |            0 |            12 | {"UNKNOWN": {"control": 6, "glaucoma": 6}}                                                      |                   6 |                  6 | none detected                                                                                                                                                                            | [0.3662, 0.1136, 0.1092] | [0.3662, 0.1136, 0.1092] | REJECTED (race unavailable)                 | PARTIAL: covariate-adjusted model could not be fitted |                      89 |                     0 |                                0 | MISSING - no gene symbols |                 0 | log2         | GEO !Sample_data_processing states RMA/log2; observed range 1.73..13.98, median 6.37      |                        18 |                           12 |
| GSE9944-GPL571     |         42 |      22277 |         21 | ASSUMED already log2 (author must confirm) [observed range 2.24..13.77] | False          | {"control": 18, "glaucoma": 3} | {"African_American": 12, "Caucasian": 9} |           21 |            21 | {"African_American": {"control": 9, "glaucoma": 3}, "Caucasian": {"control": 9, "glaucoma": 0}} |                   3 |                 18 | only 3 glaucoma / 18 control donors - underpowered; ALL glaucoma donors share one ancestry: race and disease are nearly collinear; the adjusted disease coefficient is not interpretable | [0.3028, 0.109, 0.0699]  | [0.3322, 0.119, 0.0767]  | intercept,glaucoma,race_Caucasian,age_z,sex | OK                                                    |                    1375 |                   454 |                                0 | GPL571.annot.gz           |             21154 | log2         | GEO !Sample_data_processing states RMA/log2; observed range 2.24..13.77, median 5.33      |                        42 |                           42 |
| GSE9944-GPL8300    |         19 |      12600 |         16 | ASSUMED already log2 (author must confirm) [observed range 4.77..14.62] | False          | {"glaucoma": 10, "control": 6} | {"Caucasian": 13, "African_American": 3} |           16 |            16 | {"African_American": {"control": 0, "glaucoma": 3}, "Caucasian": {"control": 6, "glaucoma": 7}} |                  10 |                  6 | none detected                                                                                                                                                                            | [0.4264, 0.1431, 0.1345] | [0.4712, 0.1475, 0.1121] | intercept,glaucoma,race_Caucasian,age_z,sex | OK                                                    |                     472 |                     0 |                               67 | GPL8300.annot.gz          |             12156 | log2         | GEO !Sample_data_processing states RMA/log2; observed range 4.77..14.62, median 9.34      |                        19 |                           19 |
| GSE9944-GPL91      |          2 |      12600 |          2 | ASSUMED already log2 (author must confirm) [observed range 4.88..14.22] | False          | {"glaucoma": 1, "control": 1}  | {"Caucasian": 2}                         |            2 |             2 | {"Caucasian": {"control": 1, "glaucoma": 1}}                                                    |                   1 |                  1 | only 1 glaucoma / 1 control donors - underpowered; ALL glaucoma donors share one ancestry: race and disease are nearly collinear; the adjusted disease coefficient is not interpretable  | [1.0, 0.0]               | [1.0, 0.0]               | nan                                         | SKIPPED: only 2 labelled donors (>=4 required)        |                     nan |                   nan |                              nan | GPL91.annot.gz            |                 0 | log2         | GEO !Sample_data_processing states RMA/log2; observed range 4.88..14.22, median 9.38      |                         2 |                            2 |

## Scale decisions (must be confirmed in Methods)

- **GSE2378-GPL8300**: `linear` — linear MAS5-like intensities, no RMA statement; max 62255.3, median 149.1 -> log2 applied; annotation: GPL8300.annot.gz
- **GSE2378-GPL91**: `linear` — linear MAS5-like intensities, no RMA statement; max 13219.5, median 171.2 -> log2 applied; annotation: GPL91.annot.gz
- **GSE45570**: `log2` — GEO !Sample_data_processing states RMA/log2; observed range 1.73..13.98, median 6.37; annotation: MISSING - no gene symbols
- **GSE9944-GPL571**: `log2` — GEO !Sample_data_processing states RMA/log2; observed range 2.24..13.77, median 5.33; annotation: GPL571.annot.gz
- **GSE9944-GPL8300**: `log2` — GEO !Sample_data_processing states RMA/log2; observed range 4.77..14.62, median 9.34; annotation: GPL8300.annot.gz
- **GSE9944-GPL91**: `log2` — GEO !Sample_data_processing states RMA/log2; observed range 4.88..14.22, median 9.38; annotation: GPL91.annot.gz

## Donor overlap (10_donor_overlap.csv)

| dataset_A       | dataset_B       |   donors_A |   donors_B |   shared_donor_ids | shared_list                        | interpretation                                                                                      |
|:----------------|:----------------|-----------:|-----------:|-------------------:|:-----------------------------------|:----------------------------------------------------------------------------------------------------|
| GSE2378-GPL8300 | GSE2378-GPL91   |         13 |          2 |                  0 |                                    | SAME GEO SERIES but no shared donor IDs in titles - still one experiment, not an independent cohort |
| GSE2378-GPL8300 | GSE45570        |         13 |         12 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL8300 | GSE9944-GPL571  |         13 |         21 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL8300 | GSE9944-GPL8300 |         13 |         16 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL8300 | GSE9944-GPL91   |         13 |          2 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL91   | GSE45570        |          2 |         12 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL91   | GSE9944-GPL571  |          2 |         21 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL91   | GSE9944-GPL8300 |          2 |         16 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE2378-GPL91   | GSE9944-GPL91   |          2 |          2 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE45570        | GSE9944-GPL571  |         12 |         21 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE45570        | GSE9944-GPL8300 |         12 |         16 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE45570        | GSE9944-GPL91   |         12 |          2 |                  0 |                                    | DIFFERENT SERIES - verify donor provenance before claiming independence                             |
| GSE9944-GPL571  | GSE9944-GPL8300 |         21 |         16 |                  5 | 03-11R;03-13L;04-20L;04-24R;05-16L | SAME GEO SERIES - overlapping donors / arrays are technical replication, NOT independent validation |
| GSE9944-GPL571  | GSE9944-GPL91   |         21 |          2 |                  0 |                                    | SAME GEO SERIES but no shared donor IDs in titles - still one experiment, not an independent cohort |
| GSE9944-GPL8300 | GSE9944-GPL91   |         16 |          2 |                  0 |                                    | SAME GEO SERIES but no shared donor IDs in titles - still one experiment, not an independent cohort |

## DEG counts by model

| platform_dataset   | model                       |   alpha |   abs_log2FC_min | use_BH_q   |   n_DE_probes |   n_probe_tested |   df_residual | note                                                  |
|:-------------------|:----------------------------|--------:|-----------------:|:-----------|--------------:|-----------------:|--------------:|:------------------------------------------------------|
| GSE2378-GPL8300    | M0_array_nominal            |    0.05 |              0.5 | False      |           748 |            12625 |            11 |                                                       |
| GSE2378-GPL8300    | M1_donor_nominal            |    0.05 |              0.5 | False      |           748 |            12625 |            11 |                                                       |
| GSE2378-GPL8300    | M2_donor_adjusted_FDR_LFC1  |    0.05 |              1   | True       |             1 |            12625 |            11 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE2378-GPL8300    | M3_donor_adjusted_FDR_LFC05 |    0.05 |              0.5 | True       |             2 |            12625 |            11 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE45570           | M0_array_nominal            |    0.05 |              0.5 | False      |            89 |            22011 |            10 |                                                       |
| GSE45570           | M1_donor_nominal            |    0.05 |              0.5 | False      |            89 |            22011 |            10 |                                                       |
| GSE45570           | M2_donor_adjusted_FDR_LFC1  |    0.05 |              1   | True       |             0 |            22011 |            10 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE45570           | M3_donor_adjusted_FDR_LFC05 |    0.05 |              0.5 | True       |             0 |            22011 |            10 | ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata |
| GSE9944-GPL571     | M0_array_nominal            |    0.05 |              0.5 | False      |          1375 |            22277 |            40 |                                                       |
| GSE9944-GPL571     | M1_donor_nominal            |    0.05 |              0.5 | False      |          1075 |            22277 |            19 |                                                       |
| GSE9944-GPL571     | M2_donor_adjusted_FDR_LFC1  |    0.05 |              1   | True       |            95 |            22277 |            16 |                                                       |
| GSE9944-GPL571     | M3_donor_adjusted_FDR_LFC05 |    0.05 |              0.5 | True       |           516 |            22277 |            16 |                                                       |
| GSE9944-GPL8300    | M0_array_nominal            |    0.05 |              0.5 | False      |           472 |            12600 |            17 |                                                       |
| GSE9944-GPL8300    | M1_donor_nominal            |    0.05 |              0.5 | False      |           337 |            12600 |            14 |                                                       |
| GSE9944-GPL8300    | M2_donor_adjusted_FDR_LFC1  |    0.05 |              1   | True       |             0 |            12600 |            11 |                                                       |
| GSE9944-GPL8300    | M3_donor_adjusted_FDR_LFC05 |    0.05 |              0.5 | True       |             0 |            12600 |            11 |                                                       |

## Six key genes

| model                                       | gene   |   n_probes |      log2FC |             p |         q_BH | status                      |
|:--------------------------------------------|:-------|-----------:|------------:|--------------:|-------------:|:----------------------------|
| GSE2378-GPL8300|M0_array_nominal            | FGFR1  |          4 |   0.728934  |   0.00844111  |   0.353523   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M0_array_nominal            | SMAD1  |          2 |   0.844961  |   0.00312214  |   0.290426   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M0_array_nominal            | STAT1  |          8 |  -0.821042  |   0.0143424   |   0.433189   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M0_array_nominal            | TGFBR2 |          2 |   0.602682  |   0.000903491 |   0.227098   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M0_array_nominal            | CASP1  |          2 |   1.92103   |   0.000737361 |   0.224052   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M0_array_nominal            | CASP4  |          1 |   0.783519  |   0.00305743  |   0.290226   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M1_donor_nominal            | FGFR1  |          4 |   0.728934  |   0.00844111  |   0.353523   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M1_donor_nominal            | SMAD1  |          2 |   0.844961  |   0.00312214  |   0.290426   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M1_donor_nominal            | STAT1  |          8 |  -0.821042  |   0.0143424   |   0.433189   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M1_donor_nominal            | TGFBR2 |          2 |   0.602682  |   0.000903491 |   0.227098   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M1_donor_nominal            | CASP1  |          2 |   1.92103   |   0.000737361 |   0.224052   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M1_donor_nominal            | CASP4  |          1 |   0.783519  |   0.00305743  |   0.290226   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M2_donor_adjusted_FDR_LFC1  | FGFR1  |          4 |   0.728934  |   0.00844111  |   0.353523   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M2_donor_adjusted_FDR_LFC1  | SMAD1  |          2 |   0.844961  |   0.00312214  |   0.290426   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M2_donor_adjusted_FDR_LFC1  | STAT1  |          8 |  -0.821042  |   0.0143424   |   0.433189   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M2_donor_adjusted_FDR_LFC1  | TGFBR2 |          2 |   0.602682  |   0.000903491 |   0.227098   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M2_donor_adjusted_FDR_LFC1  | CASP1  |          2 |   1.92103   |   0.000737361 |   0.224052   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M2_donor_adjusted_FDR_LFC1  | CASP4  |          1 |   0.783519  |   0.00305743  |   0.290226   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M3_donor_adjusted_FDR_LFC05 | FGFR1  |          4 |   0.728934  |   0.00844111  |   0.353523   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M3_donor_adjusted_FDR_LFC05 | SMAD1  |          2 |   0.844961  |   0.00312214  |   0.290426   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M3_donor_adjusted_FDR_LFC05 | STAT1  |          8 |  -0.821042  |   0.0143424   |   0.433189   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M3_donor_adjusted_FDR_LFC05 | TGFBR2 |          2 |   0.602682  |   0.000903491 |   0.227098   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M3_donor_adjusted_FDR_LFC05 | CASP1  |          2 |   1.92103   |   0.000737361 |   0.224052   | not significant (BH q>=.05) |
| GSE2378-GPL8300|M3_donor_adjusted_FDR_LFC05 | CASP4  |          1 |   0.783519  |   0.00305743  |   0.290226   | not significant (BH q>=.05) |
| GSE45570|M0_array_nominal                   | FGFR1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M0_array_nominal                   | SMAD1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M0_array_nominal                   | STAT1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M0_array_nominal                   | TGFBR2 |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M0_array_nominal                   | CASP1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M0_array_nominal                   | CASP4  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M1_donor_nominal                   | FGFR1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M1_donor_nominal                   | SMAD1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M1_donor_nominal                   | STAT1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M1_donor_nominal                   | TGFBR2 |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M1_donor_nominal                   | CASP1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M1_donor_nominal                   | CASP4  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M2_donor_adjusted_FDR_LFC1         | FGFR1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M2_donor_adjusted_FDR_LFC1         | SMAD1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M2_donor_adjusted_FDR_LFC1         | STAT1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M2_donor_adjusted_FDR_LFC1         | TGFBR2 |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M2_donor_adjusted_FDR_LFC1         | CASP1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M2_donor_adjusted_FDR_LFC1         | CASP4  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M3_donor_adjusted_FDR_LFC05        | FGFR1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M3_donor_adjusted_FDR_LFC05        | SMAD1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M3_donor_adjusted_FDR_LFC05        | STAT1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M3_donor_adjusted_FDR_LFC05        | TGFBR2 |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M3_donor_adjusted_FDR_LFC05        | CASP1  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE45570|M3_donor_adjusted_FDR_LFC05        | CASP4  |          0 | nan         | nan           | nan          | no probe mapped             |
| GSE9944-GPL571|M0_array_nominal             | FGFR1  |          6 |  -0.676617  |   0.0244367   |   0.102829   | not significant (BH q>=.05) |
| GSE9944-GPL571|M0_array_nominal             | SMAD1  |          2 |   0.964819  |   0.00120089  |   0.0114082  | significant                 |
| GSE9944-GPL571|M0_array_nominal             | STAT1  |          6 |  -1.16297   |   0.000914164 |   0.00931177 | significant                 |
| GSE9944-GPL571|M0_array_nominal             | TGFBR2 |          2 |   0.512075  |   0.0189381   |   0.086275   | not significant (BH q>=.05) |
| GSE9944-GPL571|M0_array_nominal             | CASP1  |          5 |   1.14971   |   0.000120041 |   0.00191148 | significant                 |
| GSE9944-GPL571|M0_array_nominal             | CASP4  |          2 |   0.733614  |   0.000171136 |   0.00249278 | significant                 |
| GSE9944-GPL571|M1_donor_nominal             | FGFR1  |          6 |  -0.676617  |   0.107262    |   0.373823   | not significant (BH q>=.05) |
| GSE9944-GPL571|M1_donor_nominal             | SMAD1  |          2 |   0.964819  |   0.0231792   |   0.162605   | not significant (BH q>=.05) |
| GSE9944-GPL571|M1_donor_nominal             | STAT1  |          6 |  -1.16297   |   0.0149053   |   0.124176   | not significant (BH q>=.05) |
| GSE9944-GPL571|M1_donor_nominal             | TGFBR2 |          2 |   0.512075  |   0.10266     |   0.365307   | not significant (BH q>=.05) |
| GSE9944-GPL571|M1_donor_nominal             | CASP1  |          5 |   1.14971   |   0.00677261  |   0.0754744  | not significant (BH q>=.05) |
| GSE9944-GPL571|M1_donor_nominal             | CASP4  |          2 |   0.733614  |   0.00831925  |   0.0859591  | not significant (BH q>=.05) |
| GSE9944-GPL571|M2_donor_adjusted_FDR_LFC1   | FGFR1  |          6 |  -0.797797  |   0.0832964   |   0.372896   | not significant (BH q>=.05) |
| GSE9944-GPL571|M2_donor_adjusted_FDR_LFC1   | SMAD1  |          2 |  -0.164335  |   0.00453354  |   0.0769182  | not significant (BH q>=.05) |
| GSE9944-GPL571|M2_donor_adjusted_FDR_LFC1   | STAT1  |          6 |  -0.949784  |   0.0823703   |   0.37105    | not significant (BH q>=.05) |
| GSE9944-GPL571|M2_donor_adjusted_FDR_LFC1   | TGFBR2 |          2 |   0.338248  |   0.339413    |   0.695319   | not significant (BH q>=.05) |
| GSE9944-GPL571|M2_donor_adjusted_FDR_LFC1   | CASP1  |          5 |   1.09065   |   0.0310496   |   0.227456   | not significant (BH q>=.05) |
| GSE9944-GPL571|M2_donor_adjusted_FDR_LFC1   | CASP4  |          2 |   0.677499  |   0.0399219   |   0.260651   | not significant (BH q>=.05) |
| GSE9944-GPL571|M3_donor_adjusted_FDR_LFC05  | FGFR1  |          6 |  -0.797797  |   0.0832964   |   0.372896   | not significant (BH q>=.05) |
| GSE9944-GPL571|M3_donor_adjusted_FDR_LFC05  | SMAD1  |          2 |  -0.164335  |   0.00453354  |   0.0769182  | not significant (BH q>=.05) |
| GSE9944-GPL571|M3_donor_adjusted_FDR_LFC05  | STAT1  |          6 |  -0.949784  |   0.0823703   |   0.37105    | not significant (BH q>=.05) |
| GSE9944-GPL571|M3_donor_adjusted_FDR_LFC05  | TGFBR2 |          2 |   0.338248  |   0.339413    |   0.695319   | not significant (BH q>=.05) |
| GSE9944-GPL571|M3_donor_adjusted_FDR_LFC05  | CASP1  |          5 |   1.09065   |   0.0310496   |   0.227456   | not significant (BH q>=.05) |
| GSE9944-GPL571|M3_donor_adjusted_FDR_LFC05  | CASP4  |          2 |   0.677499  |   0.0399219   |   0.260651   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M0_array_nominal            | FGFR1  |          4 |   0.832295  |   0.0223078   |   0.254427   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M0_array_nominal            | SMAD1  |          2 |   0.927524  |   0.00537541  |   0.175046   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M0_array_nominal            | STAT1  |          8 |  -0.707385  |   0.00239389  |   0.139      | not significant (BH q>=.05) |
| GSE9944-GPL8300|M0_array_nominal            | TGFBR2 |          2 |   0.567188  |   0.0176616   |   0.239372   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M0_array_nominal            | CASP1  |          2 |   0.587019  |   0.000206758 |   0.0766219  | not significant (BH q>=.05) |
| GSE9944-GPL8300|M0_array_nominal            | CASP4  |          1 |   1.16429   |   0.00117156  |   0.119046   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M1_donor_nominal            | FGFR1  |          4 |   0.423133  |   0.0354588   |   0.459766   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M1_donor_nominal            | SMAD1  |          2 |   0.763042  |   0.0181268   |   0.40395    | not significant (BH q>=.05) |
| GSE9944-GPL8300|M1_donor_nominal            | STAT1  |          8 |  -0.6431    |   0.0085925   |   0.333599   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M1_donor_nominal            | TGFBR2 |          2 |   0.53797   |   0.029379    |   0.433711   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M1_donor_nominal            | CASP1  |          2 |   0.544925  |   0.00056847  |   0.201537   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M1_donor_nominal            | CASP4  |          1 |   1.01585   |   0.00617986  |   0.323096   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M2_donor_adjusted_FDR_LFC1  | FGFR1  |          4 |   0.316615  |   0.0644736   |   0.739168   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M2_donor_adjusted_FDR_LFC1  | SMAD1  |          2 |   0.0999265 |   0.708878    |   0.892728   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M2_donor_adjusted_FDR_LFC1  | STAT1  |          8 |  -0.785099  |   0.0512716   |   0.728359   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M2_donor_adjusted_FDR_LFC1  | TGFBR2 |          2 |  -0.326471  |   0.505368    |   0.808486   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M2_donor_adjusted_FDR_LFC1  | CASP1  |          2 |   0.314652  |   0.063462    |   0.739168   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M2_donor_adjusted_FDR_LFC1  | CASP4  |          1 |   0.173536  |   0.579292    |   0.840729   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M3_donor_adjusted_FDR_LFC05 | FGFR1  |          4 |   0.316615  |   0.0644736   |   0.739168   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M3_donor_adjusted_FDR_LFC05 | SMAD1  |          2 |   0.0999265 |   0.708878    |   0.892728   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M3_donor_adjusted_FDR_LFC05 | STAT1  |          8 |  -0.785099  |   0.0512716   |   0.728359   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M3_donor_adjusted_FDR_LFC05 | TGFBR2 |          2 |  -0.326471  |   0.505368    |   0.808486   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M3_donor_adjusted_FDR_LFC05 | CASP1  |          2 |   0.314652  |   0.063462    |   0.739168   | not significant (BH q>=.05) |
| GSE9944-GPL8300|M3_donor_adjusted_FDR_LFC05 | CASP4  |          1 |   0.173536  |   0.579292    |   0.840729   | not significant (BH q>=.05) |

## Interpretation rules
1. M0 >> M2 means the original DEG list was driven by pseudo-replication and lack of FDR.
2. If a key gene is not q<0.05 in M2, it must NOT be called a key gene.
3. If validation q>=0.05 in GSE45570, report non-replication; do not rescue by relaxing thresholds.
4. Platform overlap from the SAME GSE accession is technical replication, not external validation.
