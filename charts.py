"""Charts Nexus-style (navy, Inter bila ada, angka mono) -> charts/*.png."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
CH = ROOT / "charts"

NAVY, SURF, BLUE, LBLUE, INK, MUT = "#0B1120", "#0F172A", "#3B82F6", "#60A5FA", "#F1F5F9", "#94A3B8"


def _fig():
    plt.rcParams.update({"figure.facecolor": NAVY, "axes.facecolor": SURF,
                         "text.color": INK, "axes.labelcolor": MUT,
                         "xtick.color": MUT, "ytick.color": MUT,
                         "font.family": "sans-serif"})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for s in ax.spines.values():
        s.set_color("#1E293B")
    return fig, ax


def _save(fig, name):
    CH.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(CH / name, dpi=110)
    plt.close(fig)


def spending_by_category(m):
    d = m.groupby("category")["expense"].sum().sort_values(ascending=False).head(8)
    fig, ax = _fig()
    ax.barh(d.index[::-1], d.values[::-1], color=BLUE)
    ax.set_title("SPENDING BY CATEGORY (IDR)", fontsize=10, loc="left", color=MUT, family="monospace")
    for i, v in enumerate(d.values[::-1]):
        ax.text(v, i, f" {v:,.0f}", va="center", fontsize=8, color=INK, family="monospace")
    _save(fig, "spending_by_category.png")


def cashflow_trend(m):
    fig, ax = _fig()
    ax.plot(m["ym"], m["income"], marker="o", color=BLUE, label="income")
    ax.plot(m["ym"], m["expense"], marker="o", color="#F87171", label="expense")
    ax.set_title("NET CASHFLOW TREND", fontsize=10, loc="left", color=MUT, family="monospace")
    ax.legend(frameon=False, labelcolor=MUT)
    _save(fig, "cashflow_trend.png")


def habit_rates(m, names):
    m = m.copy()
    m["name"] = m["habit_id"].map(names)
    m = m.sort_values("rate")
    fig, ax = _fig()
    ax.barh(m["name"], m["rate"], color=LBLUE)
    ax.set_xlim(0, 1)
    ax.set_title("HABIT RATE · 30 DAYS", fontsize=10, loc="left", color=MUT, family="monospace")
    for i, v in enumerate(m["rate"]):
        ax.text(v, i, f" {v:.0%}", va="center", fontsize=8, color=INK, family="monospace")
    _save(fig, "habit_rates.png")


def task_throughput(m):
    fig, ax = _fig()
    x = range(len(m))
    ax.bar(x, m["done"], color=BLUE, label="done")
    ax.bar(x, m["overdue"], bottom=m["done"], color="#F87171", label="overdue")
    ax.set_xticks(list(x), m["week"], rotation=30, fontsize=7, family="monospace")
    ax.set_title("TASK THROUGHPUT PER WEEK", fontsize=10, loc="left", color=MUT, family="monospace")
    ax.legend(frameon=False, labelcolor=MUT)
    _save(fig, "task_throughput.png")


def all_charts(marts, habit_names):
    spending_by_category(marts["spending_daily"])
    cashflow_trend(marts["cashflow_monthly"])
    habit_rates(marts["habit_rates"], habit_names)
    task_throughput(marts["task_throughput"])
    print("charts: 4 png")
