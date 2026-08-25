"""モデル学習，評価，Permutation Importance 計算."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from tqdm import tqdm

N_SPLITS = 5
RANDOM_STATE = 0
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 5


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """RMSE を計算する．"""
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def evaluate_models(
    inputs: np.ndarray,
    normalized_targets: np.ndarray,
    target_idx: int,
    groups: np.ndarray,
) -> pd.DataFrame:
    """
    3 モデルの GroupKFold 交差検証 RMSE を計算する．

    Args:
        inputs (np.ndarray): 説明変数，shape (n_samples, n_features)
        normalized_targets (np.ndarray): 標準化済み目的変数，shape (n_samples, n_targets)
        target_idx (int): teacher_signals 内の目的変数インデックス
        groups (np.ndarray): グループ ID，shape (n_samples,)

    Returns:
        pd.DataFrame: columns=[Model, Train RMSE, Test RMSE]
    """
    gkf = GroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    model_specs = {
        "Linear regression": LinearRegression(),
        "Polynomial regression": make_pipeline(PolynomialFeatures(2), LinearRegression()),
        "Random Forest": RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_STATE,
        ),
    }

    rows = []
    y_all = normalized_targets[:, target_idx]

    for model_name, estimator in model_specs.items():
        train_scores: List[float] = []
        test_scores: List[float] = []

        for train_idx, test_idx in gkf.split(inputs, normalized_targets, groups=groups):
            x_train, x_test = inputs[train_idx], inputs[test_idx]
            y_train, y_test = y_all[train_idx], y_all[test_idx]

            model = clone(estimator)
            if model_name == "Polynomial regression":
                model.fit(x_train, y_train)
            else:
                model.fit(x_train, y_train)

            train_pred = model.predict(x_train)
            test_pred = model.predict(x_test)
            train_scores.append(_rmse(y_train, train_pred))
            test_scores.append(_rmse(y_test, test_pred))

        rows.append(
            {
                "Model": model_name,
                "Train RMSE": float(np.mean(train_scores)),
                "Test RMSE": float(np.mean(test_scores)),
            }
        )

    return pd.DataFrame(rows)


def compute_feature_importance(
    inputs: np.ndarray,
    normalized_targets: np.ndarray,
    target_idx: int,
    groups: np.ndarray,
) -> np.ndarray:
    """
    Random Forest の Feature Importance を fold 平均で計算する．

    Args:
        inputs (np.ndarray): 説明変数，shape (n_samples, n_features)
        normalized_targets (np.ndarray): 標準化済み目的変数
        target_idx (int): 目的変数インデックス
        groups (np.ndarray): グループ ID

    Returns:
        np.ndarray: 平均 Feature Importance，shape (n_features,)
    """
    gkf = GroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    importances = []

    y_all = normalized_targets[:, target_idx]
    for train_idx, _ in gkf.split(inputs, normalized_targets, groups=groups):
        model = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_STATE,
        )
        model.fit(inputs[train_idx], y_all[train_idx])
        importances.append(model.feature_importances_)

    return np.mean(importances, axis=0)


def compute_permutation_importance(
    inputs: np.ndarray,
    normalized_targets: np.ndarray,
    target_idx: int,
    groups: np.ndarray,
    feature_names: List[str],
) -> pd.DataFrame:
    """
    各特徴量の Permutation Importance（RMSE 増分）を fold 平均で計算する．

    Args:
        inputs (np.ndarray): 説明変数
        normalized_targets (np.ndarray): 標準化済み目的変数
        target_idx (int): 目的変数インデックス
        groups (np.ndarray): グループ ID
        feature_names (List[str]): 説明変数名

    Returns:
        pd.DataFrame: columns=[Feature, Permutation importance (RMSE increase)]
    """
    gkf = GroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    fold_importances = np.zeros((N_SPLITS, len(feature_names)))
    y_all = normalized_targets[:, target_idx]

    splits = list(gkf.split(inputs, normalized_targets, groups=groups))
    for fold_idx, (train_idx, test_idx) in enumerate(
        tqdm(splits, desc="Permutation importance", leave=False)
    ):
        model = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_STATE,
        )
        model.fit(inputs[train_idx], y_all[train_idx])

        result = permutation_importance(
            model,
            inputs[test_idx],
            y_all[test_idx],
            n_repeats=10,
            random_state=RANDOM_STATE,
            scoring="neg_root_mean_squared_error",
        )
        fold_importances[fold_idx] = result.importances_mean

    mean_importance = fold_importances.mean(axis=0)
    return pd.DataFrame(
        {
            "Feature": feature_names,
            "Permutation importance (RMSE increase)": mean_importance,
        }
    ).sort_values("Permutation importance (RMSE increase)", ascending=False)


def run_all_targets(
    inputs: np.ndarray,
    targets: np.ndarray,
    target_names: List[str],
    target_indices: List[int],
    groups: np.ndarray,
    feature_names: List[str],
) -> Dict[str, object]:
    """
    全目的変数に対するモデル評価と重要度計算を実行する．

    Args:
        inputs (np.ndarray): 説明変数
        targets (np.ndarray): 全目的変数（6 列）
        target_names (List[str]): 分析対象目的変数名（3）
        target_indices (List[int]): teacher_signals 内インデックス（3）
        groups (np.ndarray): グループ ID
        feature_names (List[str]): 説明変数名

    Returns:
        Dict[str, object]: 結果辞書
    """
    ts_mean = targets.mean(axis=0)
    ts_std = targets.std(axis=0)
    normalized_targets = (targets - ts_mean) / ts_std

    model_results: Dict[str, pd.DataFrame] = {}
    feature_importances: Dict[str, np.ndarray] = {}
    permutation_tables: Dict[str, pd.DataFrame] = {}

    for name, idx in zip(target_names, target_indices):
        model_results[name] = evaluate_models(inputs, normalized_targets, idx, groups)
        feature_importances[name] = compute_feature_importance(
            inputs, normalized_targets, idx, groups
        )
        permutation_tables[name] = compute_permutation_importance(
            inputs, normalized_targets, idx, groups, feature_names
        )

    return {
        "model_results": model_results,
        "feature_importances": feature_importances,
        "permutation_tables": permutation_tables,
    }
