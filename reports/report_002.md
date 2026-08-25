# ファインバブル発生装置の最適操作条件検討 — Figure Set レポート

`orders/order_002.md` に基づき，論文執筆用 Figure Set を生成し，研究内容・実験方法・実験結果をまとめたレポートである．  
実験コードは `ex002_figure_set/`，出力は `outputs/ex002_figure_set/` に保存されている．

---

## 1. 研究内容

### 1.1 背景と目的

ファインバブル（Fine Bubble, FB）は直径 $100\,\mu\mathrm{m}$ 以下の微細気泡であり，高い滞留性およびガス溶解性を有する．本研究では FBG-OS Type1 による FB 発生装置において，操作条件と FB 物性値の関係を機械学習で解析し，以下を目的とする．

- 操作条件から FB 物性値を予測可能であることの定量的示唆
- 複数目的変数の中から分析対象を選定する統計的根拠の提示
- 線形回帰，多項式回帰，Random Forest の比較による最適モデルの選定
- Random Forest による重要操作因子の抽出と，その関係形状の可視化

### 1.2 分析対象

目的変数は以下 3 つとする．データセット中の NB 表記は全体を通して **UFB** と表記する．

| 目的変数 | 略称 | 計測器 |
| :--- | :--- | :--- |
| MB 濃度 | MB conc. | PartAn SI |
| UFB 濃度 | UFB conc. | NanoSight LM10 |
| 酸素含量 | Oxygen cont. | Oxygraph |

---

## 2. 実験方法

### 2.1 データセット

- ファイル: `MB_data_v4.csv`
- サンプル数: 82
- 操作条件数: 39（条件あたり 1〜5 反復）

#### 説明変数（6）

| 変数 | 単位 | 設定値 |
| :--- | :--- | :--- |
| Dissolve tube | m | 0.12, 2.0 |
| Dissolution pressure | MPa | 2, 3, 4 |
| Discharge tube | m | 0.7, 2, 4, 5 |
| Flow speed (oxygen) | mL/min | 3.3, 5, 10, 25 |
| Flow speed (water) | mL/min | 25, 40, 45, 46.7 |
| Water volume | mL | 50, 100 |

### 2.2 機械学習

| 項目 | 設定 |
| :--- | :--- |
| 交差検証 | 5-fold GroupKFold（同一操作条件を同一グループ） |
| 線形回帰 | `LinearRegression` |
| 多項式回帰 | `PolynomialFeatures(degree=2)` + 線形回帰 |
| Random Forest | `n_estimators=100`, `max_depth=5`, `random_state=0` |
| 評価指標 | 標準化後目的変数の RMSE |
| 重要度 | MDI ベース F.I.（fold 平均），Permutation Importance（RMSE 増分，fold 平均） |

### 2.3 図の共通仕様

- モノクロ（グレースケール）
- 余計な線なし（上・右スパインおよびグリッドを非表示）
- グラフタイトルなし
- 軸ラベルは英語，単位付き

---

## 3. Figure Set 一覧

| 図番 | ファイル | 内容 |
| :--- | :--- | :--- |
| Fig. 1 | `figures/correlation_input_target.png` | 説明変数と目的変数の Pearson 相関係数 |
| Table 1 | `tables/cv_within_group.md` | CV と郡内標準偏差 |
| Table 2 | `tables/model_comparison.md` | 3 モデルの Train/Test RMSE |
| Fig. 2a–c | `figures/feature_importance_*.png` | Random Forest F.I.（MB, UFB, Oxygen） |
| Fig. 3a–c | `figures/scatter_*.png` | 最重要特徴量と目的変数の散布図 |
| Table 3 | `tables/permutation_importance_all.md` | 置換重要度（全目的変数） |

---

## 4. 実験結果

### 4.1 目的変数の選定根拠（Table 1）

郡内標準偏差は標準化後の目的変数について，同一操作条件内の標準偏差を条件間平均した値である．CV は全体の $\sigma / \mu$ とする（`ex001_base_model/main.ipynb` と同一定義）．

| Target | CV | Within-group std |
| :--- | ---: | ---: |
| Mean size [nm] | 0.216 | 0.450 |
| Mode size [nm] | 0.228 | 0.458 |
| **UFB conc.** | **0.636** | 0.349 |
| **MB conc.** | **0.688** | **0.167** |
| Size (bin) [µm] | 0.068 | 0.236 |
| **Oxygen cont.** | 0.112 | 0.289 |

MB 濃度は郡内標準偏差が 0.167 と比較的小さく，同一条件内の再現性が高い．UFB 濃度および MB 濃度は CV が 0.6 以上と大きく，操作条件による変動が顕著である．Size (bin) は CV が 0.07 と小さく，操作条件の影響を受けにくい．  
Oxygen cont. は CV は小さいが，後述の相関・F.I. 解析において操作条件との関連が確認されるため，本 Figure Set では UFB，MB，Oxygen の 3 変数を分析対象とした．

### 4.2 説明変数と目的変数の相関（Fig. 1）

主要な相関関係は以下の通りである．

| 説明変数 | MB conc. | UFB conc. | Oxygen cont. |
| :--- | ---: | ---: | ---: |
| Discharge tube | −0.46 | 0.07 | **0.65** |
| Flow speed (oxygen) | −0.23 | **0.38** | −0.01 |
| Water volume | 0.13 | **−0.40** | −0.08 |

Discharge tube は MB 濃度と負，酸素含量と正の相関を示す．UFB 濃度は Flow speed (oxygen) および Water volume と相関が相対的に大きい．  
操作条件と目的変数の間に一定の線形相関が存在することから，機械学習による予測が有効である可能性が示唆される．

### 4.3 モデル比較（Table 2）

| Target | Model | Train RMSE | Test RMSE |
| :--- | :--- | ---: | ---: |
| MB conc. | Linear | 0.865 | 0.936 |
| MB conc. | Polynomial | 0.522 | 0.755 |
| MB conc. | **Random Forest** | **0.380** | **0.642** |
| UFB conc. | Linear | 0.844 | 0.956 |
| UFB conc. | Polynomial | 0.695 | 1.168 |
| UFB conc. | **Random Forest** | **0.618** | **0.885** |
| Oxygen cont. | Linear | 0.675 | 0.750 |
| Oxygen cont. | Polynomial | 0.509 | 0.792 |
| Oxygen cont. | **Random Forest** | **0.461** | **0.684** |

3 目的変数すべてにおいて Random Forest が最低 Test RMSE を示した．多項式回帰は UFB 濃度で過学習（Test RMSE 1.168）が確認された．  
よって本研究の予測モデルとして Random Forest を採用するのが妥当である．

### 4.4 Feature Importance（Fig. 2）

Random Forest の F.I.（fold 平均）の結果は以下の通りである．

#### MB conc.

| Feature | Importance |
| :--- | ---: |
| **Discharge tube** | **0.619** |
| Flow speed (water) | 0.083 |
| Flow speed (oxygen) | 0.080 |

#### UFB conc.

| Feature | Importance |
| :--- | ---: |
| **Discharge tube** | **0.247** |
| Dissolution pressure | 0.234 |
| Water volume | 0.224 |

#### Oxygen cont.

| Feature | Importance |
| :--- | ---: |
| **Discharge tube** | **0.768** |
| Flow speed (water) | 0.067 |
| Flow speed (oxygen) | 0.065 |

MB 濃度および酸素含量では Discharge tube が支配的である．UFB 濃度では Discharge tube，Dissolution pressure，Water volume が同程度の寄与を示し，単一因子支配型ではない．

### 4.5 散布図（Fig. 3）

F.I. 上位特徴量（3 目的変数すべて Discharge tube）と目的変数の関係を散布図で示した．

- **MB conc. vs Discharge tube**: 吐出管 0.7 m で高濃度，2 m 以上で低濃度に推移する非線形パターン
- **UFB conc. vs Discharge tube**: 単調増加ではなく，条件依存の散らばり
- **Oxygen cont. vs Discharge tube**: 0.7 m で低，2 m 以上で高い値に推移

MB 濃度と酸素含量は Discharge tube に対して**逆方向**の応答を示す可能性があり，多目的最適化におけるトレードオフの存在が示唆される．

### 4.6 置換重要度（Table 3）

Permutation Importance（RMSE 増分，fold 平均）の上位結果は以下の通りである．

| Target | Feature | RMSE increase |
| :--- | :--- | ---: |
| MB conc. | Discharge tube | 0.427 |
| UFB conc. | Water volume | 0.091 |
| UFB conc. | Discharge tube | 0.085 |
| Oxygen cont. | Discharge tube | 0.549 |

MDI ベース F.I. と整合的に，MB および Oxygen では Discharge tube の絶対的寄与が大きい．UFB では複数変数への寄与が分散する．  
Permutation Importance は性能低下量として解釈可能であり，Discharge tube の重要性を絶対量でも支持する結果となった．

---

## 5. 考察

- 操作条件から FB 物性値を予測する問題設定は，相関解析および GroupKFold 評価の結果から妥当である．
- 目的変数の選定は CV および F.I. 解析に基づき，UFB 濃度，MB 濃度，酸素含量を採用するのが適切である．
- Random Forest は 3 目的変数すべてで最良の Test RMSE を示し，予稿（`proceeding.pdf`）の結果と整合する．
- Discharge tube は MB 濃度・酸素含量に対する主要因子であり，F.I. の形状類似は両応答が同一操作因子に強く感作されているためと解釈できる．
- UFB 濃度は複数因子の寄与が分散しており，単一因子支配型の MB/Oxygen とは異なる応答構造を持つ．

---

## 6. 今後の展開

- 各目的変数に応じた最適操作条件の探索（単目的最適化および多目的最適化）
- Partial $R^2$ や SHAP による絶対的重要度の追加解析
- 追加実験による未試条件の補完と外挿性能の検証

---

## 参考文献

1. Kakiuchi K, et al., Do Ultrafine Bubbles Work as Oxygen Carriers? Langmuir, 2023.
