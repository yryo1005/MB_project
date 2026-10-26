# UFB 濃度に対する組み合わせ特徴量の寄与探索（続き）— 上位候補に限定した厳密な全部分集合探索

`.orders/order_021.md` に基づき，`.reports/report_020.md`（相関に基づく貪欲法）よりも Test RMSE を低下させる（＝寄与率を高める）特徴量の組み合わせを探索した．
モデル（Random Forest）・交差検証（5-fold GroupKFold）・組み合わせ特徴量生成はすべて既存実装のまま，新たに「Permutation Importance 上位候補に限定した厳密な全部分集合探索」を追加した．
指示に従い，相関閾値や候補数等のパラメータに対する感度分析は本レポートでは行わず，次オーダー以降で実施する．
実験コードは `ex003_feature_engineering/run_exhaustive_search.py`，出力は `outputs/ex003_feature_engineering/` に保存されている．

---

## 1. 背景

report_020 の貪欲法は，既に選択した特徴量と相関 $|r|>0.8$ の候補を逐次的に除外する手続き上，候補の評価順序（Permutation Importance 順）やこの閾値の設定次第で，真に最良な組み合わせを見落とす可能性があった．
実際，report_020 の「今後の検討候補」で「後方除去や厳密な全部分集合探索との比較により，4 特徴量が真に最良かを検証する余地がある」と指摘していた．本レポートはこれを実施する．

---

## 2. 方法

1. 57 特徴量モデルの Permutation Importance 上位 15 件（`CANDIDATE_POOL_SIZE`）に候補を限定した．全探索の候補を絞る目的は計算量の抑制であり，相関による除外は行っていない（貪欲法との違い）．
2. この 15 件の候補から，サイズ 1〜5（`MAX_SUBSET_SIZE`）の部分集合を**全て**（$\sum_{k=1}^{5} {}_{15}C_k = 4943$ 通り）列挙し，各部分集合について Random Forest の 5-fold GroupKFold Test RMSE を計算した．
3. 計算量を抑えるため，探索フェーズでは決定木数を 30（`SEARCH_N_ESTIMATORS`，`train.py` の既定値 100 より少ない）に減らした．
4. 各サイズにおける最良部分集合を，`train.py` と同一の決定木数 100 で再評価し，最終的な Train/Test RMSE とした．

探索フェーズの決定木数を減らしたのは計算時間短縮のためであり（4943 件 × 5-fold の評価に要した時間は 560.8 秒），最終的に報告する数値はすべて `train.py` と同一条件（決定木数 100）で再評価した値である．

---

## 3. 結果

### 3.1 サイズごとの最良部分集合（n_estimators=100 で再評価）

`tables/exhaustive_search_best_per_size.md`，`figures/exhaustive_search_rmse_curve.png` を示す．

| サイズ | Train RMSE | Test RMSE |
| ---: | ---: | ---: |
| 1 | 0.8230 | 0.8891 |
| 2 | 0.6357 | 0.8438 |
| 3 | 0.6204 | 0.8176 |
| **4** | **0.6177** | **0.8107** |
| 5 | 0.6208 | 0.8144 |

サイズ 4 で Test RMSE が最小（0.8107）となり，サイズ 5 ではわずかに悪化した．

### 3.2 最良の組み合わせ（4 特徴量）

| 特徴量 | 種別 | Feature importance (MDI) |
| :--- | :--- | ---: |
| Dissolution pressure × Flow speed (oxygen) | product | 0.413 |
| Discharge tube × Water volume | product | 0.277 |
| Flow speed (oxygen) / Discharge tube | ratio | 0.236 |
| Flow speed (oxygen) / Dissolve tube | ratio | 0.073 |

**Test RMSE 0.8107** は，ベースライン（基礎説明変数 6 個，0.8855）比で **約 8.4% の改善**，report_020 の貪欲法による最良値（4 特徴量，0.8442）比でも **約 4.0% の改善**であった．

上記 4 特徴量のうち先頭 3 つ（product: Dissolution pressure × Flow speed (oxygen)，product: Discharge tube × Water volume，ratio: Flow speed (oxygen) / Discharge tube）は，`tables/exhaustive_search_top50.md` の上位 50 件の大半に共通して含まれており，サイズ 3〜5 の探索結果全体で安定した「中核」をなしていた（`tables/exhaustive_search_best_per_size.md` のサイズ 3・4 の内訳を参照）．これに対し 4 番目の特徴量は，report_020 の貪欲法が選んだ `Flow speed (water) / Dissolution pressure` ではなく `Flow speed (oxygen) / Dissolve tube` であり，相関閾値による逐次除外では見落とされていた組み合わせであった．

---

## 4. 考察

- **貪欲法より良い組み合わせが見つかった**: 相関閾値による逐次除外を行わず，Permutation Importance 上位候補内で全探索したことで，貪欲法の最良値（0.8442）を約 4% 更新する組み合わせ（0.8107）を発見した．貪欲法は計算量を抑えつつ良い解を素早く見つける手法だが，本件のように相関閾値の設定が探索結果に影響する場合があることを裏付けている．
- **中核となる 3 特徴量の頑健性**: 「Dissolution pressure × Flow speed (oxygen)」「Discharge tube × Water volume」「Flow speed (oxygen) / Discharge tube」の 3 つは，貪欲法・全探索のいずれでも繰り返し選ばれており，UFB concentration の予測に頑健に寄与する組み合わせであると考えられる．
- **サイズ 4 が頭打ち**: サイズ 5 で Test RMSE が再び悪化したことから，少なくとも探索した範囲（候補 15 件，サイズ 5 まで）では，4 特徴量が最も汎化性能の高い組み合わせであった．
- **探索範囲の限定**: 本探索は計算量の都合上，候補を Permutation Importance 上位 15 件・サイズ上限 5 に限定している。候補プールに含まれなかった特徴量（57 件中の下位 42 件）や，サイズ 6 以上の組み合わせはこの時点では評価していない。

---

## 5. 今後の検討候補（感度分析）

指示に従い，以下は次オーダー以降で実施する．

- 候補プールサイズ（`CANDIDATE_POOL_SIZE`，本レポートでは 15）を変化させた場合に，最良 Test RMSE・最良部分集合がどの程度変化するかを確認する．
- 探索する部分集合サイズの上限（`MAX_SUBSET_SIZE`，本レポートでは 5）を広げた場合に，さらに良い組み合わせが存在するかを確認する．
- 探索フェーズの決定木数（`SEARCH_N_ESTIMATORS`，本レポートでは 30）を変化させた場合に，探索順位・最良部分集合の選定が安定しているかを確認する．
