これまでの結果から，Random ForestモデルがMB conc., Oxygen cont.を予測する際に，
Discharge Tubeの寄与が大きい（Feature Importance）が大きいことがわかりました．

これに対しUFB conc.は特定の説明変数のFeature Importanceが高くないこともわかっています．

本研究の最終目的は，それぞれの目的変数をどの説明変数を変更することで制御できるかを明らかにすることです．

そこで，説明変数同士を組み合わせた説明変数（積や逆数など）を新たに加え，
UFB conc.に寄与する説明変数を探してください．

ex003とします

---

## 解釈・対応記録

- モデル構造（Random Forest 等）自体は変更せず，説明変数の前処理（特徴量エンジニアリング）が本質的に変わるため，`root_prompt.md`／`machine_learning.md` の規約に従い実験番号を `n+1`（ex003）とする．ユーザー指定とも一致する．
- 「積や逆数など」を，6つの基礎説明変数から作る (1) 全ペアの積，(2) 各変数の逆数，(3) 全ペア（有向）の比，の3種類の組み合わせ特徴量と解釈した．
- 対象目的変数は UFB concentration のみとする．他目的変数（MB conc., Oxygen cont.）は Discharge tube による説明で十分との既存知見があるため，今回の特徴量探索では主対象としない．
- 既存ディレクトリ（`ex001_base_model/`, `ex002_figure_set/`）は変更せず，`ex003_feature_engineering/` を新規作成して実装する．
