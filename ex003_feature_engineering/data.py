"""MB_data_v4.csv の読み込みと，組み合わせ特徴量（積・逆数・比）の生成."""

from __future__ import annotations

import csv
import itertools
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# 説明変数（6）: ex002_figure_set/data.py と同一
FEATURE_NAMES: List[str] = [
    "Dissolve tube [m]",
    "Dissolution pressure [MPa]",
    "Discharge tube [m]",
    "Flow speed (oxygen) [mL/min]",
    "Flow speed (water) [mL/min]",
    "Water volume [mL]",
]

# 目的変数（3）: teacher_signals 内インデックス -> 表示名．本実験では UFB concentration のみを用いる．
TARGET_KEYS: Dict[str, int] = {
    "MB concentration [particles/mL]": 3,
    "UFB concentration [×10^7 particles/mL]": 2,
    "Oxygen content [mg/L]": 5,
}
UFB_TARGET_NAME = "UFB concentration [×10^7 particles/mL]"


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
                    .replace("﻿", "")
                    .replace("\n", "")
                    .replace("　", "")
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


def build_engineered_features(
    inputs: np.ndarray,
    feature_names: List[str],
) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    基礎説明変数から，積・逆数・比による組み合わせ特徴量を生成する．

    基礎説明変数はいずれも正の値のみを取るため（データセット中に 0 以下の値はない），
    逆数・比の計算で 0 除算は発生しない．

    生成する特徴量:
        - 積: 相異なる 2 変数の組み合わせすべて（$ {}_6C_2 = 15 $ 種）
        - 逆数: 各変数の逆数（6 種）
        - 比: 相異なる 2 変数の有向な組み合わせすべて（$ x_i / x_j $，$ i \\neq j $，$ 6 \\times 5 = 30 $ 種）

    Args:
        inputs (np.ndarray): 基礎説明変数，shape (n_samples, 6)
        feature_names (List[str]): 基礎説明変数名，shape (6,)

    Returns:
        Tuple[np.ndarray, List[str], List[str]]:
            combined_inputs (n_samples, 6 + 51): 基礎説明変数 + 組み合わせ特徴量,
            combined_names (6 + 51,): 対応する名前,
            engineered_kind (6 + 51,): 各列の種別（"base" / "product" / "reciprocal" / "ratio"）
    """
    if np.any(inputs <= 0.0):
        raise ValueError("逆数・比の計算には全説明変数が正の値である必要があります．")

    n_features = len(feature_names)
    columns: List[np.ndarray] = [inputs[:, i] for i in range(n_features)]
    names: List[str] = list(feature_names)
    kinds: List[str] = ["base"] * n_features

    for i, j in itertools.combinations(range(n_features), 2):
        columns.append(inputs[:, i] * inputs[:, j])
        names.append(f"{feature_names[i]} * {feature_names[j]}")
        kinds.append("product")

    for i in range(n_features):
        columns.append(1.0 / inputs[:, i])
        names.append(f"1 / ({feature_names[i]})")
        kinds.append("reciprocal")

    for i, j in itertools.permutations(range(n_features), 2):
        columns.append(inputs[:, i] / inputs[:, j])
        names.append(f"({feature_names[i]}) / ({feature_names[j]})")
        kinds.append("ratio")

    combined_inputs = np.stack(columns, axis=1)
    return combined_inputs, names, kinds
