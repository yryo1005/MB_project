"""slim（縦の解像度を保ったまま横を狭くした）図を別ファイルとして生成する（既存の図は上書きしない）."""

from __future__ import annotations

from data import compute_input_target_correlation, get_selected_targets, load_dataset, build_groups
from figures import plot_boxplot_feature_target, plot_correlation_heatmap, plot_feature_importance
from run_figures_large import (
    FONT_SIZE_FI,
    FONT_SIZE_PANEL,
    LARGE_FIGURE_DIR,
    PANEL_LETTERS,
    PANEL_NAMES,
)
from run_figures import CSV_PATH, _build_correlation_display_df
from train import run_all_targets

# 各 _large 図と同じ高さ [inch]（＝縦の解像度）を維持し，幅のみ縮小する．
# ヒートマップは列数が少なく余白が広いため，注釈同士が重ならない範囲で最も幅を絞った値とした．
SLIM_HEIGHT_HEATMAP = 5.3
SLIM_WIDTH_HEATMAP = 4.5
SLIM_FONT_SIZE_HEATMAP = 11.0
SLIM_HEIGHT_PANEL = 5.0
SLIM_WIDTH_PANEL = 4.2
SLIM_HEIGHT_FI = 4.5
SLIM_WIDTH_FI = 3.0


def main() -> None:
    """slim 版の相関ヒートマップ，Feature Importance，箱ひげ図を生成する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    _, target_names, target_indices = get_selected_targets(targets)
    groups = build_groups(inputs)

    corr_df = compute_input_target_correlation(
        inputs, targets, feature_names, target_names, target_indices
    )
    plot_correlation_heatmap(
        _build_correlation_display_df(corr_df),
        LARGE_FIGURE_DIR / "figure2_correlation_coefficient_slim.png",
        figsize=(SLIM_WIDTH_HEATMAP, SLIM_HEIGHT_HEATMAP),
        font_size=SLIM_FONT_SIZE_HEATMAP,
    )

    results = run_all_targets(inputs, targets, target_names, target_indices, groups, feature_names)
    for target_name, target_idx in zip(target_names, target_indices):
        short = PANEL_NAMES[target_name]
        letter = PANEL_LETTERS[short]
        importances = results["feature_importances"][target_name]
        plot_feature_importance(
            importances,
            feature_names,
            LARGE_FIGURE_DIR / f"figure3{letter}_{short}_feature_importance_slim.png",
            figsize=(SLIM_WIDTH_FI, SLIM_HEIGHT_FI),
            font_size=FONT_SIZE_FI,
            wrap_units=True,
        )
        top_idx = int(importances.argmax())
        plot_boxplot_feature_target(
            inputs[:, top_idx],
            targets[:, target_idx],
            feature_names[top_idx],
            target_name.replace(" [", "\n["),
            LARGE_FIGURE_DIR / f"figure4{letter}_{short}_box_plot_slim.png",
            figsize=(SLIM_WIDTH_PANEL, SLIM_HEIGHT_PANEL),
            font_size=FONT_SIZE_PANEL,
        )
    print(f"Saved to: {LARGE_FIGURE_DIR}")


if __name__ == "__main__":
    main()
