"""ex003 続き: Permutation Importance 順位 + 相関に基づく貪欲法で UFB 濃度への寄与特徴量を絞り込む．

モデル（Random Forest）・交差検証（5-fold GroupKFold）・特徴量生成（積・逆数・比）は
run_experiment.py と同一のものを再利用し，新規に導入するのは「相関に基づく貪欲法による
特徴選択」のみとする．
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data import (
    TARGET_KEYS,
    UFB_TARGET_NAME,
    build_engineered_features,
    build_groups,
    load_dataset,
)
from figures import plot_rmse_curve, plot_scatter_feature_target, plot_top_feature_importance
from run_experiment import CSV_PATH, FIGURE_DIR, OUTPUT_DIR, TABLE_DIR, _save_csv_and_markdown
from train import compute_feature_importance, compute_permutation_importance, evaluate_models

# 既に選択した特徴量と |Pearson r| がこの値を超える候補は，冗長であるとして除外する．
CORRELATION_THRESHOLD = 0.8
# 貪欲法で選択する特徴量数の上限．
MAX_SELECTED_FEATURES = 15


def _rf_rmse(inputs: np.ndarray, normalized_targets: np.ndarray, target_idx: int, groups: np.ndarray) -> tuple[float, float]:
    """指定した特徴量行列で Random Forest を評価し，(Train RMSE, Test RMSE) を返す．"""
    results = evaluate_models(inputs, normalized_targets, target_idx, groups)
    rf_row = results[results["Model"] == "Random Forest"].iloc[0]
    return float(rf_row["Train RMSE"]), float(rf_row["Test RMSE"])


def main() -> None:
    """相関に基づく貪欲法で特徴量を1つずつ追加し，Test RMSE が最小となる組み合わせを探索する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    groups = build_groups(inputs)
    ufb_idx = TARGET_KEYS[UFB_TARGET_NAME]
    normalized_targets = (targets - targets.mean(axis=0)) / targets.std(axis=0)

    combined_inputs, combined_names, kinds = build_engineered_features(inputs, feature_names)
    kind_of = dict(zip(combined_names, kinds))

    # --- ベースライン（基礎説明変数 6 個のみ）を参照値として再計算 ---
    baseline_train_rmse, baseline_test_rmse = _rf_rmse(inputs, normalized_targets, ufb_idx, groups)

    # --- 候補の順位付け: 57 特徴量モデルの Permutation Importance（降順）を利用 ---
    perm_df = compute_permutation_importance(
        combined_inputs, normalized_targets, ufb_idx, groups, combined_names
    )
    candidate_order = perm_df["Feature"].tolist()

    # --- 特徴量間の Pearson 相関行列（冗長な候補を除外するために使用）---
    corr_matrix = np.corrcoef(combined_inputs, rowvar=False)

    selected_idx: list[int] = []
    selected_names: list[str] = []
    progression_rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []

    for name in candidate_order:
        idx = combined_names.index(name)
        redundant_with = None
        for s_idx, s_name in zip(selected_idx, selected_names):
            if abs(corr_matrix[idx, s_idx]) > CORRELATION_THRESHOLD:
                redundant_with = s_name
                break
        if redundant_with is not None:
            skipped_rows.append(
                {
                    "Feature": name,
                    "Kind": kind_of[name],
                    "Reason": f"|r| > {CORRELATION_THRESHOLD} with '{redundant_with}'",
                }
            )
            continue

        selected_idx.append(idx)
        selected_names.append(name)
        train_rmse, test_rmse = _rf_rmse(
            combined_inputs[:, selected_idx], normalized_targets, ufb_idx, groups
        )
        progression_rows.append(
            {
                "Step": len(selected_idx),
                "Added feature": name,
                "Kind": kind_of[name],
                "n_features": len(selected_idx),
                "Train RMSE": train_rmse,
                "Test RMSE": test_rmse,
                "Test RMSE < baseline": test_rmse < baseline_test_rmse,
            }
        )
        if len(selected_idx) >= MAX_SELECTED_FEATURES:
            break

    progression_df = pd.DataFrame(progression_rows)
    _save_csv_and_markdown(progression_df, "feature_selection_progression")
    skipped_df = pd.DataFrame(skipped_rows)
    _save_csv_and_markdown(skipped_df, "feature_selection_skipped")

    plot_rmse_curve(
        progression_df["n_features"].tolist(),
        progression_df["Train RMSE"].tolist(),
        progression_df["Test RMSE"].tolist(),
        baseline_test_rmse,
        FIGURE_DIR / "feature_selection_rmse_curve.png",
    )

    best_row = progression_df.loc[progression_df["Test RMSE"].idxmin()]
    best_n = int(best_row["n_features"])
    best_names = selected_names[:best_n]
    best_idx = selected_idx[:best_n]

    # --- 最良部分集合（Test RMSE 最小）における Feature Importance ---
    best_inputs = combined_inputs[:, best_idx]
    best_mdi = compute_feature_importance(best_inputs, normalized_targets, ufb_idx, groups)
    best_mdi_df = pd.DataFrame(
        {
            "Feature": best_names,
            "Kind": [kind_of[n] for n in best_names],
            "Feature importance (MDI)": best_mdi,
        }
    ).sort_values("Feature importance (MDI)", ascending=False)
    _save_csv_and_markdown(best_mdi_df, "best_subset_feature_importance")

    plot_top_feature_importance(
        best_names,
        best_mdi,
        [kind_of[n] for n in best_names],
        FIGURE_DIR / "best_subset_feature_importance.png",
        top_k=best_n,
        figsize=(7.0, 0.6 * best_n + 1.5),
        xlabel="Feature importance (MDI)",
    )

    # --- 4 特徴量目（Test RMSE が大きく低下した要因）と UFB 濃度の関係を確認 ---
    trigger_name = best_names[-1]
    trigger_idx = combined_names.index(trigger_name)
    plot_scatter_feature_target(
        combined_inputs[:, trigger_idx],
        targets[:, ufb_idx],
        trigger_name,
        UFB_TARGET_NAME,
        FIGURE_DIR / "scatter_rmse_drop_feature.png",
    )

    manifest = {
        "correlation_threshold": CORRELATION_THRESHOLD,
        "max_selected_features": MAX_SELECTED_FEATURES,
        "n_candidates_scanned": len(candidate_order[: len(progression_rows) + len(skipped_rows)]),
        "n_selected": len(selected_names),
        "n_skipped_redundant": len(skipped_rows),
        "baseline_test_rmse": baseline_test_rmse,
        "best_n_features": int(best_row["n_features"]),
        "best_test_rmse": float(best_row["Test RMSE"]),
        "best_test_rmse_below_baseline": bool(best_row["Test RMSE"] < baseline_test_rmse),
        "selected_features_up_to_best": selected_names[: int(best_row["n_features"])],
    }
    with open(OUTPUT_DIR / "manifest_feature_selection.json", "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
