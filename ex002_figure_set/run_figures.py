"""Figure Set 生成のエントリポイント."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from data import (
    TARGET_NAMES,
    build_groups,
    compute_cv_and_within_group_std,
    compute_input_target_correlation,
    get_selected_targets,
    load_dataset,
)
from figures import (
    plot_boxplot_feature_target,
    plot_correlation_heatmap,
    plot_feature_importance,
    save_table_markdown,
)
from train import run_all_targets

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "MB_data_v4.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "ex002_figure_set"
FIGURE_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"


def _slugify(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "_")
        .replace("[", "")
        .replace("]", "")
        .replace("/", "_")
        .replace("×", "x")
        .replace("(", "")
        .replace(")", "")
    )


def _save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=True)


def main() -> None:
    """Figure Set と表を生成する．"""
    inputs, targets, feature_names, all_target_names = load_dataset(CSV_PATH)
    selected_targets, target_names, target_indices = get_selected_targets(targets)
    groups = build_groups(inputs)

    # 1. CV / within-group std table (all 6 targets for selection argument)
    cv_table = compute_cv_and_within_group_std(inputs, targets, all_target_names)
    cv_table_display = cv_table.copy()
    cv_table_display["CV"] = cv_table_display["CV"].map(lambda x: f"{x:.5f}")
    cv_table_display["Within-group std"] = cv_table_display["Within-group std"].map(
        lambda x: f"{x:.5f}"
    )
    _save_csv(cv_table, TABLE_DIR / "cv_within_group.csv")
    save_table_markdown(cv_table_display, TABLE_DIR / "cv_within_group.md")

    # 2. Correlation heatmap (inputs vs selected targets)
    corr_df = compute_input_target_correlation(
        inputs, targets, feature_names, target_names, target_indices
    )
    _save_csv(corr_df, TABLE_DIR / "input_target_correlation.csv")
    save_table_markdown(corr_df, TABLE_DIR / "input_target_correlation.md")
    plot_correlation_heatmap(corr_df, FIGURE_DIR / "correlation_input_target.png")

    # 3. Model training / evaluation
    results = run_all_targets(
        inputs, targets, target_names, target_indices, groups, feature_names
    )

    model_summary_rows = []
    for target_name, df in results["model_results"].items():
        for _, row in df.iterrows():
            model_summary_rows.append(
                {
                    "Target": target_name,
                    "Model": row["Model"],
                    "Train RMSE": row["Train RMSE"],
                    "Test RMSE": row["Test RMSE"],
                }
            )
    model_summary = pd.DataFrame(model_summary_rows)
    _save_csv(model_summary, TABLE_DIR / "model_comparison.csv")
    save_table_markdown(
        model_summary.set_index(["Target", "Model"]),
        TABLE_DIR / "model_comparison.md",
    )

    # 4. Feature Importance figures and Box-Plots
    boxplot_manifest = []
    for target_name in target_names:
        slug = _slugify(target_name)
        importances = results["feature_importances"][target_name]
        plot_feature_importance(
            importances,
            feature_names,
            FIGURE_DIR / f"feature_importance_{slug}.png",
            xlim_max=1.0,
        )

        top_idx = int(importances.argmax())
        top_feature = feature_names[top_idx]
        plot_boxplot_feature_target(
            inputs[:, top_idx],
            targets[:, target_indices[target_names.index(target_name)]],
            top_feature,
            target_name,
            FIGURE_DIR / f"boxplot_{slug}.png",
        )
        boxplot_manifest.append(
            {
                "target": target_name,
                "top_feature": top_feature,
                "importance": float(importances[top_idx]),
            }
        )

    # 5. Permutation importance tables
    perm_summary_rows = []
    for target_name in target_names:
        perm_df = results["permutation_tables"][target_name]
        slug = _slugify(target_name)
        _save_csv(perm_df.set_index("Feature"), TABLE_DIR / f"permutation_importance_{slug}.csv")
        save_table_markdown(perm_df.set_index("Feature"), TABLE_DIR / f"permutation_importance_{slug}.md")
        for _, row in perm_df.iterrows():
            perm_summary_rows.append(
                {
                    "Target": target_name,
                    "Feature": row["Feature"],
                    "Permutation importance (RMSE increase)": row[
                        "Permutation importance (RMSE increase)"
                    ],
                }
            )

    perm_summary = pd.DataFrame(perm_summary_rows)
    _save_csv(perm_summary, TABLE_DIR / "permutation_importance_all.csv")
    save_table_markdown(
        perm_summary.set_index(["Target", "Feature"]),
        TABLE_DIR / "permutation_importance_all.md",
    )

    manifest = {
        "csv_path": str(CSV_PATH),
        "output_dir": str(OUTPUT_DIR),
        "target_names": target_names,
        "boxplot_manifest": boxplot_manifest,
    }
    with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    print(f"Outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
