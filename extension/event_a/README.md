# Event A experiment

This experiment applies the M2 ClassSplitter and Bavota methods to MapperHelper (Mapper, case 13) and NetClient (Mindustry, case 3490). The case order is 13 followed by 3490, with Python random seed 2026. The model identifier, cached similarities, algorithm defaults and scoring are those used by `repro/run_repro.py`.

The [report](../../results/event_a/REPORT.md) contains the interpretation and design implication. The [prediction](PREDICTION.md) specifies the expected outcome and the decision criteria.

## Environment

The recorded environment uses Python 3.12.14, Java 17.0.20 and the versions in [requirements.txt](requirements.txt). The complete installed dependency list is in [environment_freeze.txt](../../results/event_a/environment_freeze.txt). Java must be available on PATH. The two selected cases use the supplied cache, so execution requires neither an API key nor a model download.

Commands below run from the repository root. On Windows, using Git Bash:

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install torch==2.10.0+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r extension/event_a/requirements.txt
python -m pip check
export PYTHONUTF8=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
```

On Linux, environment creation and activation use `python3.12 -m venv .venv` and `source .venv/bin/activate`; the remaining commands are the same.

## Primary experiment

```bash
python extension/event_a/verify_results.py
python extension/event_a/run_event_a.py --seed 2026 --out-dir results/event_a_check
python extension/event_a/verify_results.py --run results/event_a_check
```

The output directory must not already exist. Execution is serial because the upstream scorer uses shared temporary `group.rsf` and `example.rsf` files.

| Case | ClassSplitter overall | Bavota overall |
|---|---:|---:|
| MapperHelper | 0.2084 | 0.2500 |
| NetClient | 0.5594 | 0.6272 |
| Mean | 0.3839 | 0.4386 |

The reporting transform is `max(0, (raw_percent - 50) / 50)`, matching M2. The verifier compares all twelve reported scores, twelve raw percentages and four final partitions with the saved primary evidence. Python's random module is seeded as in M2; NumPy and Gensim defaults are unchanged.

`cases.csv` uses the position-study IDs. These IDs belong to a different catalogue from the original M2 runner's `--ids` argument.

## Validation suite

```bash
python -u extension/event_a/run_validation.py --out-dir results/event_a_validation
python extension/event_a/inspect_pairs.py --run-dir results/event_a_validation/primary --out results/event_a_validation/position_pairs.csv
cat results/event_a_validation/validation.json
```

The suite executes the primary and repeat seed-2026 runs, seeds 0–29, two diagnostics, all 133 M2 cases and the original M2 runner on the held-out catalogue. The output directory must be a new path inside the repository because the original M2 runner reports repository-relative paths.

The recorded checks are:

- Twelve primary scores match the reference values.
- The repeated run matches the primary scores and final partitions.
- Bavota has the higher mean across all thirty additional seeds.
- All 798 original M2 scores match exactly.
- The original M2 runner matches all twelve held-out scores.

## Diagnostic configurations

```bash
python extension/event_a/run_event_a.py --seed 2026 --diagnostic no-method-position --out-dir results/event_a_no_position
python extension/event_a/run_event_a.py --seed 2026 --diagnostic recompute-ms --out-dir results/event_a_recomputed_ms
```

The first diagnostic uses the authors' `PS=0, MS=1, CS=1` switch. It disables method position weighting and positional steps while retaining field-position fallback. The second recalculates only ClassSplitter's structural MS matrix in memory. These configurations have separate outputs and do not modify the cache or replace the primary result.

## Evidence layout

| Path under results/event_a | Contents |
|---|---|
| primary/ | Main seed-2026 run, member data, stages, final partitions and RSF inputs |
| repeat_seed2026/ | Repeat of the primary configuration |
| seeds/ | Individual runs for seeds 0–29 |
| diagnostic_no_method_position/ | Method-position diagnostic |
| diagnostic_recomputed_ms/ | Structural-similarity diagnostic and pairwise differences |
| m2_replay.csv and m2_replay.json | Original M2 runner's 133-case validation |
| original_runner_event_a.csv and .json | Independent two-case check through the M2 runner |
| source/ | Before-and-after source files and exact source URLs |
| primary_metrics.csv | Scores in table form |
| position_pairs.csv | Positional examples traced through the saved stages |
| validation.json | Numerical validation summary |
| evidence_sha256.json | Integrity checks for the delivered files |

Execution-specific input snapshots and timestamps remain in the raw result records.
