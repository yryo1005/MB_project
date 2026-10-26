# UFB 濃度に対する組み合わせ特徴量の寄与探索 — レポート

`.orders/order_019.md` に基づき，`ex003_feature_engineering/` を新規作成し，6 つの基礎説明変数から積・逆数・比による組み合わせ特徴量を生成した上で，UFB concentration の予測・説明に寄与する特徴量を探索した．
実験コードは `ex003_feature_engineering/`，出力は `outputs/ex003_feature_engineering/` に保存されている．

---

## 1. 背景と目的

`.reports/report_003.md`（および論文 `paper/`）の分析から，Random Forest による Feature Importance は

- MB concentration・Oxygen content: Discharge tube が単独で支配的（約 62%・約 77%）
- UFB concentration: 単一の説明変数には支配されず，Discharge tube（約 25%）を筆頭に複数の説明変数に分散

という結果であった．
本研究の最終目的は「どの説明変数を変更すれば各目的変数を制御できるか」を明らかにすることであり，UFB concentration についてはこの単一要因支配の構造が見られないため，基礎説明変数単体ではなく，複数の説明変数を組み合わせた特徴量（積・逆数・比）の中に UFB concentration への寄与因子が存在するかを検証した．

---

## 2. 実験方法

### 2.1 組み合わせ特徴量の生成

基礎説明変数（6 個：Dissolve tube，Dissolution pressure，Discharge tube，Flow speed (oxygen)，Flow speed (water)，Water volume）はいずれも正の値のみを取るため，`data.build_engineered_features` により 0 除算なしで以下を生成した．

| 種別 | 内容 | 個数 |
| :--- | :--- | :--- |
| base | 基礎説明変数そのもの | 6 |
| product | 相異なる 2 変数の積 | 15 |
| reciprocal | 各変数の逆数 | 6 |
| ratio | 相異なる 2 変数の有向な比 | 30 |

合計 57 列の拡張特徴量行列を構築した．

### 2.2 モデル・評価

`ex002_figure_set/train.py` と同一のコード（5-fold GroupKFold，Random Forest: `n_estimators=100`, `max_depth=5`, `random_state=0`）を用い，UFB concentration（標準化後）に対して以下を比較した．

1. ベースライン: 基礎説明変数 6 個のみ
2. 拡張モデル: 基礎説明変数 6 個 + 組み合わせ特徴量 51 個（計 57 個）

拡張モデルについて，Feature Importance（MDI，fold 平均）と Permutation Importance（RMSE 増分，fold 平均）を算出した．

---

## 3. 結果

### 3.1 予測精度（RMSE）

`tables/rmse_comparison.md` の結果を示す．

| Feature set | Train RMSE | Test RMSE |
| :--- | ---: | ---: |
| Base (6 features) | 0.6184 | 0.8855 |
| Base + Engineered (57 features) | 0.6118 | 0.9184 |
| Base + Top-1 engineered feature (7 features) | 0.6261 | 0.8940 |
| Top-1 engineered feature only (1 feature) | 0.8249 | 0.9042 |

拡張モデル（57 特徴量）の Test RMSE（0.9184）は，ベースライン（0.8855）より**悪化**した．
また，ベースライン 6 特徴量に最重要の組み合わせ特徴量（後述）のみを 1 個加えた 7 特徴量モデル（Test RMSE 0.8940），当該特徴量 1 個のみを説明変数としたモデル（Test RMSE 0.9042）のいずれも，ベースライン単体（0.8855）を下回らなかった．
57 個の特徴量を一度に加えると，82 サンプルという限られたデータ数に対し特徴量数が相対的に多くなり，Random Forest の分岐選択にノイズとなる特徴量が混入した結果と考えられる．

### 3.2 Feature Importance（MDI）上位

`figures/feature_importance_mdi_top15.png` に示す通り，上位は以下の通りであった．

| 順位 | 特徴量 | 種別 | MDI |
| ---: | :--- | :--- | ---: |
| 1 | Dissolution pressure × Flow speed (oxygen) | product | 0.1219 |
| 2 | Flow speed (oxygen) / Discharge tube | ratio | 0.0809 |
| 3 | Dissolution pressure / Water volume | ratio | 0.0765 |
| 4 | Discharge tube / Flow speed (oxygen) | ratio | 0.0661 |
| 5 | Water volume / Dissolution pressure | ratio | 0.0546 |

基礎説明変数（"base"）は上位 9 位以内に一つも含まれず，組み合わせ特徴量が UFB concentration の説明において基礎説明変数単体より重要度が高いことが示された．

### 3.3 Permutation Importance 上位

`tables/permutation_importance.md` でも，1 位は MDI と同じ **Dissolution pressure × Flow speed (oxygen)**（RMSE 増分 0.0422）であり，2 位以下（0.0087 以下）との差が大きい．MDI・Permutation Importance の両指標で一致して最上位となったことから，この積特徴量が最も頑健に重要であると判断した．

### 3.4 最重要特徴量と UFB concentration の関係

`figures/scatter_top_engineered_feature.png` に，`Dissolution pressure × Flow speed (oxygen)` と UFB concentration の散布図を示す．右上がりの傾向があり，Pearson 相関係数は $r = 0.403$ であった．これは基礎説明変数単体の最大相関（Water volume: $r = -0.399$，Flow speed (oxygen): $r = 0.376$）をわずかに上回る．

---

## 4. 考察

- **UFB concentration への寄与因子**: 単一の基礎説明変数ではなく，Dissolution pressure と Flow speed (oxygen) の積（＝単位時間あたりに供給される酸素のモル量に相当すると解釈できる量）が最も一貫して UFB concentration と関連する．MDI・Permutation Importance の両方で突出して 1 位となったことは，この積が他の組み合わせ特徴量よりも頑健な説明因子であることを示唆する．
- **予測精度は改善しなかった**: 57 特徴量を一度に加えると Test RMSE はむしろ悪化し，最重要特徴量 1 個のみを追加しても改善しなかった．これは，この積特徴量が UFB concentration の変動のうち基礎説明変数（特に Flow speed (oxygen) や Water volume）が既に捉えている部分と重なる情報を表しており，予測精度の面では新しい情報を追加していない可能性を示唆する．一方で，解釈性の観点では「Dissolution pressure と Flow speed (oxygen) を同時に大きくする」という単一の操作方針として UFB concentration を説明できる点に意義がある．
- **多重共線性への留意**: 組み合わせ特徴量は基礎説明変数から直接計算されるため，相互に強い相関を持つ．Feature Importance の値は特徴量間の共線性の影響を受けるため，本結果は「この組み合わせが他の候補より相対的に重要」という序列として解釈すべきであり，個々の重要度の絶対値を過度に重視すべきではない．

---

## 5. 今後の検討候補

- `Dissolution pressure × Flow speed (oxygen)` を説明変数に加えた上で，UFB concentration を目的変数とする単回帰・多項式回帰を行い，関係式の形状（線形か否か）を確認する．
- 組み合わせ特徴量を 57 個すべて使うのではなく，相関行列に基づく特徴選択やLASSO等の正則化線形モデルを用いて，予測精度を悪化させずに重要な組み合わせ特徴量のみを絞り込む手法を検討する．
- 本実験では UFB concentration のみを対象としたが，同様の手法を MB concentration・Oxygen content に適用し，Discharge tube 以外の寄与因子が存在しないか確認する余地がある（ただし現状，両者は Discharge tube 単独で十分説明できている）．
