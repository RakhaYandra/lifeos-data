"""Marts: tabel analitik siap lapor (DuckDB + parquet di work/)."""
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"


def build(df: dict) -> dict:
    con = duckdb.connect()
    for t, frame in df.items():
        con.register(t, frame)

    marts = {}
    marts["spending_daily"] = con.execute("""
        SELECT date, category, SUM(amount) AS expense
        FROM transactions WHERE type='expense'
        GROUP BY date, category ORDER BY date
    """).df()
    marts["cashflow_monthly"] = con.execute("""
        SELECT substr(date,1,7) AS ym,
          SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS income,
          SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense
        FROM transactions GROUP BY ym ORDER BY ym
    """).df()
    marts["budget_health"] = con.execute("""
        SELECT b.year, b.month, b.category, b.amount AS budget,
          COALESCE(SUM(CASE WHEN t.type='expense' THEN t.amount ELSE 0 END),0) AS actual
        FROM budgets b LEFT JOIN transactions t
          ON t.category=b.category AND t.type='expense'
          AND substr(t.date,1,4)=CAST(b.year AS VARCHAR)
          AND substr(t.date,6,2)=LPAD(CAST(b.month AS VARCHAR),2,'0')
        GROUP BY b.year, b.month, b.category, b.amount
    """).df()
    logs = df["habit_logs"].copy()
    logs["date"] = pd.to_datetime(logs["date"])
    cutoff = logs["date"].max() - pd.Timedelta(days=29)
    last30 = logs[logs["date"] >= cutoff]
    marts["habit_rates"] = (last30.groupby("habit_id")["done"]
                            .agg(checks="sum", days="count").reset_index())
    marts["habit_rates"]["rate"] = marts["habit_rates"]["checks"] / marts["habit_rates"]["days"]
    tasks = df["tasks"].copy()
    tasks["week"] = pd.to_datetime(tasks["due_date"], errors="coerce").dt.strftime("%Y-W%V")
    marts["task_throughput"] = (tasks.dropna(subset=["week"]).groupby("week")
                                .agg(total=("id", "count"),
                                     done=("status", lambda s: int((s == "completed").sum())),
                                     overdue=("status", lambda s: 0)).reset_index())
    # overdue dihitung vs max due (snapshot Sep 2026)
    today = tasks["due_date"].max()
    marts["task_throughput"]["overdue"] = tasks.dropna(subset=["week"]).groupby("week").apply(
        lambda g: int(((g["due_date"] < today) & (~g["status"].isin(["completed", "cancelled"]))).sum()),
        include_groups=False).values
    con.close()
    return marts


def save(marts: dict) -> None:
    WORK.mkdir(exist_ok=True)
    con = duckdb.connect()
    for name, frame in marts.items():
        con.register("m", frame)
        con.execute(f"COPY m TO '{WORK / (name + '.parquet')}' (FORMAT PARQUET)")
    con.close()
