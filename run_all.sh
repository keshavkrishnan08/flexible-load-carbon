#!/usr/bin/env bash
# Reproduce the entire A1 deliverable across all four roles.
# Usage: bash run_all.sh   (numpy, scipy, pytest, matplotlib required)
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
pass=0; fail=0
run() { echo "── $1"; if eval "$2"; then echo "  ✓ $1"; pass=$((pass+1)); else echo "  ✗ $1"; fail=$((fail+1)); fi; }

echo "== Role 1: General Carbon Theory & Optimal Contract =="
run "role1 verify_exact (machine-precision audit)" "cd '$ROOT/role1' && python3 -W ignore verify_exact.py | grep -q 'RESULT: 21/21'"
run "role1 verify_double_margin (main model)"       "cd '$ROOT/role1' && python3 -W ignore verify_double_margin.py | grep -q 'RESULT: 9/9'"
run "role1 verify_storage"                          "cd '$ROOT/role1' && python3 -W ignore verify_storage.py | grep -q 'RESULT: 6/6'"

echo "== Role 2: numerical solver test suite =="
run "role2 pytest" "cd '$ROOT/role2' && python3 -m pytest -q -p no:cacheprovider >/tmp/r2.txt 2>&1 && grep -q 'passed' /tmp/r2.txt"

echo "== Role 3: comparative-statics experiments =="
run "role3 experiments" "cd '$ROOT/role3' && python3 run_all_experiments.py >/tmp/r3.txt 2>&1"

echo "== Role 4: theory-hardening test suite =="
run "role4 pytest" "cd '$ROOT/role4' && python3 -m pytest tests/ -q -p no:cacheprovider >/tmp/r4.txt 2>&1 && grep -q 'passed' /tmp/r4.txt"

echo ""
echo "== SUMMARY: $pass passed, $fail failed =="
[ "$fail" -eq 0 ] && echo "ALL A1 DELIVERABLES REPRODUCE." || echo "Some checks failed, see /tmp/r*.txt"
