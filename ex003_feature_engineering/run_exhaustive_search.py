"""ex003 続き: Permutation Importance 上位候補に限定した厳密な全部分集合探索．

report_020（貪欲法）は相関閾値によって候補を逐次的に除外するため，閾値の設定次第で
真に最良な組み合わせを見落とす可能性がある．本スクリプトは，Permutation Importance
上位 `CANDIDATE_POOL_SIZE` 件に候補を絞った上で，サイズ 1〜`MAX_SUBSET_SIZE` の
全部分集合を厳密に探索し，Test RMSE を最小化する組み合わせを求める．
モデル（Random Forest）・交差検証（5-fold GroupKFold）・特徴量生成は
run_experiment.py / run_feature_selection.py と同一のものを再利用する．
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold

from data import (
    TARGET_KEYS,
    UFB_TARGET_NAME,
    build_engineered_features,
    build_groups,
    load_dataset,
)
from figures import plot_rmse_curve, plot_top_feature_importance
from run_experiment import CSV_PATH, FIGURE_DIR, OUTPUT_DIR, _save_csv_and_markdown
from train import (
    N_SPLITS,
    RANDOM_STATE,
    RF_MAX_DEPTH,
    RF_N_ESTIMATORS,
    compute_feature_importance,
    compute_permutation_importance,
    evaluate_models,
)

# Permutation Importance 上位何件を全探索の候補プールとするか．
CANDIDATE_POOL_SIZE = 15
# 全探索する部分集合の最大サイズ（1 からこのサイズまで全て探索する）．
MAX_SUBSET_SIZE = 5
# 探索フェーズで用いる決定木数（最終評価では RF_N_ESTIMATORS=100 で再評価する）．
SEARCH_N_ESTIMATORS = 30
# 各サイズごとに表へ保存する上位件数．
TOP_N_PER_SIZE = 5


def _fast_rf_test_rmse(
    inputs: np.ndarray,
    y: np.ndarray,
    splits: list[tuple[np.ndarray, np.ndarray]],
    n_estimators: int,
) -> float:
    """探索を高速化するための軽量 RF 交差検証（Test RMSE のみ計算）．"""
    test_scores = []
    for train_idx, test_idx in splits:
        model = RandomForestRegressor(
            n_estimators=n_estimators, max_depth=RF_MAX_DEPTH, random_state=RANDOM_STATE
        )
        model.fit(inputs[train_idx], y[train_idx])
        pred = model.predict(inputs[test_idx])
        test_scores.append(float(np.sqrt(mean_squared_error(y[test_idx], pred))))
    return float(np.mean(test_scores))


def main() -> None:
    """Permutation Importance 上位候補について，部分集合サイズ 1〜5 を全探索する．"""
    inputs, targets, feature_names, _ = load_dataset(CSV_PATH)
    groups = build_groups(inputs)
    ufb_idx = TARGET_KEYS[UFB_TARGET_NAME]
    normalized_targets = (targets - targets.mean(axis=0)) / targets.std(axis=0)
    y = normalized_targets[:, ufb_idx]

    combined_inputs, combined_names, kinds = build_engineered_features(inputs, feature_names)
    kind_of = dict(zip(combined_names, kinds))

    baseline_results = evaluate_models(inputs, normalized_targets, ufb_idx, groups)
    baseline_test_rmse = float(
        baseline_results[baseline_results["Model"] == "Random Forest"].iloc[0]["Test RMSE"]
    )

    perm_df = compute_permutation_importance(
        combined_inputs, normalized_targets, ufb_idx, groups, combined_names
    )
    pool_names = perm_df["Feature"].head(CANDIDATE_POOL_SIZE).tolist()
    pool_idx = [combined_names.index(n) for n in pool_names]
    print(f"Candidate pool ({CANDIDATE_POOL_SIZE}): {pool_names}")

    gkf = GroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    splits = list(gkf.split(combined_inputs, normalized_targets, groups=groups))

    all_results: list[dict[str, object]] = []
    start = time.time()
    n_evaluated = 0
    for size in range(1, MAX_SUBSET_SIZE + 1):
        for combo in itertools.combinations(range(len(pool_idx)), size):
            feature_idx = [pool_idx[i] for i in combo]
            test_rmse = _fast_rf_test_rmse(
                combined_inputs[:, feature_idx], y, splits, SEARCH_N_ESTIMATORS
            )
            all_results.append(
                {
                    "Size": size,
                    "Features": " + ".join(pool_names[i] for i in combo),
                    "Test RMSE (search, n_estimators=30)": test_rmse,
                }
            )
            n_evaluated += 1
    elapsed = time.time() - start
    print(f"Evaluated {n_evaluated} subsets in {elapsed:.1f} s")

    results_df = pd.DataFrame(all_results).sort_values(
        "Test RMSE (search, n_estimators=30)"
    )
    _save_csv_and_markdown(results_df.head(50).reset_index(drop=True), "exhaustive_search_top50")

    # --- サイズごとの最良部分集合を抽出し，RF_N_ESTIMATORS=100 で再評価 ---
    best_per_size_rows = []
    for size in range(1, MAX_SUBSET_SIZE + 1):
        size_df = results_df[results_df["Size"] == size]
        best_row = size_df.iloc[0]
        best_feature_names = best_row["Features"].split(" + ")
        best_feature_idx = [combined_names.index(n) for n in best_feature_names]
        verified_test_rmse = _fast_rf_test_rmse(
            combined_inputs[:, best_feature_idx], y, splits, RF_N_ESTIMATORS
        )
        verify_results = evaluate_models(
            combined_inputs[:, best_feature_idx], normalized_targets, ufb_idx, groups
        )
        verify_rf_row = verify_results[verify_results["Model"] == "Random Forest"].iloc[0]
        best_per_size_rows.append(
            {
                "Size": size,
                "Features": best_row["Features"],
                "Test RMSE (search, n_estimators=30)": best_row["Test RMSE (search, n_estimators=30)"],
                "Train RMSE (n_estimators=100)": float(verify_rf_row["Train RMSE"]),
                "Test RMSE (n_estimators=100)": float(verify_rf_row["Test RMSE"]),
            }
        )
    best_per_size_df = pd.DataFrame(best_per_size_rows)
    _save_csv_and_markdown(best_per_size_df, "exhaustive_search_best_per_size")

    plot_rmse_curve(
        best_per_size_df["Size"].tolist(),
        best_per_size_df["Train RMSE (n_estimators=100)"].tolist(),
        best_per_size_df["Test RMSE (n_estimators=100)"].tolist(),
        baseline_test_rmse,
        FIGURE_DIR / "exhaustive_search_rmse_curve.png",
    )

    global_best = best_per_size_df.loc[best_per_size_df["Test RMSE (n_estimators=100)"].idxmin()]
    global_best_names = global_best["Features"].split(" + ")
    global_best_idx = [combined_names.index(n) for n in global_best_names]

    global_best_mdi = compute_feature_importance(
        combined_inputs[:, global_best_idx], normalized_targets, ufb_idx, groups
    )
    global_best_mdi_df = pd.DataFrame(
        {
            "Feature": global_best_names,
            "Kind": [kind_of[n] for n in global_best_names],
            "Feature importance (MDI)": global_best_mdi,
        }
    ).sort_values("Feature importance (MDI)", ascending=False)
    _save_csv_and_markdown(global_best_mdi_df, "exhaustive_search_best_feature_importance")

    plot_top_feature_importance(
        global_best_names,
        global_best_mdi,
        [kind_of[n] for n in global_best_names],
        FIGURE_DIR / "exhaustive_search_best_feature_importance.png",
        top_k=len(global_best_names),
        figsize=(7.0, 0.6 * len(global_best_names) + 1.5),
        xlabel="Feature importance (MDI)",
    )

    manifest = {
        "candidate_pool_size": CANDIDATE_POOL_SIZE,
        "candidate_pool": pool_names,
        "max_subset_size": MAX_SUBSET_SIZE,
        "n_subsets_evaluated": n_evaluated,
        "search_elapsed_seconds": elapsed,
        "baseline_test_rmse": baseline_test_rmse,
        "previous_greedy_best_test_rmse": 0.8442446670645374,
        "global_best_size": int(global_best["Size"]),
        "global_best_features": global_best_names,
        "global_best_test_rmse": float(global_best["Test RMSE (n_estimators=100)"]),
        "improved_over_greedy": bool(
            global_best["Test RMSE (n_estimators=100)"] < 0.8442446670645374
        ),
    }
    with open(OUTPUT_DIR / "manifest_exhaustive_search.json", "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, ensure_ascii=False)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
