"""Quality gates: gagalkan run bila data kotor. Return dict laporan."""
import pandas as pd


def check(df: dict) -> dict:
    errors: list[str] = []
    warns: list[str] = []

    for t in ["tasks", "habits", "goals", "transactions", "budgets"]:
        n = len(df[t])
        if n == 0:
            errors.append(f"{t}: kosong")

    # orphan FK
    pids = set(df["projects"]["id"])
    orph = df["tasks"].dropna(subset=["project_id"])
    orph = orph[~orph["project_id"].isin(pids)]
    if len(orph):
        errors.append(f"tasks orphan project_id: {len(orph)}")

    hids = set(df["habits"]["id"])
    orph = df["habit_logs"][~df["habit_logs"]["habit_id"].isin(hids)]
    if len(orph):
        errors.append(f"habit_logs orphan: {len(orph)}")

    # nominal aneh
    bad = df["transactions"][df["transactions"]["amount"] <= 0]
    if len(bad):
        errors.append(f"transactions amount<=0: {len(bad)}")

    # tanggal tak-parse
    for t, col in [("tasks", "due_date"), ("transactions", "date"), ("habit_logs", "date")]:
        s = df[t][col].dropna()
        bad_dates = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce").isna() & (s != "")
        if bad_dates.any():
            errors.append(f"{t}.{col} rusak: {int(bad_dates.sum())}")

    # duplikat PK
    for t in df:
        if df[t]["id"].duplicated().any() if "id" in df[t].columns else False:
            errors.append(f"{t}: duplikat id")

    # warn: status di luar enum
    valid_status = {"inbox", "not_started", "in_progress", "waiting", "completed", "cancelled"}
    weird = set(df["tasks"]["status"]) - valid_status
    if weird:
        warns.append(f"tasks status asing: {weird}")

    report = {"tables": {t: len(df[t]) for t in df}, "errors": errors, "warns": warns}
    if errors:
        raise SystemExit("QUALITY FAIL: " + "; ".join(errors))
    return report
