"""論文用に文字を大きくした図を別ディレクトリへ生成するスクリプト（既存の図は上書きしない）."""

from __future__ import annotations

from pathlib import Path

from data import compute_input_target_correlation, get_selected_targets, load_dataset, build_groups
from figures import (
    plot_boxplot_feature_target,
    plot_correlation_heatmap,
    plot_feature_importance,
)
from run_figures import CSV_PATH, OUTPUT_DIR, _build_correlation_display_df
from train import run_all_targets

LARGE_FIGURE_DIR = OUTPUT_DIR / "figures_large"

FONT_SIZE_HEATMAP = 15.0
FONT_SIZE_PANEL = 17.0
FIGSIZE_HEATMAP = (6.0, 5.5)
FIGSIZE_PANEL = (6.0, 5.0)
FIGSIZE_FI = (7.5, 4.5)
FONT_SIZE_FI = 16.0

# 論文で使用しているファイル名（末尾に _large を付与）に対応する目的変数の出力名
PANEL_NAMES = {
    "MB concentration [particles/mL]": "MB",
    "UFB concentration [×10^7 particles/mL]": "UFB",
    "Oxygen content [mg/L]": "Oxygen",
}
PANEL_LETTERS = {"MB": "A", "UFB": "B", "Oxygen": "C"}


def main() -> None:
    """文字を大きくした相関ヒートマップ，Feature Importance，箱ひげ図を生成する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    _, target_names, target_indices = get_selected_targets(targets)
    groups = build_groups(inputs)

    corr_df = compute_input_target_correlation(
        inputs, targets, feature_names, target_names, target_indices
    )
    plot_correlation_heatmap(
        _build_correlation_display_df(corr_df),
        LARGE_FIGURE_DIR / "figure2_correlation_coefficient_large.png",
        figsize=FIGSIZE_HEATMAP,
        font_size=FONT_SIZE_HEATMAP,
    )

    results = run_all_targets(inputs, targets, target_names, target_indices, groups, feature_names)
    for target_name, target_idx in zip(target_names, target_indices):
        short = PANEL_NAMES[target_name]
        letter = PANEL_LETTERS[short]
        importances = results["feature_importances"][target_name]
        plot_feature_importance(
            importances,
            feature_names,
            LARGE_FIGURE_DIR / f"figure3{letter}_{short}_feature_importance_large.png",
            figsize=FIGSIZE_FI,
            font_size=FONT_SIZE_FI,
            wrap_units=False,
        )
        top_idx = int(importances.argmax())
        plot_boxplot_feature_target(
            inputs[:, top_idx],
            targets[:, target_idx],
            feature_names[top_idx],
            target_name.replace(" [", "\n["),
            LARGE_FIGURE_DIR / f"figure4{letter}_{short}_box_plot_large.png",
            figsize=FIGSIZE_PANEL,
            font_size=FONT_SIZE_PANEL,
        )
    print(f"Saved to: {LARGE_FIGURE_DIR}")


if __name__ == "__main__":
    main()
