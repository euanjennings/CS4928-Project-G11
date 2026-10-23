# M2 — Bounded reproduction — Group G11

**RQ1 status: REPRODUCED**

In M1, we planned to run ClassSplitter and the Bavota baseline on the authors' 133 cases and compare the results with their saved notebook output. We have completed those runs. Both overall means fall within our agreed tolerance, and ClassSplitter scores higher than the baseline.

This report follows the [M1 preregistration](../docs/PREREGISTRATION.md) at commit `b4ca046`, tagged `M1_PLAN`. The results below come from the saved reproduction runs, which we checked on 22 October 2026.

## 1. RQ1 and reproduction target

**RQ1:** *Using the authors' published artefact and their dataset of 133 real-world God classes, does ClassSplitter reproduce its reported decomposition accuracy (mean MoJoFM) and its reported advantage over the Bavota baseline, and which properties of the artefact affect the stability of that result?*

As agreed in M1, we use the saved outputs in cells 0 and 2 of [experienment_result.ipynb](../upstream/Implementation/experienments/experienment_result.ipynb) as our target. The reported overall means are **0.496 for ClassSplitter** and **0.334 for Bavota**. We expected both means to agree within ±0.005, with ClassSplitter scoring higher.

The baseline is the authors' implementation of Bavota's approach, `Baseline1`. We use the same score calculation as the notebook: the code transforms the raw MoJoFM percentage using `max(0, (MoJoFM - 50) / 50)`. Higher scores mean that the proposed split is closer to the developers' actual split.

## 2. Cases and method

We used all 133 cases, with runner IDs 1–133, as planned. Every run produced scores for all 133 cases, and none were excluded. The cases come from 50 projects.

We carried out the two sets of runs specified in M1:

Run A determines the reproduction verdict. Run B checks stability; its average does not replace the Run A result.

| | Run A — reproduction | Run B — seed stability |
| --- | --- | --- |
| Purpose | Decide whether the result is reproduced | Check whether changing the seed affects the result |
| Cases | All 133 | All 133 in each run |
| Seed | 2026 | 0–29 |
| Recorded commit | `b4ca046`, clean working tree | `15d7eb2`, uncommitted changes recorded; see §6 |
| Saved outputs | [CSV](m2_repro_seed2026.csv) and [JSON](m2_repro_seed2026.json) | [30 CSV/JSON pairs](m2_seeds/) |

Both used Python 3.12.3, Java 23.0.2 and the shipped similarity cache on Windows 11. The package versions are recorded in each JSON file and match across the runs. The baseline crash fix described in M1 and [DEVIATIONS.md](../docs/DEVIATIONS.md) was already applied.

For Run A, we used:

```sh
python repro/run_repro.py --out results/m2_repro_seed2026.csv --seed 2026
```

For Run B, we repeated this command with `--seed N --out results/m2_seeds/seed_N.csv`, for seeds 0–29. The runs were carried out one at a time because the upstream code writes to shared scoring files.

## 3. Results

Overall mean MoJoFM is our primary measure. The table shows the results rounded to four decimal places; we checked the decision rule using the unrounded means.

| Tool | Notebook mean | Run A mean | Range allowed by M1 | Within range? |
| --- | --- | --- | --- | --- |
| ClassSplitter | 0.496 | 0.4958 | 0.491–0.501 | Yes |
| Bavota | 0.334 | 0.3353 | 0.329–0.339 | Yes |

We also recorded the secondary measurements listed in M1:

| Measurement | Notebook | Run A |
| --- | --- | --- |
| Method-level mean, Bavota / ClassSplitter | 0.325 / 0.526 | 0.3254 / 0.5263 |
| Field-level mean, Bavota / ClassSplitter | 0.441 / 0.449 | 0.4373 / 0.4489 |
| Overall wins / ties / losses for ClassSplitter | 83 / 17 / 33 | 82 / 17 / 34 |
| Overall independent t-test p | 8.75e-08 | 1.18e-07 |
| Method-level independent t-test p | 7.79e-11 | 7.79e-11 |
| Overall paired t-test / Wilcoxon p | — | 2.11e-09 / 4.09e-09 |
| Field-level independent / paired / Wilcoxon p | 0.854 / — / — | 0.789 / 0.721 / 0.425 |

The overall and method-level comparisons favour ClassSplitter under these tests. The field-level comparisons do not reach p < 0.05. As agreed in M1, these tests are reported alongside the results but do not determine the reproduction verdict.

For wins, ties and losses, M1 treats an absolute score difference of at most `1e-6` as a tie. Applying this rule gives the same counts as the saved results.

## 4. Stability properties

### Baseline randomness

The baseline assigns fields that no method visits to a random group. We changed the seed to check how much this affects the scores.

| Measurement across seeds 0–29 | Result |
| --- | --- |
| Lowest baseline overall mean | 0.3325 |
| Highest baseline overall mean | 0.3374 |
| Average baseline overall mean | 0.3350 |
| Sample standard deviation of the baseline means | 0.0013 |
| Seeds with the baseline inside the M1 range | 30/30 |
| Seeds with ClassSplitter higher overall | 30/30 |

ClassSplitter's overall, method-level and field-level scores were identical for every case across Run A and all 30 Run B seeds. The baseline's method-level scores also stayed the same; its field-level and overall scores varied.

The notebook's overall win/tie/loss count of 83/17/33 appeared in four seeds. This is consistent with the authors having used a different random draw, although their original seed is unknown.

### Choice of statistical test

For every seed, the independent t-test, paired t-test and Wilcoxon test gave p < 0.05 for the overall and method-level comparisons. All field-level comparisons stayed above 0.05. Changing the seed or test did not change these conclusions.

### Baseline fix and embedding cache

We checked the D1 fix against the upstream code. It replaces `members` with `units` in two places. The unpatched baseline crashes, so we cannot compare complete results before and after the fix.

We did not carry out the optional embedding recomputation described in M1. Our results therefore apply to runs using the authors' shipped cache.

## 5. Decision and answer to RQ1

TBA

## 6. Evidence, deviations and limitations

TBA
