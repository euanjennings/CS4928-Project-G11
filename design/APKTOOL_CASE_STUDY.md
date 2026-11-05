# Apktool Design Case Study - Week 9

Updated locally on 4 November 2026. **Recommendation: retain the developers' Framework extraction, accept the independently implemented unused-field cleanup, and avoid further speculative extraction.** The comparative transfer question remains inconclusive.

## 1. Executive Summary

This case study investigates whether ClassSplitter's position-aware advantage transfers to an external Java project and evaluates a concrete Extract Class design decision using Apktool.

We examined Apktool's historical extraction of ten methods from `AndrolibResources` into a new `Framework` class. We compared the source structure, dependencies, cohesion, coupling and available test evidence to assess the original design change.

The investigation produced five main findings:

1. **Historical extraction:** Apktool's developers established a clearer responsibility boundary by moving framework-related operations into a dedicated class. However, the measured complexity was largely redistributed rather than eliminated.

2. **Independent improvement:** We identified an unused `mFrameworkDirectory` field remaining in `AndrolibResources` after the extraction and independently removed it.

3. **Verification:** Both the pristine historical-after version and our cleaned version produced identical outcomes across 176 tests: 175 passed, one skipped and zero failures. The cleanup reduced the field count from 15 to 14 and slightly improved measured cohesion, while coupling and complexity remained unchanged.

4. **Algorithm evaluation:** ClassSplitter and Bavota were executed on Apktool, but the structural input failed feature-equivalence validation. Their exploratory results therefore cannot establish whether ClassSplitter's advantage transfers to this project.

5. **Research limitations:** Only one external case was examined, compared with the three required by the original research plan.

**Final recommendation:** Retain the developers' Framework extraction, accept the independently verified unused-field cleanup, and avoid further extraction without stronger evidence.

The design decision is supported by the available source, test and metric evidence. However, Research Question 2 remains only partially answered.

---

## 2. Timeline of Work Completed

| Stage | Activity | Outcome |
| --- | --- | --- |
| 1. Original Reproduction | Reproduced ClassSplitter and Bavota on the authors' 133 published cases. | Confirmed ClassSplitter's reported advantage and completed the bounded Research Question 1 reproduction. |
| 2. External Case Selection | Selected Apktool and identified the historical extraction of `Framework` from `AndrolibResources`. | Established the original and refactored revisions for investigation. |
| 3. Historical Analysis | Examined the ten extracted methods, source changes, dependencies, historical tests and code-quality metrics. | Identified the benefits and limitations of the developers' extraction. |
| 4. Input Preparation | Developed successive Java input-extractor versions and constructed Apktool ground-truth data. | Generated candidate inputs for comparing ClassSplitter and Bavota. |
| 5. Algorithm Comparison | Executed ClassSplitter, Bavota and ClassSplitter without position information. | Produced exploratory comparisons against the historical extraction. |
| 6. Extractor Validation | Compared extracted features against the authors' MapperHelper reference data. | Achieved 50/50 member identity matches but identified substantial method-call and field-visit mismatches. |
| 7. Design Alternatives | Evaluated leaving the structure unchanged, removing unused state or extracting another class. | Selected the unused-field cleanup as the most proportionate intervention. |
| 8. Independent Implementation | Removed the unused `mFrameworkDirectory` field from `AndrolibResources`. | Implemented a small independent improvement without further structural changes. |
| 9. Testing and Metrics | Compared matched Gradle test outcomes and CK metrics before and after cleanup. | Verified identical outcomes across 176 tests, one fewer field and slightly improved measured cohesion. |
| 10. Final Evaluation | Reviewed algorithm validity, design evidence, research limitations and reproducibility. | Recommended retaining Framework, accepting the cleanup and avoiding further extraction without stronger evidence. |
| 11. Documentation | Prepared the case study, validation reports, experimental evidence and reproducibility scripts. | Prepared the research for repository review, with the external transfer question remaining inconclusive. |

**Current status:** The independent Apktool design investigation is complete within its documented scope. The external transfer study remains inconclusive because structural input validation failed and only one of the three planned external cases was investigated.

---

## 3. Research question and achieved scope

**Research Question 2:** Does ClassSplitter's position-aware advantage transfer to Extract Class refactorings mined from Java projects outside the authors' dataset, and what does that imply for a concrete Extract Class decision (including no structural change) in one of those systems, verified by tests and cohesion/coupling metrics?

The frozen plan required at least three external Java cases. Only Apktool was examined experimentally. Its structural input failed feature-equivalence validation, so this is a design case with exploratory algorithm evidence, not a completed transfer study. The [preregistration amendment](../docs/PREREGISTRATION.md) is explicitly retrospective: preliminary outcomes had already been inspected. The original question and plan remain unchanged.

RQ1 remains separately reproduced on the authors' 133 cases: ClassSplitter 0.4958 versus Bavota 0.3353 ([M2 report](../results/M2_SUMMARY.md)). Event A's MapperHelper and NetClient belong to the authors' dataset and do not count toward the three external cases.

## 4. Historical design change

The original class is `brut.androlib.res.AndrolibResources`. Apktool's developers extracted `brut.androlib.res.Framework` between `9c495cae` and `40d427e5`. The [preserved Java diff](../extension/apktool/publication/historical_refactoring.patch) shows the ten moved methods, listed with exact signatures in [the ground-truth report](../extension/apktool/GROUND_TRUTH_SENSITIVITY.md). The group evaluated this historical change; it did not independently implement it.

The boundary has concrete supporting evidence: AndrolibResources calls Framework to load framework resources, Framework does not refer directly back, and Main and ApkBuilder call Framework directly for framework operations. This avoids a direct cycle between the two classes and gives framework operations an independent entry point. It does not establish that the whole dependency graph is acyclic.

At the historical-after revision, AndrolibResources still declares `mFrameworkDirectory`, although its accesses moved with `getFrameworkDirectory` and Framework owns its own active field. This stale declaration is the basis for our independent cleanup.

## 5. Historical metrics and tests

The preserved historical CK CSVs measure the developers' extraction, not our cleanup:

| Metric | AndrolibResources before | AndrolibResources after | Framework after |
| --- | ---: | ---: | ---: |
| Methods, including constructors | 45 | 35 | 11 |
| LOC | 784 | 613 | 180 |
| CBO | 38 | 35 | 10 |
| LCOM* | 0.9081481 | 0.8971428 | 0.72727275 |
| WMC | 194 | 150 | 45 |

Sources: [historical before CSV](../extension/apktool/publication/evidence/metrics-before/class.csv) and [historical after CSV](../extension/apktool/publication/evidence/metrics-after/class.csv). Their original full measurement commands and JAR provenance were not preserved. The fresh matched pristine-after run reproduces the relevant after values.

AndrolibResources became about 22% smaller, but the LCOM* improvement is marginal and Framework's 0.727 is not strong cohesion. Combined WMC is 195 versus 194 before, and combined LOC is 793 versus 784. Most complexity was redistributed. CBO cannot be added across the two classes because dependencies can overlap, so these values do not demonstrate lower total coupling or measured maintenance productivity.

The previous case-study draft recorded successful historical-before and historical-after Gradle tests. The available handover evidence does not include the original historical-before XML/log set, so that earlier claim is retained as a prior report rather than a newly verified test result. Historical tests were also edited: TestUtils and SharedLibraryTest call Framework, and SharedLibraryTest exercises `installFramework`. Do not describe these historical test sources as byte-identical.

## 6. Independent cleanup and matched comparison

The separate cleanup worktree is based on `40d427e5`. Its entire tracked diff removes `private File mFrameworkDirectory = null;` and one blank line. The active `mFramework` remains. The [experiment report](../extension/apktool/INDEPENDENT_CLEANUP_EXPERIMENT.md) provides the exact patch, source checks, archived logs/XML, commands and limitations.

Both existing forced Gradle runs have 42 XML reports and **176 tests, 0 failures, 0 errors, 1 skipped**. Independent XML parsing found **zero testcase identity/outcome differences**. Both logs record `BUILD SUCCESSFUL` and 11 executed tasks. These are the same tests on the same historical-after baseline, unlike the historical extraction comparison. We did not repeat successful tests unnecessarily.

Fresh CK runs use one built JAR, matching Java-source scope and matching options:

| AndrolibResources metric | Pristine 40d427e5 | Independent cleanup |
| --- | ---: | ---: |
| Fields | 15 | 14 |
| LOC | 613 | 612 |
| Methods | 35 | 35 |
| CBO | 35 | 35 |
| LCOM* | 0.8971428 | 0.8897959 |
| WMC | 150 | 150 |

Deleting an unused field slightly changes CK's field-based cohesion average without changing method interactions. This is a modest removal of misleading state. It does not solve the remaining class's low cohesion or establish a major architectural improvement. Passing tests supports unchanged behaviour within the tested scenarios only.

## 7. Independent alternatives and decision

| Alternative at 40d427e5 | Evidence and consequence | Recommendation |
| --- | --- | --- |
| Leave unchanged | No new source change, but the obsolete field remains and LCOM* stays near 0.9. | Acceptable fallback, weaker than the verified cleanup. |
| Small internal cleanup | Remove the unused field; 175 passing and 1 skipped testcase retain their outcomes; CBO and WMC unchanged. | Accept the implemented deletion. |
| Extract another class | AAPT packaging shares configuration, SDK/version/package state and filesystem/process operations. No implemented boundary or measured coupling benefit exists. | Do not extract further on this evidence. |

The candidate packaging methods include `aaptPackage`, `aapt1Package`, `aapt2Package`, compression-list preparation and AAPT binary helpers. A new class would need a deliberate interface for their shared state. Resource decoding similarly shares ResTable/ResPackage and decoder helpers. High LCOM* alone does not identify a safe cohesive boundary. No additional internal helper changes or extractions were implemented or tested.

Retain the historical Framework split for its concrete dependency direction and direct clients. Accept the small independently verified cleanup. This recommendation combines code inspection, test evidence and measured size/cohesion/coupling, without treating either the historical developers' choice or exploratory algorithm output as authoritative.

## 8. Exploratory algorithms and validity

ClassSplitter and Bavota **have** been run experimentally, but the input is not validated. The Mapper diagnostic improved from 38 exact identities to 50/50, while calls matched only 21/50 and visits 30/50, with 563 missing reference call occurrences. [Validation report](../extension/apktool/VALIDATION_REPORT.md).

The saved v4 transformed overall scores are Bavota 0.6552, ClassSplitter 0.6206 and ClassSplitter without position 0.5518 under the original zero-moved-field convention. Rescoring the same fixed groups with the semantically moved field gives 0.6206, 0.5862 and 0.5172 respectively. These use the upstream transformation of raw MoJoFM, not raw MoJoFM percentages. [Ground-truth choices, input hashes, partitions and sensitivity](../extension/apktool/GROUND_TRUTH_SENSITIVITY.md).

Neither convention answers whether ClassSplitter's advantage transfers. Input bindings failed equivalence, one convenience-selected external case falls short of three, and the labeling/amendment decisions are retrospective. ClassSplitter did not recover the ten historical moved methods together as one group, but that observation on invalid features cannot disprove transfer.

## 9. Review package and limitations

The [publication runbook and evidence package](../extension/apktool/publication/README.md) contains archived extractor lineage, diagnostics, versioned input provenance, test archives, CK CSVs, exact patches and safe rerun scripts. Original experimental outputs remain locally preserved. Published CK/XML derivatives remove only the machine details documented in the runbook; results are unchanged.

The design experiment is complete at the scope of the field cleanup. A valid external transfer result, the missing two external cases, original historical-before test evidence and complete historical measurement environment remain unavailable. These limitations are disclosed in [DEVIATIONS.md](../docs/DEVIATIONS.md). The recommendation is ready for the group's review; it does not claim group approval or a validated transfer finding.