"""Static preview charts for the README (the interactive version lives on Tableau Public)."""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

TEAL, ROSE, GREY, INK = "#1f6f8b", "#b04a5a", "#9aa7af", "#17262f"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#66757f", "axes.labelcolor": "#4b5d68", "xtick.color": "#4b5d68",
                     "ytick.color": "#4b5d68", "axes.grid": True, "axes.axisbelow": True, "grid.color": "#e6ecef"})
FIG = Path("figures"); FIG.mkdir(exist_ok=True)
con = sqlite3.connect("data/restaurant_inspections.db")

# 1. Cuisine: worst 6 and best 6 by average initial score
cz = pd.read_csv("outputs/03_by_cuisine.csv")
sel = pd.concat([cz.head(6), cz.tail(6)]).sort_values("avg_initial_score")
fig, ax = plt.subplots(figsize=(9, 5))
worst = set(cz.head(6)["cuisine"])
colors = [ROSE if c in worst else TEAL for c in sel["cuisine"]]
ax.barh(sel["cuisine"], sel["avg_initial_score"], color=colors, height=0.65)
for y, v in enumerate(sel["avg_initial_score"]):
    ax.text(v + 0.3, y, f"{v:.1f}", va="center", fontsize=10, color=INK)
ax.axvline(13, color=INK, lw=1, ls="--"); ax.text(13.2, len(sel) - 0.45, "A-grade cutoff (13 points)", fontsize=9, color=INK)
ax.set_xlabel("Average initial inspection score (lower is cleaner)"); ax.grid(axis="y", visible=False)
fig.suptitle("Six worst (red) and six best (teal) cuisines by initial inspection score", x=0.01, ha="left", fontsize=13)
fig.tight_layout(); fig.savefig(FIG / "cuisine_scores.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# 2. Seasonality: average initial score by calendar month, 2024-01 to 2026-09
i = pd.read_sql("SELECT inspection_date, score FROM inspections WHERE is_initial_cycle = 1 "
                "AND inspection_date >= '2024-01-01' AND inspection_date < '2026-10-01'", con, parse_dates=["inspection_date"])
by_m = i.groupby(i["inspection_date"].dt.month)["score"].mean()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(by_m.index, by_m.values, color=TEAL, lw=2.5, marker="o", ms=6)
ax.set_xticks(range(1, 13)); ax.set_xticklabels(list("JFMAMJJASOND"))
ax.set_ylabel("Avg initial score"); ax.set_ylim(14, 21)
ax.annotate(f"July {by_m.loc[7]:.1f}", (7, by_m.loc[7]), xytext=(7.3, by_m.loc[7] + 0.4), fontsize=10, color=INK)
ax.annotate(f"Dec {by_m.loc[12]:.1f}", (12, by_m.loc[12]), xytext=(10.9, by_m.loc[12] - 0.9), fontsize=10, color=INK)
fig.suptitle("Inspection scores worsen every summer (initial inspections, 2024-2026)", x=0.01, ha="left", fontsize=13)
fig.tight_layout(); fig.savefig(FIG / "seasonality.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# 3. Top violations
tv = pd.read_csv("outputs/04_top_violations.csv").head(8).iloc[::-1]
short = {"10F": "Non-food surfaces not clean / sealed", "08A": "Conditions conducive to pests",
         "06C": "Food not protected from contamination", "10B": "Plumbing / drainage problems",
         "02G": "Cold food held above 41 °F", "06D": "Food-contact surfaces not sanitized",
         "02B": "Hot food held below 140 °F", "04L": "Evidence of mice"}
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.barh([f"{c}  {short.get(c, c)}" for c in tv["violation_code"]], tv["pct_of_inspections"],
        color=[ROSE if c == "Critical" else GREY for c in tv["critical"]], height=0.65)
for y, v in enumerate(tv["pct_of_inspections"]):
    ax.text(v + 0.5, y, f"{v:.0f}%", va="center", fontsize=10, color=INK)
ax.set_xlabel("Share of inspections citing the violation"); ax.grid(axis="y", visible=False)
fig.suptitle("Most common violations (red = critical)", x=0.01, ha="left", fontsize=13)
fig.tight_layout(); fig.savefig(FIG / "top_violations.png", dpi=160, bbox_inches="tight"); plt.close(fig)
print("saved", sorted(p.name for p in FIG.iterdir()))
