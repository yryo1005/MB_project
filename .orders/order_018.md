相関係数を転置して横に長くできる？

---

## 解釈・対応記録

- 相関係数ヒートマップを転置（目的変数を縦軸3行，説明変数を横軸6列）し，横に長い図（9.0×3.0 inch，300 dpi，2552×823 px）を新規作成した．
- `ex002_figure_set/figures.py` の `plot_correlation_heatmap` に `transpose` 引数を追加した（既定値 `False` で既存の呼び出し・既存図は無変更）．
- 転置版は `figure2_correlation_coefficient_transposed.png` として `outputs/ex002_figure_set/figures_large/` に新規出力した（`ex002_figure_set/run_figures_corr_transposed.py`）．既存の図（元図，large版，slim版）は上書きしていない．
- 論文への反映は行っていない．
