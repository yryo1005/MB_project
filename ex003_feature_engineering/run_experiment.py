"""ex003: 組み合わせ特徴量（積・逆数・比）による UFB 濃度への寄与探索．"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data import (
    FEATURE_NAMES,
    TARGET_KEYS,
    UFB_TARGET_NAME,
    build_engineered_features,
    build_groups,
    load_dataset,
)
from figures import plot_scatter_feature_target, plot_top_feature_importance
from train import (
    compute_feature_importance,
    compute_permutation_importance,
    evaluate_models,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "MB_data_v4.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "ex003_feature_engineering"
FIGURE_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"

TOP_K = 15


def _save_csv_and_markdown(df: pd.DataFrame, stem: str) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLE_DIR / f"{stem}.csv", index=False)
    with open(TABLE_DIR / f"{stem}.md", "w", encoding="utf-8") as file:
        file.write(df.to_markdown(index=False, floatfmt=".5f"))


def main() -> None:
    """基礎説明変数のみのモデルと，組み合わせ特徴量を加えたモデルを比較し，UFB 濃度への寄与因子を探索する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    groups = build_groups(inputs)
    ufb_idx = TARGET_KEYS[UFB_TARGET_NAME]
    # train.py の各関数は標準化済み目的変数を受け取る仕様のため，ここで標準化する
    # （ex002_figure_set/run_figures.py の run_all_targets 内部処理と同一の定義）．
    normalized_targets = (targets - targets.mean(axis=0)) / targets.std(axis=0)

    combined_inputs, combined_names, kinds = build_engineered_features(inputs, feature_names)
    print(f"Base features: {len(feature_names)}, Combined features: {len(combined_names)}")

    # --- ベースライン（基礎説明変数 6 個のみ）---
    baseline_results = evaluate_models(inputs, normalized_targets, ufb_idx, groups)
    baseline_rf_row = baseline_results[baseline_results["Model"] == "Random Forest"].iloc[0]

    # --- 拡張モデル（基礎説明変数 + 組み合わせ特徴量 57 個）---
    expanded_results = evaluate_models(combined_inputs, normalized_targets, ufb_idx, groups)
    expanded_rf_row = expanded_results[expanded_results["Model"] == "Random Forest"].iloc[0]

    # --- 拡張モデルの Feature Importance (MDI) ---
    mdi_importance = compute_feature_importance(combined_inputs, normalized_targets, ufb_idx, groups)
    mdi_df = pd.DataFrame(
        {
            "Feature": combined_names,
            "Kind": kinds,
            "Feature importance (MDI)": mdi_importance,
        }
    ).sort_values("Feature importance (MDI)", ascending=False)
    _save_csv_and_markdown(mdi_df, "feature_importance_mdi")

    plot_top_feature_importance(
        combined_names,
        mdi_importance,
        kinds,
        FIGURE_DIR / "feature_importance_mdi_top15.png",
        top_k=TOP_K,
        xlabel="Feature importance (MDI)",
    )

    # --- 拡張モデルの Permutation Importance ---
    perm_df = compute_permutation_importance(
        combined_inputs, normalized_targets, ufb_idx, groups, combined_names
    )
    perm_df = perm_df.merge(
        pd.DataFrame({"Feature": combined_names, "Kind": kinds}), on="Feature", how="left"
    )
    _save_csv_and_markdown(perm_df, "permutation_importance")

    plot_top_feature_importance(
        perm_df["Feature"].tolist(),
        perm_df["Permutation importance (RMSE increase)"].tolist(),
        perm_df["Kind"].tolist(),
        FIGURE_DIR / "permutation_importance_top15.png",
        top_k=TOP_K,
        xlabel="Permutation importance (RMSE increase)",
    )

    # --- 基礎説明変数以外で最も寄与が大きい特徴量を散布図で確認 ---
    engineered_perm = perm_df[perm_df["Kind"] != "base"].reset_index(drop=True)
    top_engineered_name = engineered_perm.loc[0, "Feature"]
    top_engineered_idx = combined_names.index(top_engineered_name)
    plot_scatter_feature_target(
        combined_inputs[:, top_engineered_idx],
        targets[:, ufb_idx],
        top_engineered_name,
        UFB_TARGET_NAME,
        FIGURE_DIR / "scatter_top_engineered_feature.png",
    )

    # --- アブレーション: 最重要特徴量のみを加えた場合の予測精度 ---
    base_plus_top1_inputs = combined_inputs[:, list(range(len(feature_names))) + [top_engineered_idx]]
    base_plus_top1_results = evaluate_models(base_plus_top1_inputs, normalized_targets, ufb_idx, groups)
    base_plus_top1_rf_row = base_plus_top1_results[
        base_plus_top1_results["Model"] == "Random Forest"
    ].iloc[0]

    top1_only_inputs = combined_inputs[:, [top_engineered_idx]]
    top1_only_results = evaluate_models(top1_only_inputs, normalized_targets, ufb_idx, groups)
    top1_only_rf_row = top1_only_results[top1_only_results["Model"] == "Random Forest"].iloc[0]

    comparison = pd.DataFrame(
        [
            {
                "Feature set": "Base (6 features)",
                "Train RMSE": baseline_rf_row["Train RMSE"],
                "Test RMSE": baseline_rf_row["Test RMSE"],
            },
            {
                "Feature set": f"Base + Engineered ({len(combined_names)} features)",
                "Train RMSE": expanded_rf_row["Train RMSE"],
                "Test RMSE": expanded_rf_row["Test RMSE"],
            },
            {
                "Feature set": "Base + Top-1 engineered feature (7 features)",
                "Train RMSE": base_plus_top1_rf_row["Train RMSE"],
                "Test RMSE": base_plus_top1_rf_row["Test RMSE"],
            },
            {
                "Feature set": "Top-1 engineered feature only (1 feature)",
                "Train RMSE": top1_only_rf_row["Train RMSE"],
                "Test RMSE": top1_only_rf_row["Test RMSE"],
            },
        ]
    )
    _save_csv_and_markdown(comparison, "rmse_comparison")

    manifest = {
        "csv_path": str(CSV_PATH),
        "output_dir": str(OUTPUT_DIR),
        "n_base_features": len(feature_names),
        "n_combined_features": len(combined_names),
        "baseline_test_rmse": float(baseline_rf_row["Test RMSE"]),
        "expanded_test_rmse": float(expanded_rf_row["Test RMSE"]),
        "base_plus_top1_test_rmse": float(base_plus_top1_rf_row["Test RMSE"]),
        "top1_only_test_rmse": float(top1_only_rf_row["Test RMSE"]),
        "top_mdi_feature": mdi_df.iloc[0]["Feature"],
        "top_mdi_kind": mdi_df.iloc[0]["Kind"],
        "top_engineered_feature_by_permutation": top_engineered_name,
        "top_engineered_feature_permutation_importance": float(
            engineered_perm.loc[0, "Permutation importance (RMSE increase)"]
        ),
    }
    with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    print(f"Outputs saved to: {OUTPUT_DIR}")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
