# ==============================
# Factorial ANOVA with Assumption Validation
# ==============================

import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy.stats import shapiro
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pingouin as pg
import os
import json

def _apply_ieee_style():
    """Apply IEEE-compliant matplotlib style."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "text.usetex": False,
        "figure.dpi": 300,
    })


def _save_and_show(fig, dirname, filename):
    """Save figure as PNG and PGF, then display it."""
    os.makedirs(dirname, exist_ok=True)
    base, _ = os.path.splitext(filename)
    fig.savefig(os.path.join(dirname, f"{base}.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(dirname, f"{base}.pgf"), bbox_inches="tight")
    plt.show()
    plt.close(fig)


def confusion_matrix_chart(df: pd.DataFrame, dirname, filename):
    _apply_ieee_style()

    tp = int(df["TP"].sum())
    fp = int(df["FP"].sum())
    fn = int(df["FN"].sum())
    tn = int(df["TN"].sum()) if "TN" in df.columns else 0

    cm = pd.DataFrame(
        [[tp, fn], [fp, tn]],
        index=["True", "False"],
        columns=["Positive", "Negative"]
    )

    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                linewidths=0.5, linecolor="gray", ax=ax)
    fig.tight_layout()

    _save_and_show(fig, dirname, filename)


def confusion_matrix_chart_grouped(df: pd.DataFrame, group_by: str, dirname, filename):
    """
    Single heatmap: rows = groups, columns = VP, FP, FN, VN.
    """
    _apply_ieee_style()

    grouped = df.groupby(group_by).agg({"TP": "sum", "FP": "sum", "FN": "sum"})
    if "TN" in df.columns:
        grouped["TN"] = df.groupby(group_by)["TN"].sum()
    else:
        grouped["TN"] = 0

    cm = grouped.rename(columns={
        "TP": "True Positive",
        "FP": "False Positive",
        "FN": "False Negative",
        "TN": "True Negative"
    })
    cm = cm[["True Positive", "False Positive", "False Negative", "True Negative"]]
    cm.index.name = None

    n_groups = len(cm)
    fig_height = max(3.5, 0.7 * n_groups + 1.5)
    fig, ax = plt.subplots(figsize=(7, fig_height))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                linewidths=0.5, linecolor="gray", ax=ax)
    fig.tight_layout()

    _save_and_show(fig, dirname, filename)


def violin_chart(df: pd.DataFrame, metric: str, group_col: str, dirname, filename, print_stats: bool = True):
    """
    Violin plot comparing distributions of a metric across groups.
    """
    _apply_ieee_style()

    # Calcular y mostrar estadísticas descriptivas
    if print_stats:
        print(f"\n=== Estadísticas para {metric} por {group_col} ===")
        stats_df = df.groupby(group_col)[metric].agg(['mean', 'std', 'count'])
        stats_df.columns = ['Mean', 'Std Dev', 'N']
        print(stats_df.to_string())
        print()

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.violinplot(data=df, x=group_col, y=metric, ax=ax, inner="box", cut=0)
    ax.set_ylim(0, 1)
    ax.set_xlabel(group_col.capitalize())
    ax.set_ylabel(metric.capitalize())
    fig.tight_layout()

    _save_and_show(fig, dirname, filename)


def violin_chart_grouped(df: pd.DataFrame, metric: str, group_col: str, hue_col: str, dirname, filename, print_stats: bool = True):
    """
    Violin plot comparing distributions of a metric across groups, split by hue.
    """
    _apply_ieee_style()

    # Calcular y mostrar estadísticas descriptivas
    if print_stats:
        print(f"\n=== Estadísticas para {metric} por {group_col} y {hue_col} ===")
        stats_df = df.groupby([group_col, hue_col])[metric].agg(['mean', 'std', 'count'])
        stats_df.columns = ['Mean', 'Std Dev', 'N']
        print(stats_df.to_string())
        print()

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(data=df, x=group_col, y=metric, hue=hue_col, ax=ax,
                   inner="box", cut=0, split=False)
    ax.set_ylim(0, 1)
    ax.set_xlabel(group_col.capitalize())
    ax.set_ylabel(metric.capitalize())
    ax.legend(title=hue_col.capitalize(), loc="best")
    fig.tight_layout()

    _save_and_show(fig, dirname, filename)


# ------------------------------
# 1. Load and preprocess data
# ------------------------------

metric_sheet = "Similarity Metric"
df = pd.read_excel("metrics.xlsx", sheet_name=metric_sheet)
experiments = open("resources/riaz_results.json", "r").read()
experiments = json.loads(experiments)
experiments_df = pd.DataFrame(experiments)

df = df[df["exception"].isna()]
df.rename(columns={
    "use_case": "Use Case",
    "sentence": "Sentence",
    "group": "Experimental Group", 
    "id": "Temperature",
    "objective": "Objective",
    "pattern": "Pattern",
    "cosine_similarity": "SBERT"}, 
    inplace=True)

violin_chart(
    df, 
    "SBERT", 
    "Experimental Group", 
    "imgs", 
    "violin_chart_accuracy_by_experimental_group.png")

violin_chart(
    df, 
    "SBERT", 
    "Temperature", 
    "imgs", 
    "violin_chart_accuracy_by_temperature.png"
)

violin_chart_grouped(
    df, 
    "SBERT", 
    "Experimental Group", 
    "Temperature", 
    "imgs", 
    "violin_chart_accuracy_by_experimental_group_and_temperature.png"
)

aggregated_df = df.groupby(
    [
        "Temperature",
        "Experimental Group",
        "Use Case",
        "Sentence",
        "Objective",
        "Pattern",
    ],
    as_index=False
).agg(
    Accuracy=("SBERT", "mean"),
    Min=("SBERT", "min"),
    Max=("SBERT", "max"),
    Precision=("SBERT", "std"),
    Count=("SBERT", "count"),
)

aggregated_df["Precision"] = abs(1 - aggregated_df["Precision"])

aggregated_df.to_csv("aggregated_metrics.csv", index=False)
violin_chart(
    aggregated_df, 
    "Accuracy", 
    "Experimental Group", 
    "imgs", 
    "aggregated_violin_chart_accuracy_by_experimental_group.png")

violin_chart(
    aggregated_df, 
    "Accuracy", 
    "Temperature", 
    "imgs", 
    "aggregated_violin_chart_accuracy_by_temperature.png"
)

violin_chart_grouped(
    aggregated_df, 
    "Accuracy", 
    "Experimental Group", 
    "Temperature", 
    "imgs", 
    "aggregated_violin_chart_accuracy_by_experimental_group_and_temperature.png"
)

violin_chart(
    aggregated_df, 
    "Precision", 
    "Experimental Group", 
    "imgs", 
    "aggregated_violin_chart_precision_by_experimental_group.png")

violin_chart(
    aggregated_df, 
    "Precision", 
    "Temperature", 
    "imgs", 
    "aggregated_violin_chart_precision_by_temperature.png"
)

violin_chart_grouped(
    aggregated_df, 
    "Precision", 
    "Experimental Group", 
    "Temperature", 
    "imgs", 
    "aggregated_violin_chart_precision_by_experimental_group_and_temperature.png"
)
