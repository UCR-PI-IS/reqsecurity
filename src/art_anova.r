# Install once if needed
install.packages("ARTool")
install.packages("readxl")
install.packages("dplyr")
install.packages("openxlsx")

library(ARTool)
library(readxl)
library(dplyr)
library(openxlsx)

metric_sheet <- "Metrics by ID"
df <- read_excel("metrics.xlsx", sheet = metric_sheet)

df <- df %>%
    group_by(id, run, group) %>%
    summarise(
        TP = sum(TP),
        FP = sum(FP),
        FN = sum(FN),
        .groups = "drop"
    )

df <- df %>%
    mutate(
        Relevance = TP / (TP + FP),
        Coverage = TP / (TP + FN)
    )

df$group <- factor(df$group)
df$id    <- factor(df$id)

# =====================
# ART ANOVA - Relevance
# =====================
model_rel <- art(Relevance ~ group * id, data = df)
anova_rel <- anova(model_rel)
print("ART ANOVA - Relevance")
print(anova_rel)

# =====================
# ART ANOVA - Coverage
# =====================
model_cov <- art(Coverage ~ group * id, data = df)
anova_cov <- anova(model_cov)
print("ART ANOVA - Coverage")
print(anova_cov)

# =====================
# Save results to Excel
# =====================
wb <- loadWorkbook("metrics.xlsx")

sheet_rel_name <- substr(paste("ART ANOVA Relevance -", metric_sheet), 1, 31)
# Excel sheet names are limited to 31 chars
sheet_cov_name <- substr(paste("ART ANOVA Coverage -", metric_sheet), 1, 31)

if (sheet_rel_name %in% names(wb)) {
  removeWorksheet(wb, sheet_rel_name)
}
addWorksheet(wb, sheet_rel_name)
writeData(wb, sheet_rel_name, anova_rel, rowNames = TRUE)

if (sheet_cov_name %in% names(wb)) {
  removeWorksheet(wb, sheet_cov_name)
}
addWorksheet(wb, sheet_cov_name)
writeData(wb, sheet_cov_name, anova_cov, rowNames = TRUE)

saveWorkbook(wb, "metrics.xlsx", overwrite = TRUE)
print("Results saved to metrics.xlsx")
