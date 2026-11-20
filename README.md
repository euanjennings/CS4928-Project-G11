# CS4928 Group Project — Decomposing God Classes (ClassSplitter)

Group G11. Paper: Chen et al., *A Position-Aware Approach to Decomposing God Classes*, ASE 2024.
Upstream artefact: https://github.com/ClassSplitter/ClassSplitter, imported verbatim into `upstream/`
at commit `459d796` (tag `UPSTREAM_IMPORT`).

## Questions and results

Questions are shortened here; the frozen wording is in the [preregistration](docs/PREREGISTRATION.md) (§2 and §3).

| Question | Result | Evidence |
| --- | --- | --- |
| **RQ1:** Does ClassSplitter reproduce its reported mean MoJoFM and its advantage over the Bavota baseline on the authors' 133 cases, and what affects the stability of that result? | **Reproduced.** Overall mean 0.4958 vs 0.3353 (notebook 0.496 vs 0.334; preregistered tolerance ±0.005). Wins/ties/losses 82/17/34. ClassSplitter higher for all 30 baseline seeds. | [M2 report](results/M2_SUMMARY.md), [Run A](results/m2_repro_seed2026.json), [Run B seeds](results/m2_seeds/) |
| **RQ2, transfer:** Does the advantage transfer to Extract Class refactorings from Java projects outside the authors' dataset? | **Inconclusive.** One external case (Apktool) was studied instead of the planned three, and its feature extractor failed equivalence validation, so the Apktool algorithm scores are exploratory only. | [Case study §1–3](design/APKTOOL_CASE_STUDY.md), [preregistration amendment](docs/PREREGISTRATION.md), D2–D3 in [deviations](docs/DEVIATIONS.md) |
| **RQ2, design decision (M4):** What does this imply for a concrete Extract Class decision in that system? | Removed the unused `mFrameworkDirectory` field left in `AndrolibResources` after the developers' Framework extraction. 176 tests with identical outcomes before and after; LCOM* 0.8971 → 0.8898, fields 15 → 14 and LOC 613 → 612; methods (35), CBO (35) and WMC (150) unchanged. The maintainers made the same deletion themselves, so this is convergent, not novel. | [Case study §4](design/APKTOOL_CASE_STUDY.md), [cleanup patch](extension/apktool/publication/cleanup.patch), D4–D6 |
| **Event A:** Does the M2 advantage hold on two held-out cases from the authors' dataset? | **No.** ClassSplitter 0.3839 vs Bavota 0.4386, against a prediction of a smaller positive gap. The workbook history shows the prediction recorded on 30 Oct, before the saved results; those are a 2 Nov recovery replay, and the timing of the original October run is unverified (D10). | [Event A summary](EVENT_A.md), [prediction](extension/event_a/PREDICTION.md), [report](results/event_a/REPORT.md) |
| **Event B:** Is adding a framework-cache statistics feature easier after the Framework extraction? | **Partly supports keeping Framework.** One production file changed in both versions; the feature sits in `Framework` instead of growing `AndrolibResources`. Prediction and results were committed together (D8); the workbook history shows the prediction recorded on 12 Nov, before the recorded test runs on 13 Nov (D10). A retrospective follow-up with matched patches and the full test suite found the same size of change in both designs (+1 method, +19 LOC, +6 WMC), no change in test outcomes, and no effect from our own M4 cleanup. | [Event B](extension/apktool/event_b/README.md), [follow-up (§8)](extension/apktool/event_b/README.md), D9 |

Every change we have made to upstream code is shown by:

```
git diff UPSTREAM_IMPORT -- upstream/
```

## Repository layout

| Path | What lives there |
| --- | --- |
| `upstream/` | Verbatim upstream copy. Edit only when needed, and log each edit in `docs/DEVIATIONS.md`. |
| `repro/` | RQ1 reproduction runner (`run_repro.py`). |
| `results/` | RQ1 (M2) and Event A raw outputs and reports. Commit these; they are the evidence. |
| `extension/event_a/` | Event A prediction, cases and scripts, including `verify_results.py`. |
| `extension/apktool/` | RQ2 Apktool case: ground truth, scripts, compact results, `verify_evidence.py` and the raw 4–5 Nov evidence in `apktool_raw_archive.zip`. |
| `extension/apktool/event_b/` | Event B patches, tests and JUnit results; `followup/` holds the retrospective follow-up harness and its run. |
| `design/` | The M4 design decision ([Apktool case study](design/APKTOOL_CASE_STUDY.md)). |
| `docs/` | [Preregistration](docs/PREREGISTRATION.md), [deviations log](docs/DEVIATIONS.md), [AI-use log](docs/AI_USE.md) and [workbook history excerpt](docs/evidence/tracker_change_history_G11.md). |

## Milestone tags

| Tag | Commit | Note |
| --- | --- | --- |
| `UPSTREAM_IMPORT` | `d06364b` | Verbatim upstream import. |
| `M1_PLAN` | `b4ca046` | Preregistration freeze. The tag was added after the freeze commit; see the [M2 report](results/M2_SUMMARY.md) §6. |
| `M2_REPRO`, `PRE_EVENT_A` | `c71b2cb` | Added retrospectively on 2026-11-20 for navigation only; see D8. |
| `PRE_EVENT_B` | `b8124f8` | Lightweight tag on the M4 state; see D8. |
| `FINAL` | | Added at submission. |

## Setup (each team member, once)

1. **Install**
   - Git.
   - Python 3.12.
   - A JDK, e.g. Eclipse Temurin. Check that `java -version` works in a *new* terminal, because upstream shells out to `java`. We planned JDK 21 but ran M2 with Java 23.0.2, Event A and Event B with Java 17, and one 5 Nov Apktool test run with JDK 21 (see D7 and D9). The Event B follow-up harness needs Java 17.
2. **Clone and create the environment**

   ```bash
   git clone <our-repo-url> && cd <repo>
   python -m venv .venv
   # macOS/Linux: source .venv/bin/activate
   # Windows:     .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Smoke test** (3 classes, under a minute):

   ```bash
   python repro/run_repro.py --ids 1 2 3 --out results/smoke_<yourname>.csv
   ```

   Delete your smoke output afterwards rather than committing it.

## Rules we agreed

- Work on a branch, open a PR, and have one teammate review it before merging to `main`.
- Never move or delete a milestone tag once pushed: `M1_PLAN`, `M2_REPRO`, `PRE_EVENT_A`, `PRE_EVENT_B`, `FINAL`.
- Create milestone tags as annotated tags and push them:

  ```bash
  git tag -a M1_PLAN -m "..."
  git push origin M1_PLAN
  ```

- Don't run two experiments at once from the same checkout. Upstream writes `group.rsf` and `example.rsf` into its own folder on every call.
- Any results we cite must come from a committed script run on a committed state. Check `git_dirty` in the JSON record.
- Log material AI contributions in `docs/AI_USE.md`, one line each.
