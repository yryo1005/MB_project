# 図の文字サイズ拡大レポート

`.orders/order_014.md` に基づき，論文で使用しているプログラム生成図（相関ヒートマップ，Feature Importance，箱ひげ図）の文字を大きくした．

## 対応内容
- `ex002_figure_set/figures.py`: `apply_figure_style` および3つの描画関数に `font_size`（既定値 10 で従来出力は不変），Feature Importance に `wrap_units`（縦軸ラベルの単位を改行）を追加した．
- `ex002_figure_set/run_figures_large.py`（新規）: 文字を大きくした図（ヒートマップ 15pt，FI・箱ひげ図 17pt，出力 300 dpi，約 1700 px 四方）を `outputs/ex002_figure_set/figures_large/` に `*_large.png` として出力する．従来の 416 px の図より解像度は高い．
- 既存の図（`figures/`，`paper/figures/` の元ファイル，`outputs/ex002_figure_set/figures/`）は一切上書きしていない（`git status` で元ファイルに変更が無いことを確認）．`paper/figures/` には `_large` 付きの新規ファイルのみを追加し，`paper/sections/` のTeXの参照先をこれらへ変更した．
- `latexmk` で再コンパイルし（7ページ），図中の文字が従来より大きく読めることを目視確認した．

## 対象外・未解決
- 装置の概略図（figure1）と表の画像（table1，table2）は外部で作成された画像であり，プログラムから再生成できないため文字サイズは変更していない．

## 追加対応（order_015）
Feature Importance の図のみ縦3：横5（7.5×4.5 inch，300 dpi）の横長に再生成し，縦軸ラベルの改行を廃止した．論文中の図3は横長図を (A)(B)(C) の縦積み配置（各 0.62\linewidth）に変更した（全8ページ）．図3は1ページ内に収まるが，紹介文の次ページに配置される場合がある．

## 追加対応（order_016）
全7図（相関ヒートマップ1枚，Feature Importance 3枚，箱ひげ図3枚）について，縦の解像度（高さ）を `_large` 版と同一に保ったまま横幅のみ縮小した `_slim` 版を `outputs/ex002_figure_set/figures_large/` に新規出力した（`ex002_figure_set/run_figures_slim.py`）．文字・数値が重ならない範囲で幅を絞っており，幅は図によって24〜32%程度縮小している．既存の図・`_large` 図は上書きしていない．論文への反映はまだ行っていない．

## 追加対応（order_017）
Feature Importance の図を転置（横棒→縦棒）し，縦に長い図（3.5×7.0 inch，975×2022 px）を3目的変数分新規作成した（`ex002_figure_set/run_figures_fi_transposed.py`）．`figures.py` の `plot_feature_importance` に `transpose` 引数を追加したが，既定値は `False` のため既存の図・呼び出しへの影響はない．既存図は上書きせず，`outputs/ex002_figure_set/figures_large/*_transposed.png` に保存した．論文への反映はまだ行っていない．

## 追加対応（order_018）
相関係数ヒートマップを転置（目的変数3行×説明変数6列）し，横に長い図（9.0×3.0 inch，2552×823 px）を新規作成した（`ex002_figure_set/run_figures_corr_transposed.py`）．`figures.py` の `plot_correlation_heatmap` に `transpose` 引数を追加したが，既定値は `False` のため既存の図・呼び出しへの影響はない．既存図は上書きせず，`outputs/ex002_figure_set/figures_large/figure2_correlation_coefficient_transposed.png` に保存した．論文への反映はまだ行っていない．
