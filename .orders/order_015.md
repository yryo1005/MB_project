Feature Imortanceの図だけ縦３横５くらいの横長にして，項目の文字の開業を無くす

---

## 解釈・対応記録

- Feature Importance の図のみ，縦3：横5（7.5×4.5 inch，300 dpi）の横長に変更し，縦軸ラベルの単位前の改行を廃止した（`wrap_units=False`）．箱ひげ図・相関ヒートマップは変更していない．
- 横長の図を横に3枚並べると文字が小さくなるため，論文中の図3は (A)(B)(C) を縦に積む配置に変更した．
- 既存の図は上書きせず，`*_large.png` を再生成（`outputs/ex002_figure_set/figures_large/`）して `paper/figures/` の同名 `_large` ファイルを更新した．
