# Apktool research evidence and reproduction

Publication package prepared on 5 November 2026 from the completed 4 November experiment. Read the [case study](../../../design/APKTOOL_CASE_STUDY.md), [validation report](../VALIDATION_REPORT.md), [label sensitivity](../GROUND_TRUTH_SENSITIVITY.md) and [cleanup experiment](../INDEPENDENT_CLEANUP_EXPERIMENT.md).

**External transfer remains inconclusive.** Only Apktool was examined externally, and structural features failed equivalence validation. The independent dead-field cleanup has matched tests and CK measurements. Algorithm outputs are exploratory only.

## Evidence retained for review

- `inputs/`: v1-v4 candidate lineage, original truth and separately named semantic-field truth.
- `scripts_original/`: unchanged extractors, ground-truth generator and diagnostics. These retain their historical sibling-layout assumptions and obsolete upload messages. Use the wrappers below; do not follow those messages.
- `evidence/`: both original Mapper diagnostics, historical CK CSVs, both successful Gradle logs, and all 42 XML reports per side.
- `ck_pristine_20261104/` and `ck_cleanup_20261104/`: matched class/method metrics and CK runtime logs.
- `verified/`: test counts and every testcase outcome, validation counts, mismatch examples, exact moved-method mapping, fixed-partition sensitivity, versioned algorithm provenance and source hashes.
- `source/`, `cleanup.patch` and `historical_refactoring.patch`: code and distinct historical versus independent changes.
- [CK manifest](ck_run_manifest.json): tool hash/version, Java version, timestamp, matching options and exit codes. Commands use explicit portable placeholders.
- [Publication provenance](PUBLICATION_PROVENANCE.json): original and published SHA-256 hashes and exact transformations. The original private handover package is retained locally, not submitted. The separate submission manifest inventories the final published set.

CK CSV derivatives change only the `file` column to a repository-relative Java path. XML derivatives remove hostnames, environment properties and console streams; suite/test attributes, durations, identities, failures/errors/skips and outcome nodes remain. Complete original XML and raw CK files remain locally preserved. Gradle logs are decoded from UTF-16 to UTF-8, with local javac source-path prefixes replaced by `<APKTOOL>` and line endings normalized. Excluded CK build troubleshooting logs are not needed to verify the scientific results. No metric or test outcome has been edited.

Version-specific algorithm results and caches remain at [v2](../results/comparison.json), [v3](../results_v3/comparison.json) and [v4](../results_v4/comparison.json). Their input and cache hashes are verified by the script below. Do not mix candidate versions or describe the upstream transformed score as raw MoJoFM.

## Verify evidence without rerunning algorithms

From the repository root, with Python 3 and Java on PATH, choose an output directory that does not exist:

```powershell
python extension/apktool/publication/verify_evidence.py --out "$env:TEMP/cs4928-evidence-new"
```

The script parses both published XML ZIPs, compares testcase identities/outcomes with multiplicity, recounts validation agreements, verifies candidate/result hashes, and rescores fixed v4 partitions under both field conventions. It writes only new output. This command was executed successfully against the publication derivatives; the saved scientific summaries reproduce exactly.

## Rerun Mapper diagnostics

Use Python with `javalang==0.13.0` installed:

```powershell
python extension/apktool/publication/rerun_validation.py --version initial
python extension/apktool/publication/rerun_validation.py --version members
```

The wrappers create unique temporary layouts from existing tracked source/reference files and archived scripts. Earlier execution reproduced both original diagnostics byte-for-byte. The publication copies have not altered their code or inputs. Matching identities do not validate calls or visits.

## Optional exploratory algorithm rerun

With the scientific dependencies in the repository's `requirements.txt` and Java available:

```powershell
python extension/apktool/publication/rerun_exploratory.py --version 4
```

Versions 2 and 3 are also supported. The wrapper selects the explicit candidate and matching cache, copies evaluator modules to a temporary directory and invokes the existing runner with seed 2026 and `sentence-transformers/all-mpnet-base-v2`. It avoids overwriting preserved outputs. Historical package provenance is incomplete; record the environment of any future run. The wrapper has not been used to rerun invalid inputs as a new scientific result.

The older `../run_apktool.py` is retained for lineage and imported by the wrapper. Do not directly run it over preserved `results/`: it writes that directory and upstream scratch RSFs. The proposed submission excludes the push-triggered workflow.

## Reproduce matched CK measurements

Obtain CK source commit `8a1ef916d597d33ad619d748b616bb7dbc3f0c36` and use Java 17. The successful local package build used Maven 3.6.1, a short source path, cached dependencies and:

```text
mvn -o -Dmaven.repo.local=<PRIVATE_CACHE> -Dmaven.test.skip=true -Dmaven.javadoc.skip=true package
```

Offline mode requires an already populated dependency cache; otherwise provision dependencies separately. CK test compilation and Javadoc were skipped, not passed. No CK source/POM modifications were required. The 20 MB JAR is excluded from Git; its original SHA-256 is retained in the manifest. A newly built JAR need not be byte-identical because build metadata may differ; record its hash.

With a local Apktool repository containing `40d427e5`, a CK dependency-inclusive JAR and a fresh output directory:

```powershell
python extension/apktool/publication/run_ck_pair.py --repo ../apktool-study --jar $ckJar --out "$env:TEMP/cs4928-ck-new"
```

The script uses read-only Git archives, materializes all 145 tracked Java files, applies the exact reviewed field deletion to the second snapshot, and runs one JAR with options `false 0 false`. It does not change a checkout or index. The original executed wrapper reproduced all 166 class rows' metric columns after ignoring source-path differences. Inspect new output for machine paths before publishing it.

## Behavioural evidence

The existing logs record successful forced runs of:

```powershell
.\gradlew.bat :brut.apktool:apktool-lib:test --rerun-tasks --no-daemon --console=plain
```

Both sides have 176 tests, zero failures/errors and one skip, with zero identity/outcome differences. This is evidence within tested scenarios, not universal equivalence. Full retesting requires separate complete Apktool source copies and preserved XML output for each run; the source excerpts here are not complete Gradle projects.
