"""Orkestrasi: extract -> quality -> marts -> charts + quality_report.json."""
import json

import charts as C
import etl
import marts as M
import quality as Q


def main():
    df = etl.extract()
    report = Q.check(df)
    marts = M.build(df)
    M.save(marts)
    names = dict(zip(df["habits"]["id"], df["habits"]["name"]))
    C.all_charts(marts, names)
    open("work/quality_report.json", "w").write(json.dumps(report, indent=1))
    sep = df["transactions"]
    sep9 = sep[(sep["date"] >= "2026-09-01") & (sep["date"] < "2026-10-01")]
    net = (sep9[sep9.type == "income"]["amount"].sum()
           - sep9[sep9.type == "expense"]["amount"].sum())
    print(f"insight: Sep-2026 net = {net:,.0f} "
          f"({len(sep9)} trx), tasks={len(df['tasks'])}, "
          f"habit logs={len(df['habit_logs'])}")
    print("OK: quality_report.json + 5 marts + 4 charts")


if __name__ == "__main__":
    main()
