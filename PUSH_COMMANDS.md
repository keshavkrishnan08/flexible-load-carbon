# Role 3 — Week 3: Final GitHub Push Checklist

Copy-paste these commands in order. Assumes you have `git` installed and SSH/HTTPS access to `dhruvkamath-dev/team-a1`.

---

## 0. Prereqs (one-time)
```bash
# confirm git identity
git config --global user.name  "Dhruv Kamath"
git config --global user.email "you@example.com"
```

## 1. Clone the repo (or reuse existing clone)
```bash
# fresh clone
git clone https://github.com/dhruvkamath-dev/team-a1.git
cd team-a1
```
Already cloned?
```bash
cd team-a1
git fetch origin
```

## 2. Switch to the Role-3 branch
```bash
# if the branch exists on remote
git checkout Role-3
git pull origin Role-3

# if it doesn't exist yet
git checkout -b Role-3
```

## 3. Unzip this bundle next to the repo
```bash
# from the folder where team-a1-role3-week3.zip is downloaded
unzip -o team-a1-role3-week3.zip -d /tmp/role3_week3
ls /tmp/role3_week3/week3     # sanity check
```

## 4. Copy files into the repo (Week 3 only)
```bash
# from inside team-a1/
mkdir -p role3/week3
cp -R /tmp/role3_week3/week3/. role3/week3/

# remove the bundled duplicate of numerical_solver.py
# (canonical copy already lives at role3/numerical_solver.py from Week 1)
rm -f role3/week3/numerical_solver.py

# strip any pycache if present
find role3/week3 -type d -name __pycache__ -exec rm -rf {} +
```

## 5. Verify locally before committing
```bash
# from role3/week3
cd role3/week3
python3 run_week3.py          # should print all 4 bullets and exit 0
cd ../..
git status                    # should list only role3/week3/* changes
```

## 6. Commit
```bash
git add role3/week3/
git commit -m "Role 3 — Week 3: characterization comp-statics, contract wedge, robustness value, fragility map

- Bullet 1: signs of dJ/d{R,c,beta,p,C_F,C_R,C_M} (6/7 distribution-free, 8 dists)
- Bullet 2: wedge W monotone -- 7/8 in C_M, 8/8 in C_R
- Bullet 3: Wasserstein-Beta ambiguity; LR-path sign invariant; price of robustness bounded
- Bullet 4: adoption knife-edge at C_M_bar; endpoint condition g(a) >= g(K_F*) holds 17/17 (no flip on single-mode family)
- LaTeX writeup with proofs (Prop 1-4 + Lemma + Theorem)
- Deterministic (MD5-stable) CSV artifacts + reproducibility report"
```

## 7. Push
```bash
# first push of a new branch
git push -u origin Role-3

# subsequent pushes
git push origin Role-3
```

## 8. (Optional) Open a PR into main
```bash
# via GitHub CLI
gh pr create --base main --head Role-3 \
  --title "Role 3 — Week 3 deliverables" \
  --body  "Adds role3/week3/. See role3/week3/GITHUB_CHECKLIST.md."
```
Or open in browser: https://github.com/dhruvkamath-dev/team-a1/compare/main...Role-3

## 9. Post-push sanity check
Visit: https://github.com/dhruvkamath-dev/team-a1/tree/Role-3/role3/week3
Confirm you see: `README.md`, `REPRODUCIBILITY.md`, `writeup_week3.tex`, `GITHUB_CHECKLIST.md`, `PUSH_COMMANDS.md`, 5 `.py` files, and `results/` with 9 CSVs + memo.
