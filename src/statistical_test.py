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


# ==============================
# IEEE Style Configuration
# ==============================
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "axes.labelsize": 12,
    "font.size": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10
})

# ------------------------------
# 1. Metric computation
# ------------------------------

def calculate_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Relevance and Coverage metrics.
    Relevance = TP / (TP + FP)
    Coverage  = TP / (TP + FN)
    """
    df["Relevance"] = df["TP"] / (df["TP"] + df["FP"])
    df["Coverage"] = df["TP"] / (df["TP"] + df["FN"])
    return df

# ------------------------------
# 2. Assumption validation
# ------------------------------

def validate_assumptions(model, df, response_name):
    print(f"\n--- Assumption validation for {response_name} ---")

    # 4.1 Normality of residuals
    residuals = model.resid

    output_dir = "imgs"
    os.makedirs(output_dir, exist_ok=True)

    # Q–Q plot
    sm.qqplot(residuals, line='s', fit=True)
    plt.title(f"Q–Q plot of residuals ({response_name})")
    plt.savefig(os.path.join(output_dir, f"qqplot_residuals_{response_name}-{metric_sheet}.png"),
                bbox_inches="tight", dpi=300)
    plt.show()
    plt.close()

    # Residual distribution plot
    mu, sigma = residuals.mean(), residuals.std()
    plt.figure(figsize=(6, 4))
    plt.hist(residuals, bins=15, density=True, alpha=0.6)
    x = np.linspace(residuals.min(), residuals.max(), 200)
    y = stats.norm.pdf(x, mu, sigma)
    plt.plot(x, y, linewidth=2)
    plt.xlabel("Residuals")
    plt.ylabel("Density")
    plt.title(f"Residual distribution ({response_name})")
    plt.savefig(os.path.join(output_dir, f"residuals_distribution_{response_name}-{metric_sheet}.png"),
                bbox_inches="tight", dpi=300)
    plt.show()
    plt.close()

    # Shapiro–Wilk test
    shapiro_stat, shapiro_p = shapiro(residuals)
    print(f"Shapiro–Wilk test p-value: {shapiro_p:.4f}")
    if shapiro_p > 0.05: print("→ Residuals are normally distributed")

    # 4.2 Homogeneity of variances (Levene)
    groups = [
        df.loc[(df["id"] == i) & (df["group"] == g), response_name]
        for i in df["id"].unique()
        for g in df["group"].unique()
    ]

    levene_stat, levene_p = stats.levene(*groups)
    print(f"Levene test p-value: {levene_p:.4f}")

    # Interpretation hints
    if levene_p > 0.05:
        print("→ Homogeneity of variances: OK")
    else:
        print("→ Possible heteroscedasticity detected")
    
    return {
        "Metric": response_name,
        "Shapiro-Wilk Statistic": shapiro_stat,
        "Shapiro-Wilk p-value": shapiro_p,
        "Normality": "Yes" if shapiro_p > 0.05 else "No",
        "Levene Statistic": levene_stat,
        "Levene p-value": levene_p,
        "Homogeneity": "Yes" if levene_p > 0.05 else "No"
    }

def plot_violin(df, response_name, metric_sheet, output_dir="imgs", fmt="pgf", extra_formats=("png",)):
    os.makedirs(output_dir, exist_ok=True)

    # IEEE-compatible LaTeX rendering
    tex_rc = {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Times"],
        "axes.labelsize": 10,
        "font.size": 10,
        "legend.fontsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.autolayout": True,
    }

    if fmt == "pgf":
        tex_rc["pgf.texsystem"] = "pdflatex"
        tex_rc["pgf.rcfonts"] = False

    def save_all(fig, basename):
        fig.savefig(os.path.join(output_dir, f"{basename}.{fmt}"), bbox_inches="tight", dpi=300)
        for ext in extra_formats:
            fig.savefig(os.path.join(output_dir, f"{basename}.{ext}"), bbox_inches="tight", dpi=300)

    with plt.rc_context(tex_rc):
        sns.set_theme(style="whitegrid", font="serif", rc=tex_rc)

        col_w = 3.5

        # 1. General violin plot
        fig, ax = plt.subplots(figsize=(col_w, 2.8))
        sns.violinplot(y=df[response_name], inner="quartile", ax=ax)
        ax.set_ylabel(response_name)
        save_all(fig, f"violin_general_{response_name}-{metric_sheet}")
        plt.show()
        plt.close(fig)
        
        median_general = df[response_name].median()
        std_general = df[response_name].std()
        print(f"{response_name} - General: Median={median_general:.4f}, Std={std_general:.4f}")

        # 2. Violin plot by ID
        fig, ax = plt.subplots(figsize=(col_w * 2, 2.8))
        sns.violinplot(x="id", y=response_name, data=df, inner="quartile", ax=ax)
        ax.set_xlabel("ID")
        ax.set_ylabel(response_name)
        ax.tick_params(axis="x", rotation=45)
        save_all(fig, f"violin_by_id_{response_name}-{metric_sheet}")
        plt.show()
        plt.close(fig)
        
        stats_by_id = df.groupby("id")[response_name].agg(["median", "std"])
        print(f"\n{response_name} - By ID:\n{stats_by_id}")

        # 3. Violin plot by Group
        fig, ax = plt.subplots(figsize=(col_w, 2.8))
        sns.violinplot(x="group", y=response_name, data=df, inner="quartile", ax=ax)
        ax.set_xlabel("Group")
        ax.set_ylabel(response_name)
        save_all(fig, f"violin_by_group_{response_name}-{metric_sheet}")
        plt.show()
        plt.close(fig)
        
        stats_by_group = df.groupby("group")[response_name].agg(["median", "std"])
        print(f"\n{response_name} - By Group:\n{stats_by_group}")

    print(f"Violin plots for {response_name} saved to '{output_dir}/' as .{fmt} and {list(extra_formats)}")

# ------------------------------
# 3. Load and preprocess data
# ------------------------------

metric_sheet = "Metrics by ID"
df = pd.read_excel("metrics.xlsx", sheet_name=metric_sheet)

# Aggregate results per id, run, and group
df = (
    df.groupby(["id", "run", "group"], as_index=False)
      .aggregate({
          "TP": "sum",
          "FP": "sum",
          "FN": "sum"
      })
)

# Compute derived metrics
df = calculate_score(df)

# ------------------------------
# 3. ANOVA models
# ------------------------------

model_relevance = ols(
    "Relevance ~ C(id) + C(group) + C(id):C(group)",
    data=df
).fit()

anova_relevance = sm.stats.anova_lm(model_relevance, typ=2)
print("\nANOVA - Relevance")
print(anova_relevance)

model_coverage = ols(
    "Coverage ~ C(id) + C(group) + C(id):C(group)",
    data=df
).fit()

anova_coverage = sm.stats.anova_lm(model_coverage, typ=2)
print("\nANOVA - Coverage")
print(anova_coverage)

# Post-hoc por niveles de "id"
tukey_rel_id = pg.pairwise_tukey(data=df, dv="Relevance", between="id")
print("\nTukey HSD - Relevance por ID")
print(tukey_rel_id)

tukey_cov_id = pg.pairwise_tukey(data=df, dv="Coverage", between="id")
print("\nTukey HSD - Coverage por ID")
print(tukey_cov_id)

# Post-hoc por niveles de "group"
tukey_rel_group = pg.pairwise_tukey(data=df, dv="Relevance", between="group")
print("\nTukey HSD - Relevance por Group")
print(tukey_rel_group)

tukey_cov_group = pg.pairwise_tukey(data=df, dv="Coverage", between="group")
print("\nTukey HSD - Coverage por Group")
print(tukey_cov_group)

# ------------------------------
# 4. Run assumption checks & Save Results
# ------------------------------

relevance_assumptions = validate_assumptions(model_relevance, df, "Relevance")
coverage_assumptions = validate_assumptions(model_coverage, df, "Coverage")

plot_violin(df, "Relevance", metric_sheet)
plot_violin(df, "Coverage", metric_sheet)

assumption_df = pd.DataFrame([relevance_assumptions, coverage_assumptions])

# Save to Excel
with pd.ExcelWriter('metrics.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    assumption_df.to_excel(writer, sheet_name=f"Assumptions-{metric_sheet}", index=False)
    anova_relevance.to_excel(writer, sheet_name=f"ANOVA Relevance-{metric_sheet}")
    anova_coverage.to_excel(writer, sheet_name=f"ANOVA Coverage-{metric_sheet}")
    tukey_rel_id.to_excel(writer, sheet_name=f"Tukey Relevance ID-{metric_sheet}")
    tukey_cov_id.to_excel(writer, sheet_name=f"Tukey Coverage ID-{metric_sheet}")
    tukey_rel_group.to_excel(writer, sheet_name=f"Tukey Relevance Group-{metric_sheet}")
    tukey_cov_group.to_excel(writer, sheet_name=f"Tukey Coverage Group-{metric_sheet}")

print(f"\nResults saved")
