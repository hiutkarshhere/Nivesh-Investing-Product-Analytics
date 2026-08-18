"""
Product adoption analysis: what do users invest in first, and do they
expand into other product types over time? This is the classic "expansion"
side of product analytics that funnel/retention work doesn't capture --
a user can be perfectly retained (still investing every month) while never
actually deepening their relationship with the platform beyond one product.
For a company monetizing on AUM and transaction volume, cross-product
adoption is usually worth more than pure retention.
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
VIZ = ROOT / "visuals"

sns.set_theme(style="whitegrid", context="talk")

investments = pd.read_csv(RAW / "investments.csv", parse_dates=["investment_date"])
users = pd.read_csv(RAW / "users.csv")

user_products = investments.groupby("user_id")["product_type"].apply(lambda s: sorted(s.unique()))
n_products = user_products.apply(len)
first_product = investments.sort_values("investment_date").groupby("user_id")["product_type"].first()

adoption = pd.DataFrame({
    "first_product": first_product,
    "n_distinct_products": n_products,
}).join(users.set_index("user_id")[["risk_profile", "acquisition_channel", "city_tier"]])
adoption["expanded"] = adoption.n_distinct_products >= 2

overall_expansion_rate = adoption.expanded.mean() * 100
print(f"Overall product expansion rate (>=2 distinct products): {overall_expansion_rate:.1f}%")
print(f"Total activated investors analyzed: {len(adoption):,}")

# expansion rate by first product -- which entry point leads to the deepest
# platform relationship?
by_first_product = adoption.groupby("first_product").agg(
    users=("expanded", "count"),
    expansion_rate_pct=("expanded", lambda s: round(s.mean() * 100, 1)),
).sort_values("expansion_rate_pct", ascending=False)
by_first_product.to_csv(PROC / "expansion_by_first_product.csv")
print("\n=== EXPANSION RATE BY FIRST PRODUCT ===")
print(by_first_product.to_string())

# expansion rate by risk profile -- tests the hypothesis carried over from
# the correction study: do aggressive investors diversify faster too?
by_risk = adoption.groupby("risk_profile").agg(
    users=("expanded", "count"),
    expansion_rate_pct=("expanded", lambda s: round(s.mean() * 100, 1)),
).sort_values("expansion_rate_pct", ascending=False)
by_risk.to_csv(PROC / "expansion_by_risk_profile.csv")
print("\n=== EXPANSION RATE BY RISK PROFILE ===")
print(by_risk.to_string())

# most common second product, given the first -- a simple "what's next"
# recommendation-relevant table
expanded_users = adoption[adoption.expanded].index
second_products = (
    investments[investments.user_id.isin(expanded_users)]
    .sort_values("investment_date")
    .groupby("user_id")["product_type"]
    .apply(lambda s: s.unique()[1] if len(s.unique()) > 1 else None)
)
transition_table = pd.DataFrame({
    "first_product": adoption.loc[second_products.index, "first_product"],
    "second_product": second_products,
})
transition_counts = transition_table.groupby(["first_product", "second_product"]).size().reset_index(name="users")
transition_counts = transition_counts.sort_values(["first_product", "users"], ascending=[True, False])
transition_counts.to_csv(PROC / "product_transition_pairs.csv", index=False)
print("\n=== TOP TRANSITION FOR EACH FIRST PRODUCT ===")
print(transition_counts.groupby("first_product").head(1).to_string(index=False))

# ---------------------------------------------------------------------------
# charts
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6))
order = by_first_product.sort_values("expansion_rate_pct")
ax.barh(order.index, order.expansion_rate_pct, color=sns.light_palette("#1d4ed8", n_colors=len(order)+1)[1:])
for i, (v, n) in enumerate(zip(order.expansion_rate_pct, order.users)):
    ax.text(v + 0.5, i, f"{v}%  (n={n})", va="center", fontsize=10.5)
ax.set_xlabel("Expansion Rate (%, adopted a 2nd product type)")
ax.set_title("Which Entry Product Leads to the Deepest Platform Relationship?")
plt.tight_layout()
plt.savefig(VIZ / "07_expansion_by_first_product.png", dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(8, 5.5))
colors = {"Conservative": "#b34d4d", "Moderate": "#d99a4e", "Aggressive": "#3f7d5c"}
ax.bar(by_risk.index, by_risk.expansion_rate_pct, color=[colors[r] for r in by_risk.index])
for i, v in enumerate(by_risk.expansion_rate_pct):
    ax.text(i, v + 0.5, f"{v}%", ha="center", fontsize=12)
ax.set_ylabel("Expansion Rate (%)")
ax.set_xlabel("Risk Profile")
ax.set_title("Product Expansion Rate by Risk Profile")
plt.tight_layout()
plt.savefig(VIZ / "08_expansion_by_risk.png", dpi=150)
plt.close()

print("\nsaved: visuals/07_expansion_by_first_product.png, 08_expansion_by_risk.png")
print("saved: data/processed/expansion_by_first_product.csv, expansion_by_risk_profile.csv, product_transition_pairs.csv")
