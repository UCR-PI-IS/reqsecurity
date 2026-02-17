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

def calculate_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Relevance and Coverage metrics.
    Relevance = TP / (TP + FP)
    Coverage  = TP / (TP + FN)
    """
    df["relevance"] = df["TP"] / (df["TP"] + df["FP"])
    df["coverage"] = df["TP"] / (df["TP"] + df["FN"])
    return df


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


def violin_chart(df: pd.DataFrame, metric: str, group_col: str, dirname, filename):
    """
    Violin plot comparing distributions of a metric across groups.
    """
    _apply_ieee_style()

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.violinplot(data=df, x=group_col, y=metric, ax=ax, inner="box", cut=0)
    ax.set_xlabel(group_col.capitalize())
    ax.set_ylabel(metric.capitalize())
    fig.tight_layout()

    _save_and_show(fig, dirname, filename)


def violin_chart_grouped(df: pd.DataFrame, metric: str, group_col: str, hue_col: str, dirname, filename):
    """
    Violin plot comparing distributions of a metric across groups, split by hue.
    """
    _apply_ieee_style()

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(data=df, x=group_col, y=metric, hue=hue_col, ax=ax,
                   inner="box", cut=0, split=False)
    ax.set_xlabel(group_col.capitalize())
    ax.set_ylabel(metric.capitalize())
    ax.legend(title=hue_col.capitalize(), loc="best")
    fig.tight_layout()

    _save_and_show(fig, dirname, filename)


# ------------------------------
# 1. Load and preprocess data
# ------------------------------

metric_sheet = "Metrics by ID"
df = pd.read_excel("metrics.xlsx", sheet_name=metric_sheet)
experiments = open("resources/riaz_results.json", "r").read()
experiments = json.loads(experiments)
experiments_df = pd.DataFrame(experiments)

# Aggregate results per id, run, and group
df = (
    df.groupby(["id", "use_case", "group"], as_index=False)
      .aggregate({
          "TP": "sum",
          "FP": "sum",
          "FN": "sum"
      })
)

# # General confusion matrix (all data summed)
# confusion_matrix_chart(
#     df,
#     "imgs",
#     "confusion_matrix_general"
# )

# # Grouped confusion matrix by "group"
# confusion_matrix_chart_grouped(
#     df,
#     group_by="group",
#     dirname="imgs",
#     filename="confusion_matrix_by_group"
# )

# # Grouped confusion matrix by "id"
# confusion_matrix_chart_grouped(
#     df,
#     group_by="id",
#     dirname="imgs",
#     filename="confusion_matrix_by_id"
# )

df = calculate_score(df)
df['n'] = 15

df = pd.concat([df, experiments_df], ignore_index=True)

df.drop(columns=["TP", "FP", "FN", "efficiency", "quality"], inplace=True)
df["domain"] = df["use_case"].apply(lambda x: "Healthcare" if "health" in x.lower() else "Mobile" if "mobile" in x.lower() else "Other")

table_by_group = df.groupby(["id", "group"], as_index=False).agg({
    "relevance": "mean",
    "coverage": "mean"
})
table_by_use_case = df.groupby(["id", "domain"], as_index=False).agg({
    "relevance": "mean",
    "coverage": "mean"
})
overall_table = df.groupby(["id"], as_index=False).agg({
    "relevance": "mean",
    "coverage": "mean"
})

# Convert DataFrames to LaTeX tables
print("\n=== TABLE BY GROUP ===")
print(table_by_group.to_latex(index=False, float_format="%.3f"))

print("\n=== TABLE BY USE CASE ===")
print(table_by_use_case.to_latex(index=False, float_format="%.3f"))

print("\n=== OVERALL TABLE ===")
print(overall_table.to_latex(index=False, float_format="%.3f"))

# Optionally, save to files
os.makedirs("tables", exist_ok=True)
with open("tables/table_by_group.tex", "w") as f:
    f.write(table_by_group.to_latex(index=False, float_format="%.3f"))
with open("tables/table_by_use_case.tex", "w") as f:
    f.write(table_by_use_case.to_latex(index=False, float_format="%.3f"))
with open("tables/overall_table.tex", "w") as f:
    f.write(overall_table.to_latex(index=False, float_format="%.3f"))

# # How do the distributions of coverage metrics of security requirements generated by
# # large language models compare to those elicited by human participants?
# df["source"] = df["id"].apply(lambda x: "LLM" if x in ["UCR26a", "UCR26b", "UCR26c", "UCR26d"] else "Human")

# violin_chart(df, "coverage", "source", "imgs", "violin_coverage")

# # How do the distributions of relevance scores of security requirements generated by
# # large language models compare to those elicited by human participants?
# violin_chart(df, "relevance", "source", "imgs", "violin_relevance")

# # Coverage: control vs treatment, split by source (Human / LLM)
# violin_chart_grouped(df, "coverage", "group", "source", "imgs", "violin_coverage_by_group")

# # Relevance: control vs treatment, split by source (Human / LLM)
# violin_chart_grouped(df, "relevance", "group", "source", "imgs", "violin_relevance_by_group")

