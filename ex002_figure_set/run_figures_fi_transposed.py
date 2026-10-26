"""Feature Importance を転置（縦棒・縦長）した図を別ファイルとして生成する（既存の図は上書きしない）."""

from __future__ import annotations

from data import build_groups, get_selected_targets, load_dataset
from figures import plot_feature_importance
from run_figures import CSV_PATH
from run_figures_large import LARGE_FIGURE_DIR, PANEL_LETTERS, PANEL_NAMES
from train import run_all_targets

FIGSIZE_FI_TRANSPOSED = (3.5, 7.0)
FONT_SIZE_FI_TRANSPOSED = 15.0


def main() -> None:
    """転置した縦長の Feature Importance 図を生成する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    _, target_names, target_indices = get_selected_targets(targets)
    groups = build_groups(inputs)

    results = run_all_targets(inputs, targets, target_names, target_indices, groups, feature_names)
    for target_name in target_names:
        short = PANEL_NAMES[target_name]
        letter = PANEL_LETTERS[short]
        importances = results["feature_importances"][target_name]
        plot_feature_importance(
            importances,
            feature_names,
            LARGE_FIGURE_DIR / f"figure3{letter}_{short}_feature_importance_transposed.png",
            figsize=FIGSIZE_FI_TRANSPOSED,
            font_size=FONT_SIZE_FI_TRANSPOSED,
            wrap_units=False,
            transpose=True,
        )
    print(f"Saved to: {LARGE_FIGURE_DIR}")


if __name__ == "__main__":
    main()
