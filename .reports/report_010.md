# TeX論文「実験」章 執筆レポート

`.orders/order_010.md` に基づき，`@proceeding.pdf`（予稿），`ex001_base_model/`，`ex002_figure_set/` の内容を参考に，論文の「実験」章（データの収集，実験条件，実験結果，考察）を TeX で執筆した．指示通り，アブストラクト・はじめに・おわりに等の他章は作成していない．

---

## 1. 指示内容と対象範囲

- 章立て: 1. 実験（1.1 データの収集，1.2 実験条件，1.3 実験結果，1.4 考察）
- 図は `@figures/` 以下の 10 ファイルをそのまま使用（再生成はしていない）
- 標準化，相関係数，CV，郡内分散，RMSE，Random Forest 等，数式が絡む説明は数式を用いて記述
- 用語統一: 目的変数／説明変数の定義を明記，NB（NanoSight 表記）は UFB に統一

投稿先・ページ数制限・締切は指示書に記載がなく，本セッションでは未確認である．

---

## 2. 作成物

```text
paper/
├── main.tex                              # \section{実験} と各小節の \input
├── ieicejsp.cls                          # .ai/ai-tex-kit/templates/ja_paper/ から複製
├── latexmkrc                             # 同上
├── main.pdf                              # 生成物（5 ページ）
├── sections/
│   ├── 01_data_collection.tex            # 1.1 データの収集
│   ├── 02_experimental_conditions.tex    # 1.2 実験条件
│   ├── 03_results.tex                    # 1.3 実験結果
│   └── 04_discussion.tex                 # 1.4 考察
└── figures/                              # /figures/ から複製した 10 ファイル
```

`main.tex` の `\title`／`\author`／`\affliate` はテンプレートの体裁を保ったまま，タイトルのみ `@proceeding.pdf` に記載の研究題目（「AI を用いたファインバブル発生装置の最適操作条件の検討」）に置き換えた．著者名は本セッションに情報が無いため，プレースホルダ（「著者」）のまま残している．

`latexmk -pdfdvi -synctex=1 main.tex` によりコンパイルし，エラーなく `main.pdf`（5 ページ）を生成できることを確認した．

---

## 3. 各節の内容と根拠

### 3.1 データの収集（1.1）
`@proceeding.pdf` の手順欄および `MB_data_v4.csv` の実データから，FBG-OS Type1 による FB 生成，6 説明変数の設定水準，測定機器（NanoSight LM10／PartAn SI／Oxygraph）を記述した．サンプル数（82）・操作条件数（39）は `MB_data_v4.csv` を実際に集計して確認した値であり，`@proceeding.pdf` の記載（水準の組み合わせ）とも整合する．図 1（`figure1_experimental_procedure.png`）を用いて実験系の概略を説明した．

### 3.2 実験条件（1.2）
`ex002_figure_set/data.py` の実装（`normalize_targets`，`compute_cv_and_within_group_std`，`compute_input_target_correlation`）に基づき，標準化，Pearson 相関係数，CV，郡内標準偏差の定義式を記述した．

**用語に関する注記**: `figures/table1_...png` の見出しおよび `.orders/order_010.md` の文言は「郡内分散（Within-Group Variance）」であるが，実際に `data.py` で計算されている量は標準化後サンプルの郡内標準偏差（分散の平方根）であり，`.reports/report_003.md` も同じ値を「郡内標準偏差」と記載している．本文中では実際の計算内容に忠実な「郡内標準偏差」という表記に統一し，数式（式 4, 5）も標準偏差として定義した．表 1 の画像自体の見出し文字列（「Within-Group Variance」）は変更していない．

CV・郡内標準偏差（表 1）から UFB 濃度・MB 濃度を，研究目的上の重要性（`@proceeding.pdf` の背景・目的）から酸素含量を分析対象に選定する根拠を記述した．

### 3.3 実験結果（1.3）
`ex002_figure_set/train.py` の実装（`evaluate_models`: 線形回帰／`PolynomialFeatures(2)`＋線形回帰／`RandomForestRegressor(n_estimators=100, max_depth=5)`，5-fold `GroupKFold`，`compute_feature_importance`: fold平均 MDI）に基づき，モデル構成，RMSE の定義，Random Forest が全目的変数で最良の Test RMSE を示したこと（表 2），多項式回帰が UFB 濃度で過学習していること（Train 0.695 vs Test 1.168）を記述した．Feature Importance（図 3〜5）と箱ひげ図（図 6〜8）について，MB・酸素含量は吐出管長さが支配的，UFB 濃度は複数因子が分散して寄与する，という傾向を実際の図から読み取れる数値（Feature Importance 約 62%／77%，中央値の推移等）とともに記述した．

### 3.4 考察（1.4）
Random Forest が優れた理由として，(1) MB 濃度と吐出管長さの関係が非単調であり線形回帰では表現できないこと，(2) 多項式回帰が UFB 濃度で過学習したこと，(3) Random Forest は決定木の深さ制限とアンサンブル平均により過学習を抑制しつつ非線形性を近似できること，を述べた．また，相関係数・Feature Importance・箱ひげ図を横断的に参照し，酸素含量は単一要因（吐出管長さ）で説明できる度合いが高く，MB 濃度は非線形な単一要因依存，UFB 濃度は複数要因の複合的な影響を受けている，という 3 目的変数間の違いを考察としてまとめた．

---

## 4. 未解決の論点・今後の検討候補

- `\author`／`\affliate` はプレースホルダのままであり，実際の著者名・所属を確定させる必要がある．
- 投稿先（学会・ページ数制限）が指示書に記載されていないため，`.ai/ai-tex-kit/README.md` のサンプル（`ja_paper_*`，`ja_proceeding_*`）を参照した分量調整は行っていない．必要であれば投稿先の指定を受けて章構成・分量を調整する．
- 表 1 の画像に埋め込まれた見出し文字列「Within-Group Variance」と，本文中の用語「郡内標準偏差」に不一致がある（3.2 節参照）．画像を差し替えるか，本文表記を合わせるかは次の指示を待つ．
- 参考文献（`thebibliography`）は，本章内で外部文献を直接引用する記述が無いため作成していない．はじめに・おわりに等の章を追加する際に必要になる可能性がある．
- Feature Importance の非線形性に関する考察（1.4.2）は，統計的根拠（相関係数と Feature Importance の乖離）に基づく推論であり，操作条件と FB 物性値の間の具体的な流体力学的メカニズムには踏み込んでいない．装置構造に基づく物理的な解釈が必要な場合は追加の検討が必要である．
