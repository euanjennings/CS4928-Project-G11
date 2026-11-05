# Apktool study: evidence and reproduction

Read the [case study](../../design/APKTOOL_CASE_STUDY.md) for the design decision, the [ground-truth report](GROUND_TRUTH_SENSITIVITY.md) for the as-run labels and retrospective sensitivity calculation, and the [validation report](VALIDATION_REPORT.md) for the failed feature-equivalence check. The frozen plan and retrospective scope amendment are in [preregistration](../../docs/PREREGISTRATION.md); [deviations](../../docs/DEVIATIONS.md) record departures from it.

The original algorithm runs used **declaration-only** ground truth: ten methods and zero fields marked moved. The semantic treatment of `mFrameworkDirectory` was a later sensitivity analysis. Only one of three planned external cases was studied. Member identities matched 50/50 after correction, but calls matched 21/50 and field visits 30/50. Exploratory scores therefore cannot establish external transfer.

## Published evidence

| File | Role |
| --- | --- |
| [apktool_ground_truth.csv](apktool_ground_truth.csv) | Single authoritative as-run ground-truth file, byte-for-byte identical to the original submitted input. |
| [v2](publication/inputs/apktool_classsplitter_candidate_v2.csv), [v3](publication/inputs/apktool_classsplitter_candidate_v3.csv), [v4](publication/inputs/apktool_classsplitter_candidate_v4.csv) | One authoritative candidate file per genuinely different extractor version. |
| [v2 cache](results/apktool_similarity_cache.json), [v3 cache](results_v3/apktool_similarity_cache.json), [v4 cache](results_v4/apktool_similarity_cache.json) | Version-matched embedding caches used by the runner. |
| [run_apktool.py](run_apktool.py), [rerun_exploratory.py](publication/rerun_exploratory.py) | Algorithm runner and isolated rerun wrapper; the wrapper writes to a new temporary directory and uses the root ground-truth CSV. |
| [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json) | Saved scores and v4 partitions, input/cache/result hashes, retrospective rerun outcomes, validation/test counts and CK metrics. |
| [verify_evidence.py](verify_evidence.py) | Read-only checks of published inputs, caches and results; optional deeper comparison with preserved raw evidence. |
| [cleanup.patch](publication/cleanup.patch), [run_ck_pair.py](publication/run_ck_pair.py) | Exact one-field cleanup and matched CK reproduction from external source. |
| [mapper_validation_members_v2.py](publication/scripts_original/mapper_validation_members_v2.py) | Targeted MapperHelper diagnostic against the author reference already in this repository. |

The v2-to-v3 candidate changes 22 `inner invocations` cells; v3-to-v4 changes 60 cells across calls and invocation columns. They are different scientific inputs, not copies distinguished only by line endings. Earlier duplicate ground-truth and v2 candidate copies are preserved outside this repository; their bytes matched the authoritative files. The semantic-field truth is a separate retrospective alternative and is not substituted into the algorithm inputs.

## External source and reproduction

| Source | Repository | Exact revision |
| --- | --- | --- |
| Apktool before Framework extraction | `https://github.com/iBotPeaches/Apktool.git` | `9c495cae295dbff3aab378da4a889d8b926f081a` |
| Apktool after Framework extraction and cleanup baseline | same | `40d427e5bdf5c204c58022cef3b369f34e19b043` |
| Identical maintainer field deletion | same | `ab6f1b416e0a3f21dea6853bd26bfe672cae12f7` (#3116) |
| Later AaptInvoker/ResourcesDecoder extraction | same | `a7e2e3e5e10ad223764cdac8c23cb9ee189c569f` (#3124) |
| CK tool | `https://github.com/mauricioaniche/ck.git` | `8a1ef916d597d33ad619d748b616bb7dbc3f0c36` |

The historical extraction is the diff between the first two Apktool revisions. The [cleanup patch](publication/cleanup.patch) applies to the after revision and removes only its unused `AndrolibResources.mFrameworkDirectory` declaration and a blank line. Apktool maintainers had already made the identical deletion in a larger change, so the group's independently implemented and tested cleanup is convergent rather than novel.

From a fresh Group 11 clone with the scientific packages in `requirements.txt` and Java available, run:

```powershell
python extension/apktool/verify_evidence.py
python extension/apktool/publication/rerun_exploratory.py --version 2
python extension/apktool/publication/rerun_exploratory.py --version 3
python extension/apktool/publication/rerun_exploratory.py --version 4
```

The wrapper selects the corresponding candidate and cache, uses seed 2026 and `sentence-transformers/all-mpnet-base-v2`, and writes new results under a unique temporary directory. It does not overwrite saved evidence or the Git index. These are **retrospective reproductions**, not the original runs. Under the recorded later environment, v2 and v3 output files reproduced byte-for-byte; v4 scores reproduced but `mFramework` (member 5) changed ClassSplitter group, so its full JSON hash did not match. The cause is unresolved. The original comparison files did not record their producing Git commit or dirty status; a contemporaneous 4 November snapshot was dirty. [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json) distinguishes these facts. A newly committed clean state is needed before claiming fully committed provenance for the revised wrapper and authoritative input bytes.

The historical-before forced test run at `9c495cae` succeeded with 176 tests, 175 passes, one skip and no failures or errors. The historical-after baseline had the same testcase identities and outcomes, although test sources changed. The pristine-after versus independent-cleanup comparison also had 176 tests on each side with identical outcomes. Full Gradle logs and XML are preserved outside the repository; concise verified counts are in the [results summary](RESULTS_SUMMARY.json).

To repeat matched CK measurement, build CK at the exact commit with Java 17 and Maven 3.6.1; the successful local build used `mvn -Dmaven.test.skip=true -Dmaven.javadoc.skip=true package`. Then provide a dependency-inclusive JAR and an Apktool clone containing the historical-after revision:

```powershell
python extension/apktool/publication/run_ck_pair.py --repo "<APKTOOL_REPOSITORY>" --jar "<CK_JAR>" --out "<NEW_OUTPUT_DIRECTORY>"
```

This script uses read-only Git archives, 145 tracked Java files, one JAR and options `false 0 false`. It makes fresh private outputs and does not alter a checkout. The matched original runs emitted 166 class rows per side. The small LCOM* decrease after field removal partly follows from the field-based metric calculation; method interactions did not measurably improve.

Full method-level CK tables, testcase XML, diagnostic comparisons and original result JSONs are retained in the separate local archive for extended audit. The published scripts, versioned inputs/caches, ground truth, saved score/partition summary and external source references support the essential calculations from a fresh clone. Exact v4 output reproduction remains a limitation, and no published data repairs the extractor's failed feature-equivalence validation.
