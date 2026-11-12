# Apktool design case study

## 1. Overall result

**Research Question 2:** Does ClassSplitter's position-aware advantage transfer to Extract Class refactorings mined from Java projects outside the authors' dataset, and what does that imply for a concrete Extract Class decision (including no structural change) in one of those systems, verified by tests and cohesion/coupling metrics?

This study examined one external case, Apktool, rather than three planned. Its feature extractor failed equivalence validation against the authors' reference data, so the saved comparisons are exploratory and **do not establish external transfer**. The design result is narrower: Apktool's historical Framework extraction had a clear responsibility boundary, and an unused field could be removed without changing tested outcomes.

Event A examined two held-out cases from the authors' own dataset, not two additional external cases. Its mean overall scores were ClassSplitter 0.3839 and Bavota 0.4386 ([Event A report](../EVENT_A.md)). The separate RQ1 reproduction on 133 author cases reported 0.4958 and 0.3353 respectively ([M2 report](../results/M2_SUMMARY.md)). Neither result fills the missing Apktool transfer sample. The [preregistration amendment](../docs/PREREGISTRATION.md) and ground-truth decisions below were made after preliminary outcomes were inspected.

## 2. Historical Framework extraction and metrics

Apktool's developers moved ten framework-related methods from `brut.androlib.res.AndrolibResources` into `brut.androlib.res.Framework` between [`9c495cae295dbff3aab378da4a889d8b926f081a`](https://github.com/iBotPeaches/Apktool/commit/9c495cae295dbff3aab378da4a889d8b926f081a) and [`40d427e5bdf5c204c58022cef3b369f34e19b043`](https://github.com/iBotPeaches/Apktool/commit/40d427e5bdf5c204c58022cef3b369f34e19b043). The [ground-truth report](../extension/apktool/GROUND_TRUTH_SENSITIVITY.md) lists their signatures. Framework has direct callers in Main and ApkBuilder; AndrolibResources calls it to load framework resources, with no direct reverse reference. This supports the boundary but does not prove system-wide acyclicity.

| CK class metric | AndrolibResources before | AndrolibResources after | Framework after |
| --- | ---: | ---: | ---: |
| Methods, including constructors | 45 | 35 | 11 |
| LOC | 784 | 613 | 180 |
| CBO | 38 | 35 | 10 |
| LCOM* | 0.9081481 | 0.8971428 | 0.72727275 |
| WMC | 194 | 150 | 45 |

These [historical measurements](../extension/apktool/RESULTS_SUMMARY.json) show redistribution of complexity: combined WMC is 195 after versus 194 before, and combined LOC is 793 versus 784. CBO values cannot be added across classes because dependencies may overlap. The historical CK command and JAR provenance were not fully recorded.

A fresh forced Gradle run at the before revision succeeded: 42 XML reports, 176 tests, 175 passed, one skipped, zero failures or errors. The historical-after baseline also had 176 tests with the same testcase identities and outcomes. TestUtils and SharedLibraryTest changed with the extraction, so these are outcomes under related but modified test sources; they do not prove behavioural equivalence for all clients.

## 3. Algorithm results and interpretation

The algorithm runs used the **declaration-only** ground truth: ten methods moved and zero fields moved. A later, explicitly retrospective sensitivity analysis treated the field `mFrameworkDirectory` as semantically moved because Framework owns its active use even though the old declaration remained. This alternative rescored fixed v4 partitions; it did not rerun either algorithm. The [ground-truth report](../extension/apktool/GROUND_TRUTH_SENSITIVITY.md) gives both conventions and the score transformation.

| Saved input | Bavota | ClassSplitter | ClassSplitter without position |
| --- | ---: | ---: | ---: |
| v2 | 0.6552 | 0.6552 | 0.5172 |
| v3 | 0.6552 | 0.6206 | 0.5518 |
| v4 | 0.6552 | 0.6206 | 0.5518 |

These are transformed MoJoFM scores, not raw percentages. Position-aware ClassSplitter exceeded its no-position variant in all three comparisons, a direction relevant to the hypothesis. Bavota tied it on v2 and exceeded it on v3/v4. In saved v4, Bavota placed all 60 members in one group. Only ten methods were labelled moved, so leaving the retained majority together can score well without identifying a useful extraction. On Event A's NetClient, Bavota likewise grouped all 61 members and scored 0.6272 versus ClassSplitter's 0.5594. A high score alone is not a design recommendation.

The saved ClassSplitter v4 first group contains 22 methods. Eight have names that later appear in the developers' ResourcesDecoder: `decodeManifest`, `adjustPackageManifest`, `decodeManifestWithResources`, `getResFileDecoder`, `getManifestFileDecoder`, `getResXmlSerializer`, `generateValuesFile` and `generatePublicXml`. Other members later went to ResTable or already belonged to Framework. This overlap is suggestive, but the group is not the later extraction boundary. The [validation diagnostic](../extension/apktool/VALIDATION_REPORT.md) matched 50/50 member identities but only 21/50 call features and 30/50 field visits; the structural input was not equivalent. No transfer conclusion follows from the grouping.

## 4. Design alternatives and decision

The group's bounded independent change at the historical-after revision removed the unused `private File mFrameworkDirectory = null;` declaration and its blank line, leaving Framework's active field intact ([exact patch](../extension/apktool/publication/cleanup.patch)). Both pristine-after and cleaned-after forced runs had 176 tests, 175 passes, one skip and zero failures; all testcase identities and outcomes matched. Matched CK runs used the same JAR, 145 tracked Java files and options `false 0 false`. AndrolibResources changed from 15 to 14 fields, 613 to 612 LOC and LCOM* 0.8971428 to 0.8897959; methods (35), CBO (35) and WMC (150) were unchanged. Removing an unused field reduces CK's field-based lack-of-cohesion average partly by changing its denominator. It does not show substantially better method interactions.

Apktool's maintainers had already made the [identical field deletion in commit `ab6f1b41` (#3116)](https://github.com/iBotPeaches/Apktool/commit/ab6f1b416e0a3f21dea6853bd26bfe672cae12f7), alongside other decoder changes. The group's implementation and tests therefore provide convergent confirmation of a small cleanup, **not a novel refactoring**.

The original alternatives were to leave the field, remove it, or extract more responsibilities. The later [`a7e2e3e5` change (#3124)](https://github.com/iBotPeaches/Apktool/commit/a7e2e3e5e10ad223764cdac8c23cb9ee189c569f) introduced AaptInvoker and ResourcesDecoder, redistributed state and behaviour into other classes, and removed AndrolibResources. This developer change shows that further extraction was feasible and weakens any categorical recommendation against it. The supported decision for the tested revision is the small field cleanup; whether the larger extraction improves quality requires a separate matched test and CK comparison across its own before/after revisions. That later change also modifies other source and tests, so its effects cannot be attributed to extraction alone without analysis.

## 5. Limitations and evidence

The [compact evidence guide](../extension/apktool/README.md) provides the source commits, scripts, input hashes and [results](../extension/apktool/RESULTS_SUMMARY.json). Retrospective reruns of the committed wrapper reproduced v2 and v3 result files byte-for-byte. The v4 scores reproduced, but one field changed ClassSplitter group assignment in the rerun; the saved v4 file did not reproduce byte-for-byte. This partition-level difference and the original dirty working-tree status are disclosed in the provenance record. They further limit interpretation of the exploratory grouping.

The case remains one external system with an unvalidated feature extractor. Historical test sources changed, the original historical CK environment is incomplete, and the later #3124 extraction has not received a matched test/metric comparison in this study. Complete raw XML, method-level CK data and diagnostic outputs are preserved outside this repository; the concise published results can be checked with the included scripts. These limits are also recorded in [deviations](../docs/DEVIATIONS.md).
