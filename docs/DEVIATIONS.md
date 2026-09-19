# Deviations from the upstream artefact / paper

Each entry: ID · what changed · why · evidence · effect on results.

## D1 — Baseline1 crashes on the published code (fixed)
- **What:** `baseline1.py` `compute_group_coupling()` reads `group.members`, but `Group` in the published `cluster.py` only has `.units`. The baseline raises `AttributeError` part-way through the 133 classes.
- **Change:** `group1.members[i]` → `group1.units[i]` (same for `group2`). Two-token edit, see `git diff UPSTREAM_IMPORT -- upstream/`.
- **Why:** Without it the Bavota baseline cannot be run at all. `cluster.py` appears to have been refactored after the notebook outputs were generated.
- **Effect:** Method-level MoJoFM in the setup check matched the saved notebook exactly (baseline 0.325, ClassSplitter 0.526, 82/17/34 wins/ties/losses). ClassSplitter overall MoJoFM also matched (0.496). The baseline's overall and field MoJoFM differed slightly (see randomness note below). To be confirmed in our M2 run.

## Audit notes (not code changes)
- **Unseeded randomness in the baseline:** `Baseline1.handel_fields()` puts never-visited fields into `random.randint(...)` groups with no seed. Baseline overall and field MoJoFM therefore vary between runs, and the authors' exact draw can't be recovered. Setup check: baseline overall 0.3345 (notebook 0.334), W/T/L 82/17/34 (notebook 83/17/33); field 0.437 (notebook 0.441). `run_repro.py --seed` makes our runs repeatable. Consider reporting the spread over several seeds.
- Upstream `show_result.draw_compare` uses an independent-samples t-test (`ttest_ind`) on paired per-class data; `repro/run_repro.py` reports it alongside paired t-test and Wilcoxon signed-rank.
- Embedding similarities come from the shipped cache (`cache_time_all-mpnet-base-v2.json`); the sentence-transformer model is not loaded for the 133 classes.
