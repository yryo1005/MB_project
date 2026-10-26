"""相関係数ヒートマップを転置（横長）した図を別ファイルとして生成する（既存の図は上書きしない）."""

from __future__ import annotations

from data import compute_input_target_correlation, get_selected_targets, load_dataset
from figures import plot_correlation_heatmap
from run_figures import CSV_PATH, _build_correlation_display_df
from run_figures_large import FONT_SIZE_HEATMAP, LARGE_FIGURE_DIR

FIGSIZE_HEATMAP_TRANSPOSED = (9.0, 3.0)


def main() -> None:
    """転置した横長の相関係数ヒートマップを生成する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    _, target_names, target_indices = get_selected_targets(targets)

    corr_df = compute_input_target_correlation(
        inputs, targets, feature_names, target_names, target_indices
    )
    plot_correlation_heatmap(
        _build_correlation_display_df(corr_df),
        LARGE_FIGURE_DIR / "figure2_correlation_coefficient_transposed.png",
        figsize=FIGSIZE_HEATMAP_TRANSPOSED,
        font_size=FONT_SIZE_HEATMAP,
        transpose=True,
    )
    print(f"Saved to: {LARGE_FIGURE_DIR}")


if __name__ == "__main__":
    main()
