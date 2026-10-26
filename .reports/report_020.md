# UFB 濃度に対する組み合わせ特徴量の寄与探索（続き）— 相関に基づく貪欲法による特徴選択

`.orders/order_020.md` に基づき，`.reports/report_019.md`（ex003）の続きとして，Random Forest・5-fold GroupKFold・組み合わせ特徴量生成（積・逆数・比）はすべて既存実装のまま，新たに「Permutation Importance 順位 + 相関に基づく貪欲法」による特徴選択を追加した．
実験コードは `ex003_feature_engineering/run_feature_selection.py`，出力は `outputs/ex003_feature_engineering/` に保存されている．

---

## 1. 背景

report_019 では，57 個の組み合わせ特徴量を一度にすべて加えると Test RMSE がベースライン（6 特徴量，0.8855）より悪化し（0.9184），最重要特徴量を 1 個だけ加えても改善しなかった（0.8940）．
これは特徴量数が多すぎることによる過学習・ノイズ混入が原因と考えられたため，「相関行列に基づく特徴選択で，予測精度を悪化させずに重要な組み合わせ特徴量を絞り込む」ことを本レポートで検証した．

---

## 2. 方法

1. report_019 で算出済みの 57 特徴量モデルにおける Permutation Importance の順位を，特徴量を追加する候補順とした．
2. 57 特徴量間の Pearson 相関行列を計算した．
3. 重要度の高い候補から順に，**既に選択した特徴量のいずれかと $|r| > 0.8$ の相関を持つ場合は冗長とみなして除外**し，そうでなければ選択集合に追加した．
4. 特徴量を 1 個追加するたびに，その時点の選択集合のみを説明変数として Random Forest（`train.py`，5-fold GroupKFold，既存実装のまま変更なし）を学習し，Train/Test RMSE を記録した．
5. 選択数の上限は 15 とした（57 候補のうち相関冗長で除外されたものを除く）．

導入した新規要素は「相関に基づく貪欲法」のみであり，モデル・CV・特徴量生成はすべて report_019 の実装を再利用している．

---

## 3. 結果

### 3.1 特徴選択の推移

`tables/feature_selection_progression.md`，`figures/feature_selection_rmse_curve.png` に全過程を示す．37 候補を走査し，22 個が相関冗長（$|r|>0.8$）として除外され，15 個が選択された．

| 特徴量数 | 追加された特徴量 | 種別 | Test RMSE |
| ---: | :--- | :--- | ---: |
| 1 | Dissolution pressure × Flow speed (oxygen) | product | 0.9042 |
| 2 | Flow speed (oxygen) / Discharge tube | ratio | 0.9087 |
| 3 | Flow speed (water) / Dissolution pressure | ratio | 0.9117 |
| **4** | **Discharge tube × Water volume** | **product** | **0.8442** |
| 5〜15 | （以降，ベースライン付近で増減） | — | 0.869〜0.889 |

**4 特徴量の時点で Test RMSE が 0.8442 まで低下し，ベースライン（0.8855）を下回った．これが 15 ステップ中の最小値であった．** 5 特徴量目以降はベースライン付近（0.87〜0.89）で増減を繰り返し，4 特徴量時点を下回ることはなかった．

### 3.2 最良部分集合（4 特徴量）

| 特徴量 | 種別 | Feature importance (MDI) |
| :--- | :--- | ---: |
| Dissolution pressure × Flow speed (oxygen) | product | 0.348 |
| Discharge tube × Water volume | product | 0.270 |
| Flow speed (oxygen) / Discharge tube | ratio | 0.244 |
| Flow speed (water) / Dissolution pressure | ratio | 0.138 |

`figures/best_subset_feature_importance.png` に示す通り，4 特徴量いずれも 0.14〜0.35 の範囲で寄与しており，特定の 1 特徴量に支配されない．6 基礎説明変数のうち Dissolve tube を除く 5 変数（Dissolution pressure，Flow speed (oxygen)，Discharge tube，Water volume，Flow speed (water)）がいずれかの組み合わせ特徴量に含まれている．

### 3.3 Test RMSE 低下の要因となった特徴量

3 特徴量目から 4 特徴量目への追加（`Discharge tube × Water volume`）で Test RMSE が 0.9117 → 0.8442 と大きく低下した．`figures/scatter_rmse_drop_feature.png` にこの特徴量単体と UFB concentration の散布図を示すが，単純な単調関係は見られない．したがって，この特徴量単体の線形・単調な効果ではなく，既選択の 3 特徴量との**組み合わせ**によって Random Forest の分割精度が向上したことが示唆される（詳細な交互作用の分解は本レポートの範囲外とする）．

---

## 4. 考察

- 57 特徴量を一度に用いると過学習したが，Permutation Importance 順位と相関冗長性除去による絞り込みにより，**わずか 4 個の組み合わせ特徴量でベースライン（基礎説明変数 6 個）を上回る予測精度（Test RMSE 0.8442 < 0.8855）を達成**した．UFB concentration は単一の操作条件では説明できないが，少数の組み合わせ特徴量（操作条件のペア）によって説明できる可能性が示された．
- 選択された 4 特徴量は，Dissolution pressure，Flow speed (oxygen)，Discharge tube，Water volume，Flow speed (water) の 5 変数（Dissolve tube を除く）から構成されており，report_019 で確認された「UFB concentration は単一要因ではなく複数の操作条件が複合的に影響する」という傾向と整合する．
- 5 特徴量目以降は Test RMSE が再び悪化・停滞する傾向を示しており，闇雲に特徴量を増やすのではなく，本手法のように重要度と相関冗長性の両方を考慮した絞り込みが有効であることが確認できた．
- 相関閾値（$|r|>0.8$）は一つの選択であり，閾値を変えれば選択される特徴量集合・最良ステップ数は変化しうる．本レポートでは単一の閾値のみを検証しており，閾値への感度分析は行っていない．

---

## 5. 今後の検討候補

- 相関閾値（0.6〜0.9 程度）を振って，選択される特徴量集合・最良 Test RMSE の閾値依存性を確認する．
- 4 特徴量の部分集合に対して，`Discharge tube × Water volume` と他の特徴量との交互作用（2 次元の Partial Dependence 等）を可視化し，Test RMSE 低下の要因を物理的に解釈する。
- 本レポートは貪欲法（前方選択のみ）であるため，後方除去や厳密な全部分集合探索（計算量が許す範囲で）との比較により，4 特徴量が真に最良かを検証する余地がある．
