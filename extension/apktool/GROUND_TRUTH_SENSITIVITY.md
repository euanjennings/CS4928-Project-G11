# Ground truth and exploratory score sensitivity

Recorded retrospectively on 4 November 2026, after the preliminary results were inspected. Neither labeling convention repairs the failed extractor validation.

## Labeling decision

The historical [Java diff](publication/historical_refactoring.patch) confirms ten ordinary methods moved from `AndrolibResources` to `Framework`. Both classes retain a declaration named `mFrameworkDirectory` at `40d427e5`, but only Framework's version is used. Its read/write operations belong to `getFrameworkDirectory`, which moved. This study therefore uses **semantic ownership** as its primary exploratory convention: the ten methods and `mFrameworkDirectory` are moved; the other 49 candidate members are retained. The primary label does not claim the old declaration disappeared.

The secondary **declaration-only** convention marks the ten methods moved and zero fields moved, preserving the original candidate labels and comparison files. In the authors' MapperHelper sample, `msIdSkip` is labeled removed even though its old declaration and references remain in [`Mapper_after.java`](../../results/event_a/source/Mapper_after.java). This shows that a declaration-only interpretation is not universally consistent with that sample. It does not establish a universal author rule or make the Apktool primary label beyond dispute.

Candidate membership is 60: 43 ordinary methods, two constructors and 15 fields. The ten historical moved methods are:

```text
getFrameworkApk(int,String)
emptyFrameworkDirectory()
listFrameworkDirectory()
installFramework(File)
installFramework(File,String)
publicizeResources(File)
publicizeResources(byte[])
publicizeResources(byte[],FlagsOffset[])
getFrameworkDirectory()
getAndroidFrameworkResourcesAsStream()
```

These are the before-source/candidate signatures. Framework spells the nested parameter as `ARSCDecoder.FlagsOffset[]`; the original imports that same nested type as `FlagsOffset`. The [parsed method mapping](publication/verified/method_mapping.json) verifies the ten removals/additions with this qualification accounted for.

## Fixed-partition sensitivity experiment

The saved v4 groups were held fixed. We changed only the truth partition and used the repository's shipped `mojo.MoJo` evaluator in new output files. No algorithm was rerun, no seed was changed and no old output was overwritten. The declaration-only rescoring exactly reproduces all three original overall scores.

**Scale warning:** the existing runner calls these values MoJoFM, but applies the upstream transformation `max(0, (raw MoJoFM percentage - 50) / 50)`. The percentages below are this transformed score multiplied by 100, not raw MoJoFM. Both forms are retained in [sensitivity.json](publication/verified/sensitivity.json).

| Fixed v4 partition | Declaration-only secondary | Semantic-field primary |
| --- | ---: | ---: |
| Bavota | 65.52% | 62.06% |
| ClassSplitter | 62.06% | 58.62% |
| ClassSplitter without position | 55.18% | 51.72% |

For example, ClassSplitter's raw MoJoFM is 81.03% under the secondary convention and 79.31% under the primary convention. The ranking remains the same, but this is not evidence for or against transfer because structural input failed validation and only one external case was examined. ClassSplitter's saved partition does not recover all ten moved methods as one extracted group.

## Provenance

| Candidate | Result location | Bavota / ClassSplitter / without position (transformed overall) |
| --- | --- | --- |
| v2 | [results/comparison.json](results/comparison.json) | 0.6552 / 0.6552 / 0.5172 |
| v3 | [results_v3/comparison.json](results_v3/comparison.json) | 0.6552 / 0.6206 / 0.5518 |
| v4 | [results_v4/comparison.json](results_v4/comparison.json) | 0.6552 / 0.6206 / 0.5518 |

Each row uses its own versioned input and cache, seed 2026, the same named embedding model and the original zero-moved-field labels. These are different inputs, not repeated measurements of one validated dataset. [provenance.json](publication/verified/provenance.json) records verified input, result and cache SHA-256 hashes. Full member partitions remain in the original result JSONs; RSF truth and candidate partitions for both sensitivity scenarios are in [verified/](publication/verified/). The original labels and staged files remain unchanged.
