"""MB_data_v4.csv の読み込みと統計量計算."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# 説明変数（6）
FEATURE_NAMES: List[str] = [
    "Dissolve tube [m]",
    "Dissolution pressure [MPa]",
    "Discharge tube [m]",
    "Flow speed (oxygen) [mL/min]",
    "Flow speed (water) [mL/min]",
    "Water volume [mL]",
]

# 目的変数（3）: teacher_signals 内インデックス -> 表示名
TARGET_KEYS: Dict[str, int] = {
    "MB concentration [particles/mL]": 3,
    "UFB concentration [×10^7 particles/mL]": 2,
    "Oxygen content [mg/L]": 5,
}

TARGET_NAMES: List[str] = list(TARGET_KEYS.keys())


def load_dataset(csv_path: str | Path) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """
    CSV データセットを読み込み，説明変数と目的変数に分割する．

    Args:
        csv_path (str | Path): CSV ファイルパス

    Returns:
        Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
            inputs (n_samples, 6),
            targets (n_samples, 6),
            feature_names (6,),
            all_target_names (6,)
    """
    inputs: List[List[float]] = []
    targets: List[List[float]] = []
    all_target_names: List[str] = []

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row_idx, row in enumerate(reader):
            if row_idx == 0:
                header = [
                    cell.strip()
                    .replace("\ufeff", "")
                    .replace("\n", "")
                    .replace("\u3000", "")
                    for cell in row
                ]
                all_target_names = header[6:]
                continue
            values = list(map(float, row))
            inputs.append(values[:6])
            targets.append(values[6:])

    return (
        np.array(inputs, dtype=float),
        np.array(targets, dtype=float),
        FEATURE_NAMES.copy(),
        all_target_names,
    )


def build_groups(inputs: np.ndarray) -> np.ndarray:
    """
    同一操作条件ごとにグループ ID を付与する．

    Args:
        inputs (np.ndarray): 説明変数，shape (n_samples, n_features)

    Returns:
        np.ndarray: グループ ID，shape (n_samples,)
    """
    condition_to_group: Dict[Tuple[float, ...], int] = {}
    groups = np.zeros(len(inputs), dtype=int)
    for idx, sample in enumerate(inputs):
        key = tuple(sample.tolist())
        if key not in condition_to_group:
            condition_to_group[key] = len(condition_to_group)
        groups[idx] = condition_to_group[key]
    return groups


def normalize_targets(targets: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    目的変数を標準化する．

    Args:
        targets (np.ndarray): 目的変数，shape (n_samples, n_targets)

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]:
            normalized (n_samples, n_targets),
            mean (n_targets,),
            std (n_targets,)
    """
    target_mean = targets.mean(axis=0)
    target_std = targets.std(axis=0)
    normalized = (targets - target_mean) / target_std
    return normalized, target_mean, target_std


def compute_cv_and_within_group_std(
    inputs: np.ndarray,
    targets: np.ndarray,
    target_names: List[str],
) -> pd.DataFrame:
    """
    各目的変数の CV と条件内平均標準偏差を計算する．

    ex001_base_model/main.ipynb と同様，全体 CV は $\sigma/\mu$，郡内標準偏差は
    標準化後の目的変数について同一操作条件内の標準偏差の平均とする．

    Args:
        inputs (np.ndarray): 説明変数，shape (n_samples, n_features)
        targets (np.ndarray): 目的変数，shape (n_samples, n_targets)
        target_names (List[str]): 目的変数名リスト

    Returns:
        pd.DataFrame: columns=[Target, CV, Within-group std]
    """
    normalized_targets, target_mean, target_std = normalize_targets(targets)
    cv_values = target_std / target_mean

    condition_to_samples: Dict[Tuple[float, ...], List[np.ndarray]] = {}
    for input_row, target_row in zip(inputs, normalized_targets):
        key = tuple(input_row.tolist())
        condition_to_samples.setdefault(key, []).append(target_row)

    within_stds = []
    for samples in condition_to_samples.values():
        within_stds.append(np.std(np.array(samples), axis=0))
    mean_within_std = np.mean(within_stds, axis=0)

    rows = []
    for name, cv, std in zip(target_names, cv_values, mean_within_std):
        display_name = _to_ufb_label(name)
        rows.append(
            {
                "Target": display_name,
                "CV": cv,
                "Within-group std": std,
            }
        )
    return pd.DataFrame(rows)


def compute_input_target_correlation(
    inputs: np.ndarray,
    targets: np.ndarray,
    feature_names: List[str],
    selected_target_names: List[str],
    target_indices: List[int],
) -> pd.DataFrame:
    """
    説明変数と目的変数の Pearson 相関係数を計算する．

    Args:
        inputs (np.ndarray): 説明変数，shape (n_samples, n_features)
        targets (np.ndarray): 目的変数，shape (n_samples, n_targets)
        feature_names (List[str]): 説明変数名
        selected_target_names (List[str]): 選択した目的変数名
        target_indices (List[int]): 目的変数インデックス

    Returns:
        pd.DataFrame: index=feature_names, columns=selected_target_names
    """
    corr = np.zeros((len(feature_names), len(selected_target_names)))
    for j, target_idx in enumerate(target_indices):
        y = targets[:, target_idx]
        for i in range(len(feature_names)):
            x = inputs[:, i]
            corr[i, j] = np.corrcoef(x, y)[0, 1]

    columns = [_to_ufb_label(name) for name in selected_target_names]
    return pd.DataFrame(corr, index=feature_names, columns=columns)


def get_selected_targets(targets: np.ndarray) -> Tuple[np.ndarray, List[str], List[int]]:
    """
    分析対象 3 目的変数を抽出する．

    Args:
        targets (np.ndarray): 全目的変数，shape (n_samples, 6)

    Returns:
        Tuple[np.ndarray, List[str], List[int]]:
            selected_targets (n_samples, 3),
            target_names (3,),
            target_indices (3,)
    """
    indices = [TARGET_KEYS[name] for name in TARGET_NAMES]
    selected = targets[:, indices]
    return selected, TARGET_NAMES.copy(), indices


def _to_ufb_label(name: str) -> str:
    """NB 表記を UFB 表記に置換する．"""
    name = name.replace("NB concentration", "UFB concentration")
    name = name.replace("(NB Mean)", "")
    name = name.replace("×107", "×10^7")
    return name.strip()
