"""論文用 Figure Set の描画関数."""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COLOR_DARK = "#262626"
COLOR_LIGHT = "#8C8C8C"
COLOR_CYCLE = ["#BFBFBF", "#7F7F7F"]


def apply_figure_style(font_size: float = 10.0) -> None:
    """
    モノクロ（相関ヒートマップを除く），最小限の線のみの matplotlib スタイルを適用する．

    Args:
        font_size (float): 基準フォントサイズ [pt]
    """
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


def save_table_markdown(df: pd.DataFrame, output_path: str | Path) -> None:
    """
    DataFrame を Markdown 表として保存する．

    Args:
        df (pd.DataFrame): 保存対象
        output_path (str | Path): 出力パス
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(df.to_markdown(index=True, floatfmt=".5f"))


def plot_correlation_heatmap(
    corr_df: pd.DataFrame,
    output_path: str | Path,
    figsize: tuple[float, float] = (5.0, 5.0),
    font_size: float = 10.0,
    transpose: bool = False,
) -> None:
    """
    説明変数と目的変数の相関係数ヒートマップを描画する．

    相関係数 1.0 を赤，0 を白，-1.0 を青とするカラーマップを用いる．

    Args:
        corr_df (pd.DataFrame): 相関係数，index=features, columns=targets
        output_path (str | Path): 保存先 PNG パス
        figsize (tuple[float, float]): 図サイズ
        font_size (float): 基準フォントサイズ [pt]
        transpose (bool): True の場合，行と列を入れ替える（目的変数を縦軸，
            説明変数を横軸とし，横に長い図にする用途を想定）
    """
    apply_figure_style(font_size)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_df = corr_df.T if transpose else corr_df
    data = plot_df.values
    n_rows, n_cols = data.shape

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(data, cmap="RdBu_r", vmin=-1.0, vmax=1.0, aspect="auto")

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(plot_df.columns, rotation=35, ha="right")
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(plot_df.index)

    for i in range(n_rows):
        for j in range(n_cols):
            value = data[i, j]
            color = "white" if abs(value) > 0.5 else "black"
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=color, fontsize=font_size - 1)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson r")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_feature_importance(
    importances: Sequence[float],
    feature_names: Sequence[str],
    output_path: str | Path,
    figsize: tuple[float, float] = (5.0, 5.0),
    xlim_max: float = 100.0,
    font_size: float = 10.0,
    wrap_units: bool = False,
    transpose: bool = False,
) -> None:
    """
    Random Forest の Feature Importance 棒グラフを描画する．

    Args:
        importances (Sequence[float]): 重要度（0〜1 の割合），shape (n_features,)
        feature_names (Sequence[str]): 説明変数名
        output_path (str | Path): 保存先 PNG パス
        figsize (tuple[float, float]): 図サイズ
        xlim_max (float): 重要度軸の最大値（%表記，3 目的変数間で揃える）
        font_size (float): 基準フォントサイズ [pt]
        wrap_units (bool): True の場合，説明変数ラベルの単位 [..] の前で改行する
        transpose (bool): True の場合，縦棒グラフとして描画する（説明変数を横軸，
            重要度を縦軸とし，縦に長い図にする用途を想定）
    """
    apply_figure_style(font_size)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    order = np.argsort(importances)[::-1]
    sorted_names = [feature_names[i] for i in order]
    if wrap_units:
        sorted_names = [name.replace(" [", "\n[") for name in sorted_names]
    sorted_values = [importances[i] * 100.0 for i in order]

    fig, ax = plt.subplots(figsize=figsize)
    bar_colors = [COLOR_DARK if i == 0 else COLOR_LIGHT for i in range(len(sorted_names))]
    if transpose:
        ax.bar(
            range(len(sorted_names)),
            sorted_values,
            color=bar_colors,
            edgecolor="black",
            linewidth=0.5,
        )
        ax.set_xticks(range(len(sorted_names)))
        ax.set_xticklabels(sorted_names, rotation=90, ha="center")
        ax.set_ylabel("Feature Importance [%]")
        ax.set_ylim(0.0, xlim_max)
    else:
        ax.barh(
            range(len(sorted_names)),
            sorted_values,
            color=bar_colors,
            edgecolor="black",
            linewidth=0.5,
        )
        ax.set_yticks(range(len(sorted_names)))
        ax.set_yticklabels(sorted_names)
        ax.invert_yaxis()
        ax.set_xlabel("Feature Importance [%]")
        ax.set_xlim(0.0, xlim_max)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_boxplot_feature_target(
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str,
    ylabel: str,
    output_path: str | Path,
    figsize: tuple[float, float] = (5.0, 5.0),
    font_size: float = 10.0,
) -> None:
    """
    特徴量の各水準ごとに目的変数の Box-Plot を描画する．

    Args:
        x (np.ndarray): 特徴量，shape (n_samples,)
        y (np.ndarray): 目的変数，shape (n_samples,)
        xlabel (str): x 軸ラベル（英語，単位付き）
        ylabel (str): y 軸ラベル（英語，単位付き）
        output_path (str | Path): 保存先 PNG パス
        figsize (tuple[float, float]): 図サイズ
        font_size (float): 基準フォントサイズ [pt]
    """
    apply_figure_style(font_size)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    unique_values = sorted(set(x.tolist()))
    grouped = [y[x == value] for value in unique_values]
    tick_labels = [str(value) for value in unique_values]

    fig, ax = plt.subplots(figsize=figsize)
    boxplot = ax.boxplot(
        grouped,
        tick_labels=tick_labels,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 1.0},
        whiskerprops={"color": "black", "linewidth": 0.8},
        capprops={"color": "black", "linewidth": 0.8},
        flierprops={
            "marker": "o",
            "markerfacecolor": COLOR_DARK,
            "markeredgecolor": COLOR_DARK,
            "markersize": 4,
            "linestyle": "none",
        },
    )
    for idx, box in enumerate(boxplot["boxes"]):
        box.set_facecolor(COLOR_CYCLE[idx % 2])
        box.set_edgecolor("black")
        box.set_linewidth(0.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
