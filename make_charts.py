import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV outputs
sov_df = pd.read_csv("reports/exports/sov.csv")
spv_df = pd.read_csv("reports/exports/spv.csv")

# Chart 1: SoV bar chart
plt.figure(figsize=(6,4))
plt.bar(sov_df["brand"], sov_df["sov"]*100)
plt.ylabel("Share of Voice (%)")
plt.title("Top Brands by Share of Voice")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("reports/sov_chart.png")
plt.close()

# Chart 2: SPV bar chart
plt.figure(figsize=(6,4))
plt.bar(spv_df["brand"], spv_df["spv"]*100, color="green")
plt.ylabel("Share of Positive Voice (%)")
plt.title("Share of Positive Voice by Brand")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("reports/spv_chart.png")
plt.close()

print("Charts saved in reports/ as sov_chart.png and spv_chart.png")
