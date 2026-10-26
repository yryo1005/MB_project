Feature Importanceのグラフを転置して縦に長くできない？

---

## 解釈・対応記録

- Feature Importance の棒グラフを転置（横棒→縦棒，説明変数を横軸，重要度[%]を縦軸）し，縦に長い図（3.5×7.0 inch，300 dpi，975×2022 px）を新規作成した．
- `ex002_figure_set/figures.py` の `plot_feature_importance` に `transpose` 引数を追加した（既定値 `False` で既存の呼び出し・既存図は無変更）．
- 転置版は3目的変数分すべて `figure3{A,B,C}_..._feature_importance_transposed.png` として `outputs/ex002_figure_set/figures_large/` に新規出力した（`ex002_figure_set/run_figures_fi_transposed.py`）．既存の図（横棒版，large版，slim版）は上書きしていない．
- 論文への反映は行っていない．
