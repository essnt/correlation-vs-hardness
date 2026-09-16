#!/usr/bin/env bash
# Unified progress caliber: completed = rows in the DB whose status is not an
# error / planned job count.
# S0 total 832 = frozen grid 720 + grid-floor extension 112 (s0_ext_low)
# Note: E3a+E3b submitted 2100 jobs, of which 120 E3b original-arm jobs merge
# idempotently into E3a by identical key, hence 1980 rows when complete
# (1980/1980 = fully complete; the 120 delta is not missing work).
# Usage: bash scripts/status.sh
cd "$(dirname "$0")/.."
for pair in "m2_s0.db 832 S0" "m2_e1e2.db 840 E1+E2" "m2_main.db 1980 E3a+E3b"; do
  set -- $pair
  db="results/$1"; total=$2; name=$3
  [ -f "$db" ] || { echo "$name: not started (0/$total)"; continue; }
  read -r done err wt <<< "$(sqlite3 "$db" "SELECT SUM(CASE WHEN status NOT LIKE 'error%' AND status NOT LIKE 'childerror%' THEN 1 ELSE 0 END) || ' ' || SUM(CASE WHEN status LIKE 'error%' OR status LIKE 'childerror%' THEN 1 ELSE 0 END) || ' ' || SUM(CASE WHEN status='walltimeout' THEN 1 ELSE 0 END) FROM runs")"
  mt=$(ls --time-style=+%H:%M:%S -la "$db" | awk '{print $6}')
  echo "$name: completed ${done:-0}/$total (error rows pending recompute: ${err:-0}, walltime cutoffs: ${wt:-0}) | mtime $mt"
done
echo "---"
if [ -f results/e6.json ]; then
  echo "E6: done ($(wc -l < results/e6.json) JSON lines; H3 cut per preregistered kill line, see REPORT_zh section 10)"
else
  echo "E6: not started"
fi
for extra in m2_e4.db m2_s0_spotcheck.db; do
  [ -f "results/$extra" ] && echo "$extra: $(sqlite3 results/$extra 'SELECT COUNT(*) FROM runs') rows"
done
date +%H:%M:%S
