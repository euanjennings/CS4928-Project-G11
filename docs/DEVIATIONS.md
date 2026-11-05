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


## D2 - RQ2 external sample and retrospective amendment (2026-11-04)

- **What:** Three external cases were planned; only Apktool was examined experimentally, and its algorithm input did not pass full feature-equivalence validation. MapperHelper and NetClient are authors-dataset cases, not extra external cases.
- **Effect:** External transfer remains inconclusive. Section 6 of [PREREGISTRATION.md](PREREGISTRATION.md) records an explicitly retrospective amendment after results were inspected; the original frozen text is preserved.

## D3 - Extractor features and ground-truth ambiguity (2026-11-04)

- **What:** The initial Mapper diagnostic matched 38/50 identities. Targeted corrections reached 50/50, but only 37/50 inner invocations, 21/50 calls and 30/50 visits matched; 563 reference call occurrences remain absent. Empty external-invocation fields are not binding validation.
- **Change:** Preserve v1-v4 and both diagnostics. Stop extractor development at the agreed diagnostic boundary. Use semantic movement of `mFrameworkDirectory` as the primary exploratory label and declaration-only retention as a sensitivity alternative, chosen retrospectively.
- **Effect:** Saved version-specific scores remain exploratory. Fixed-v4-partition sensitivity was recomputed under both labels without rerunning the algorithms. Scores use the upstream transformed MoJoFM scale, not raw percentages. See [validation](../extension/apktool/VALIDATION_REPORT.md) and [sensitivity](../extension/apktool/GROUND_TRUTH_SENSITIVITY.md).

## D4 - Historical comparison versus independent cleanup (2026-11-04)

- **What:** The historical Framework extraction changed TestUtils and SharedLibraryTest. Historical test sources cannot be described as byte-identical. The group did not implement that extraction.
- **Independent change:** The separate cleanup deletes only the obsolete private field and a blank line at the same after revision, retaining the active `mFramework`. Existing forced Gradle evidence gives 176 tests, 0 failures, 0 errors and 1 skip on each side, with zero testcase identity/outcome differences on independent rechecking.
- **Effect:** Supports the small cleanup within tested scenarios, not global equivalence or proof of a major architectural improvement. Further extraction is not justified by current evidence.

## D5 - Matched CK build and measurement scope (2026-11-04)

- **What:** The original wrapper failed in the long Windows path. A short temporary source copy avoided path parsing. Offline cached Maven and a private cache copy resolved download/cache access problems. CK packaged successfully with its own test compilation and Javadoc disabled; these skips are disclosed.
- **Change:** Used read-only Git-archive Java snapshots instead of an additional worktree, preserving Git metadata. The same CK JAR measured 145 tracked Java files (main and tests, no generated build files) at pristine-after and cleanup-after, with options `false 0 false`. Both produced 166 class rows and exited 0.
- **Effect:** AndrolibResources fields 15 to 14, LOC 613 to 612, LCOM* 0.8971428 to 0.8897959; methods 35, CBO 35 and WMC 150 unchanged. The small cohesion change reflects removing unused state. Historical before/after CSVs remain separately identified; their original commands/JAR provenance are incomplete. See [independent experiment](../extension/apktool/INDEPENDENT_CLEANUP_EXPERIMENT.md).
