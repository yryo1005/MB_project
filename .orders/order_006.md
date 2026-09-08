相関係数以外の図はモノクロにして

---

## 解釈・対応記録

- 「相関係数以外の図」とは，`ex002_figure_set` が生成する Figure Set のうち，`correlation_input_target.png`（相関係数ヒートマップ）以外の図を指すと解釈した．具体的には Feature Importance 棒グラフ（`feature_importance_*.png`）および Box-Plot（`boxplot_*.png`）が対象である．
- これらの図は従来 `COLOR_BLUE`（青）／`COLOR_RED`（赤）で色分けしていたが，本指示に基づき色相（Hue）を持たない灰色階調（モノクロ）に変更した．
- 相関係数ヒートマップは `.orders/order_003.md`／`.orders/order_004.md` の指示（「この画像のみカラーで 1.0 が赤，0 が白，-1.0 を青」）により意図的にカラーとしている図であるため，本指示の対象外として変更していない．
