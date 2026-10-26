"""ex003 用の図の描画関数（モノクロ，最小限の線のみ）."""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

import matplotlib.pyplot as plt
import numpy as np

COLOR_DARK = "#262626"
COLOR_LIGHT = "#8C8C8C"
COLOR_BASE = "#BFBFBF"


def apply_figure_style(font_size: float = 10.0) -> None:
    """モノクロ，最小限の線のみの matplotlib スタイルを適用する．"""
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "black",
            "axes.linewidth": 0.8,
            "axes.grid": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": "black",
            "ytick.color": "black",
            "text.color": "black",
            "font.size": font_size,
            "savefig.facecolor": "white",
            "savefig.edgecolor": "white",
        }
    )


def plot_top_feature_importance(
    names: Sequence[str],
    importances: Sequence[float],
    kinds: Sequence[str],
    output_path: str | Path,
    top_k: int = 15,
    figsize: tuple[float, float] = (7.0, 6.0),
    xlabel: str = "Feature importance",
) -> None:
    """
    重要度上位 top_k 件の特徴量を横棒グラフで示す．

    説明変数の種別（base / product / reciprocal / ratio）によって色を変える．

    Args:
        names (Sequence[str]): 特徴量名，shape (n_features,)
        importances (Sequence[float]): 重要度，shape (n_features,)
        kinds (Sequence[str]): 各特徴量の種別（"base"/"product"/"reciprocal"/"ratio"）
        output_path (str | Path): 保存先 PNG パス
        top_k (int): 表示する上位件数
        figsize (tuple[float, float]): 図サイズ
        xlabel (str): 横軸ラベル
    """
    apply_figure_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    order = np.argsort(importances)[::-1][:top_k]
    sorted_names = [names[i] for i in order]
    sorted_values = [importances[i] for i in order]
    sorted_kinds = [kinds[i] for i in order]

    color_map = {
        "base": COLOR_BASE,
        "product": COLOR_LIGHT,
        "reciprocal": COLOR_LIGHT,
        "ratio": COLOR_DARK,
    }
    bar_colors = [color_map[k] for k in sorted_kinds]

    fig, ax = plt.subplots(figsize=figsize)
    ax.barh(range(len(sorted_names)), sorted_values, color=bar_colors, edgecolor="black", linewidth=0.5)
    ax.set_yticks(range(len(sorted_names)))
    ax.set_yticklabels(sorted_names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=color_map[k], edgecolor="black", linewidth=0.5)
        for k in ["base", "product", "reciprocal", "ratio"]
    ]
    ax.legend(handles, ["base", "product", "reciprocal", "ratio"], loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_scatter_feature_target(
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str,
    ylabel: str,
    output_path: str | Path,
    figsize: tuple[float, float] = (5.0, 5.0),
) -> None:
    """
    特徴量と目的変数の散布図を描画する．

    Args:
        x (np.ndarray): 特徴量，shape (n_samples,)
        y (np.ndarray): 目的変数，shape (n_samples,)
        xlabel (str): x 軸ラベル
        ylabel (str): y 軸ラベル
        output_path (str | Path): 保存先 PNG パス
        figsize (tuple[float, float]): 図サイズ
    """
    apply_figure_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y, color=COLOR_DARK, edgecolor="black", linewidth=0.5, s=30)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_rmse_curve(
    n_features: Sequence[int],
    train_rmse: Sequence[float],
    test_rmse: Sequence[float],
    baseline_test_rmse: float,
    output_path: str | Path,
    figsize: tuple[float, float] = (6.0, 5.0),
) -> None:
    """
    貪欲法による特徴選択の過程で，特徴量数ごとの Train/Test RMSE を折れ線で示す．

    Args:
        n_features (Sequence[int]): 選択済み特徴量数，shape (n_steps,)
        train_rmse (Sequence[float]): 各ステップの Train RMSE，shape (n_steps,)
        test_rmse (Sequence[float]): 各ステップの Test RMSE，shape (n_steps,)
        baseline_test_rmse (float): 基礎説明変数 6 個のみのベースライン Test RMSE（水平線で表示）
        output_path (str | Path): 保存先 PNG パス
        figsize (tuple[float, float]): 図サイズ
    """
    apply_figure_style()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(n_features, train_rmse, marker="o", color=COLOR_LIGHT, label="Train RMSE")
    ax.plot(n_features, test_rmse, marker="o", color=COLOR_DARK, label="Test RMSE")
    ax.axhline(
        baseline_test_rmse,
        color="black",
        linestyle="--",
        linewidth=0.8,
        label="Baseline Test RMSE (6 base features)",
    )
    ax.set_xlabel("Number of selected features")
    ax.set_ylabel("RMSE (standardized)")
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
