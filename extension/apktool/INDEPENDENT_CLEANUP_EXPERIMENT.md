# Independent Apktool cleanup experiment

Completed locally on 4 November 2026. **Recommendation: retain the historical Framework extraction, accept the tested unused-field cleanup, and do not extract another class on the present evidence.**

## Controlled change

The baseline is the pristine historical-after revision `40d427e5`, not the pre-extraction revision `9c495cae`. The existing isolated cleanup worktree has exactly one tracked-file change: deleting `private File mFrameworkDirectory = null;` and its adjacent blank line from `AndrolibResources`. The active `private ExtFile mFramework = null;` remains. The [exact patch](publication/cleanup.patch) and [source snapshots](publication/source/) preserve the change.

Source inspection found no remaining access to that field in AndrolibResources. Framework owns its own actively used field. A tracked Java-source search found no `getDeclaredField` or `Class.forName` usage indicating reflective access to the removed field. This bounded source check cannot rule out unknown external reflective clients.

The original developers implemented the Framework extraction. The group's independent implementation is this much smaller field removal, already present before this handover was executed.

## Behaviour within the tested scenarios

Existing logs record the same forced task for pristine-after and cleanup-after:

```powershell
.\gradlew.bat :brut.apktool:apktool-lib:test --rerun-tasks --no-daemon --console=plain
```

Both logs say `BUILD SUCCESSFUL` and 11 tasks executed. The handover records exit code 0 for both; an exit code is not independently encoded in the saved text logs. We did not repeat these already successful Gradle runs.

| Evidence | Baseline | Cleanup |
| --- | ---: | ---: |
| XML reports | 42 | 42 |
| Tests | 176 | 176 |
| Failures / errors | 0 / 0 | 0 / 0 |
| Skipped | 1 | 1 |
| Passing | 175 | 175 |

Reparsing all XML reports and comparing testcase class/name/outcome multiplicities gives **zero differences**. [tests.json](publication/verified/tests.json) and [testcases.csv](publication/verified/testcases.csv) retain the check. Publication XML sets, with hostnames/environment properties/console streams removed but every test result retained, are archived in [baseline_xml.zip](publication/evidence/baseline_xml.zip) and [cleanup_xml.zip](publication/evidence/cleanup_xml.zip), alongside path-redacted Gradle log derivatives.

The tests are identical across this cleanup comparison, as the Git diff changes only the production field. This supports equivalence within the observed scenarios, not universal behavioural equivalence. The historical before/after extraction comparison is different: its diff changes `TestUtils.java` and `SharedLibraryTest.java` to use Framework. SharedLibraryTest exercises `installFramework`.

## Fresh matched CK measurements

CK source commit: `8a1ef916d597d33ad619d748b616bb7dbc3f0c36`, version `0.7.1-SNAPSHOT`. Built offline in a unique short temporary path from copied source/build files, using cached Maven 3.6.1 and Java 17.0.20.1. The successful package command used `-Dmaven.test.skip=true -Dmaven.javadoc.skip=true`. CK's own tests and Javadoc were skipped; the package build succeeded. Initial wrapper network access, cache access and Javadoc failures are preserved in local build logs excluded from publication.

We used a read-only Git archive rather than creating another worktree. This avoids changing Git metadata. Both measurement snapshots contain the same 145 tracked Java files, including tests, and no generated build artifacts. The cleanup snapshot substitutes the actual reviewed working-copy file. Hashes show exactly one Java file differs; normalizing line endings confirms exactly the intended deletion. The exact same JAR and options were used: `false 0 false` (no JAR scanning, automatic partition size, no field/variable CSVs), with CK's default `.git` exclusion and no additional ignored directories. Both runs exited 0 and emitted 166 class rows; only logging-configuration warnings appeared.

| AndrolibResources metric | Pristine-after | Cleanup-after | Delta |
| --- | ---: | ---: | ---: |
| Fields (`totalFieldsQty`) | 15 | 14 | -1 |
| LOC | 613 | 612 | -1 |
| Methods (`totalMethodsQty`, includes constructors) | 35 | 35 | 0 |
| CBO | 35 | 35 | 0 |
| LCOM* | 0.8971428 | 0.8897959 | -0.0073469 |
| WMC | 150 | 150 | 0 |

Framework is unchanged: 3 fields, 11 methods, 180 LOC, CBO 10, LCOM* 0.72727275, WMC 45. All other classes' metric columns are unchanged after excluding snapshot-dependent `file` paths. Additional AndrolibResources changes are private fields 14→13, assignments 99→98 and variables 73→72; see [ck_delta.json](publication/verified/ck_delta.json).

CK's `LCOMNormalized` averages per-field non-access proportions. Deleting a field used by no method removes a maximally unshared attribute from that average. The small LCOM* decrease is therefore consistent with the cleanup itself; method responsibilities and interactions have not improved. No claim of a substantial architectural or maintenance benefit follows.

Published CSV derivatives (only the source-path column is normalized): [pristine class.csv](publication/ck_pristine_20261104/class.csv), [cleanup class.csv](publication/ck_cleanup_20261104/class.csv). [The run manifest](publication/ck_run_manifest.json) records portable command templates, Java version, timestamp, JAR hash and separately identified original/published CSV hashes. [Source hashes](publication/verified/ck_source_hashes.json) record the matched scope. The JAR remains locally preserved outside Git; rebuilding instructions are in the [runbook](publication/README.md). The [publication provenance](publication/PUBLICATION_PROVENANCE.json) distinguishes original evidence from path-normalized derivatives.

## Independent alternatives

1. **No change at 40d427e5:** avoids a new source change but leaves a private field whose only purpose moved to Framework. It also leaves the same high measured lack of cohesion.
2. **Small internal cleanup:** accept the implemented deletion. It removes misleading state with a small, reviewable diff, unchanged coupling/complexity and identical observed test outcomes. This is the supported choice. No additional helper refactoring was implemented or tested.
3. **Further Extract Class:** packaging is a plausible candidate responsibility (`aaptPackage`, `aapt1Package`, `aapt2Package`, AAPT binary helpers and compression-list preparation). However, it uses `config`, SDK/version/package state, shared-library flags, filesystem operations and process execution. Extracting it would require a deliberate state-transfer/interface design. Resource decoding also shares ResTable/ResPackage and decoder helpers. There is no validated algorithm boundary, implemented alternative, matched test run or measured coupling benefit for either proposal. Recommend against speculative extraction now.

The historical split has a defensible concrete boundary: AndrolibResources calls Framework in `loadFrameworkPkg`, while Framework has no direct reference back; Main and ApkBuilder call Framework directly for framework operations. This supports retaining the existing split. It does not prove a globally acyclic dependency graph or lower whole-system coupling. CBO values must not be added across classes.
