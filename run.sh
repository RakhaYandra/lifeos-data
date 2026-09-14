#!/usr/bin/env bash
# Full pipeline: bootstrap snapshot seed -> quality -> marts -> charts.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f work/seed.db ]; then
  echo "== bootstrap snapshot (seed fiktif) =="
  mkdir -p work
  rm -f work/seed.db
  goose -dir ../lifeos/migrations sqlite work/seed.db up >/dev/null
  sqlite3 work/seed.db < ../lifeos/seed/seed.sql
fi

python3 run.py
