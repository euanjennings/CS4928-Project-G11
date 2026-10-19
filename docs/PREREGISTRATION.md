# M1 preregistration (RQ1 freeze) — Group G11

- Paper: Chen et al., *A Position-Aware Approach to Decomposing God Classes*, ASE 2024.
- Public artefact: https://github.com/ClassSplitter/ClassSplitter, imported verbatim at `459d796d3256de428330bff693f14cf442097338` (tag `UPSTREAM_IMPORT`).
- Group members: Seán Conneally, Euan Jennings, Cian Gleeson, Yanislav Iliev
- Date agreed by the group: 2026-10-19
- Coordinator status: READY
- Project-pack bounded target: checked against the CS4928 *Project Brief and Rubric* on 2026-10-19: RQ1 is the bounded reproduction of one part of the study (ClassSplitter vs the Bavota baseline, mean MoJoFM, on the authors' 133-case evaluation dataset), using the pack's assigned paper and repository. The ClassSplitter project-pack sheet itself was not available to us when this check was made; [FILL IN: confirm against the pack sheet / Group Allocation entry in Student Tracker.xlsx, or delete this sentence].
- Scope: this freeze covers **RQ1 only**. RQ2 (transfer and design decision) will be preregistered separately before any RQ2 work starts.
- Timing note: this plan is frozen later than Week 5. At the time of freezing, no formal (full-dataset) run has been made; only the 3-case feasibility check in §3 exists. See §1 for everything seen beforehand.

## 1. Prior knowledge (disclosed before freezing)

- **Saved artefact results.** We have read the saved outputs in `upstream/Implementation/experienments/experienment_result.ipynb` (§2), because they are the reproduction target.
- **Setup check (repo notes, Sept 2026).** [DEVIATIONS.md](DEVIATIONS.md) reports a setup run that matched the notebook for method-level MoJoFM and ClassSplitter overall, with small baseline differences due to unseeded randomness. Who ran it: Euan Jennings, around 2026-09-19 (the date of the D1 commit). No raw output from that run is committed, so we treat it as an unverified claim.
- **Feasibility check (§3).** Cases 1–3 only.

We will not change the sample, metrics or decision rules to favour any of these observations.

## 2. RQ1 — bounded reproduction

**RQ1:** *Using the authors' published artefact and their dataset of 133 real-world God classes, does ClassSplitter reproduce its reported decomposition accuracy (mean MoJoFM) and its reported advantage over the Bavota baseline, and which properties of the artefact affect the stability of that result?*

Tracker entries (Week 5, as recorded by the group):

- **Sample:** We will study all 133 God-class refactoring cases supplied by the authors, using runner case IDs 1–133.
- **Method:** Run both tools on 133 published cases, compare mean MoJoFM with the reported values and check seed stability.
- **Expected result:** We expect both overall means to agree with the saved published values within ±0.005, with ClassSplitter scoring higher than Bavota.

### Reproduction target (the saved published values)

The artefact README states that "the main experiment results can be checked in experienments/experienment_result.ipynb". We use that notebook's saved outputs as the reported values (cells 0 and 2, printed to 3 decimal places):

| Measure (mean over 133 cases) | Bavota (`Baseline1`) | ClassSplitter | W/T/L (ClassSplitter vs Bavota) | Upstream `ttest_ind` p |
| --- | --- | --- | --- | --- |
| **Overall MoJoFM (primary)** | **0.334** | **0.496** | 83 / 17 / 33 | 8.75e-08 |
| Method-level MoJoFM | 0.325 | 0.526 | 82 / 17 / 34 | 7.79e-11 |
| Field-level MoJoFM | 0.441 | 0.449 | 40 / 56 / 37 | 0.854 |

- Scale: MoJoFM on 0–1, higher = closer to the developers' actual split.
- Paper cross-reference (not used for the decision rule): [FILL IN: paper table/page, if the group wants to note whether the paper's printed values match the notebook].
- The Bavota baseline is upstream `baseline1.py` (`Baseline1`), as used in the notebook.

### Cases

- Sample: **all 133 cases**, runner IDs 1–133 (the `index` column of `upstream/Implementation/experienments/GodClassRefactorDictionary.csv`).
- The 133 cases come from 50 projects (`upstream/dataset/GodClassRefactorDictionary.csv`). Cases from the same project are not independent; we report this as a threat.
- ID mapping: runner ID ≠ dataset `index`/`last index` ≠ filename prefix. The output CSV records the runner ID and data filename for every case.
- Exclusions: none planned. A case that errors is logged with its error message and reported, not silently dropped.

### Method

Environment: Python 3.12.3 (`.venv312`, `requirements.txt`), Java 23.0.2 (README asks for JDK 21; logged as a deviation), shipped embedding cache `cache_time_all-mpnet-base-v2.json`, D1 fix applied. Runs are sequential (upstream writes `group.rsf`/`example.rsf` into its own folder).

**Run A — reproduction (answers "does it reproduce"):**

```
python repro/run_repro.py --out results/m2_repro_seed2026.csv --seed 2026
```

**Run B — seed stability (answers "which properties affect stability"):** the same command with seeds 0–29 (`--seed N --out results/m2_seeds/seed_N.csv`). Only the baseline uses randomness, so ClassSplitter's scores should be identical across seeds; we will check this rather than assume it.

Measurements (per case, written to CSV):

- **Primary:** overall MoJoFM, mean over the 133 cases, for each tool.
- **Secondary:** method-level and field-level MoJoFM; wins/ties/losses (tie = absolute difference ≤ 1e-6).
- **Statistical tests (reported, not part of the decision rule):** upstream `ttest_ind` (to compare with the notebook), plus paired t-test and Wilcoxon signed-rank, because the scores are paired by case.

### Stability properties to examine (bounded list)

1. **Baseline randomness:** `Baseline1.handel_fields()` assigns never-visited fields to `random.randint` groups with no seed. Measured by Run B.
2. **Choice of statistical test:** upstream `ttest_ind` treats the two tools' scores as independent samples; paired t-test and Wilcoxon do not.
3. **The D1 fix:** the baseline cannot run without it. We check that it is a two-token attribute rename that changes no logic.
4. **Cached vs recomputed embeddings (optional):** recompute ClassSplitter's embeddings with `sentence-transformers/all-mpnet-base-v2` for cases 1–10 and compare scores. Done only if time allows after Runs A and B; otherwise reported as a limitation.

**Instability criterion:** a property affects stability if varying it (a) moves either overall mean outside ±0.005 of the saved value, (b) flips which tool has the higher overall mean, or (c) moves a significance test across p = 0.05. For Run B we report the min/max/mean of the baseline's overall MoJoFM across the 30 seeds and the share of seeds that fall within ±0.005 of 0.334.

### Decision rules (agreed before the formal runs)

Applied to Run A:

- **REPRODUCED:** both overall means are within ±0.005 of the saved values (ClassSplitter 0.491–0.501; Bavota 0.329–0.339) **and** ClassSplitter's overall mean is higher than Bavota's.
- **PARTIALLY REPRODUCED:** ClassSplitter is higher than Bavota, but at least one overall mean falls outside ±0.005.
- **NOT REPRODUCED:** ClassSplitter's overall mean is not higher than Bavota's.
- **INCONCLUSIVE / BLOCKED:** fewer than 127 of the 133 cases (95%) complete validly, or the environment fails.

±0.005 is a group-chosen tolerance. Rounding to 3 decimals alone accounts for at most ±0.0005; the remaining margin allows for the baseline’s unseeded randomness, whose size Run B measures. It is strict enough that a materially different result (e.g. a 1-point MoJoFM drop) would fail. Because the baseline has unseeded randomness, a fail on the Bavota value at seed 2026 alone is reported with Run B's seed range, not reinterpreted. We do not swap in a 30-seed average to judge reproduction.

### Expected result

As recorded by the group: both overall means agree with the saved values within ±0.005, with ClassSplitter scoring higher than Bavota (i.e. REPRODUCED). We also expect the baseline's overall mean to vary across seeds by less than 0.01, and ClassSplitter's to be identical across seeds.

## 3. Completed feasibility check

Sean ran this command before M1 on 2026-10-07:

```powershell
.\.venv312\Scripts\python.exe repro/run_repro.py --ids 1 2 3 --out results/smoke_sean.csv
```

- Runner cases: 1, 2 and 3, all from initial published material.
- Seed: 2026 (runner default).
- Result: both techniques completed all three cases and wrote CSV/JSON outputs.
- Overall means observed: Bavota 0.4665; ClassSplitter 0.6790; ClassSplitter won 3/3 cases.
- Environment: Python 3.12.3; Java 23.0.2; package versions recorded in the JSON.
- Code commit recorded: `7fad2afe991d8fe721b5d50e4e91ce70afbe7da8`; working tree was dirty. This was a feasibility run, not a frozen formal reproduction.
- Evidence: `results/smoke_sean.csv` and `results/smoke_sean.json`.

These outcomes are prior observations and will be disclosed. They demonstrate feasibility for three cases, not full-study reproduction.

## 4. Evidence to be produced

- `results/m2_repro_seed2026.csv` + `.json` (Run A), `results/m2_seeds/` (Run B), and a summary script/table comparing them with the saved notebook values.
- Deviations logged in [DEVIATIONS.md](DEVIATIONS.md): D1, unseeded baseline randomness, Java 23 vs 21, `ttest_ind` on paired data.
- Material AI contributions logged in [AI_USE.md](AI_USE.md).

## 5. Freeze and amendments

After the coordinator confirms READY, tag the reviewed commit `M1_PLAN`. After freezing, the text above is not edited; changes go in the table below with the date, the reason and whether results had already been seen.

| Date | Amendment | Reason | Results already inspected? | Evidence |
| --- | --- | --- | --- | --- |
| | | | | |