# Ground truth and exploratory score sensitivity

Recorded retrospectively on 4 November 2026, after the preliminary results were inspected. Neither labeling convention repairs the failed extractor validation.

## As-run labels and retrospective sensitivity

The [historical Apktool diff](README.md#external-source-and-reproduction) confirms ten ordinary methods moved from `AndrolibResources` to `Framework`. The **declaration-only convention was the actual as-run primary analysis**: ten methods and zero fields were labelled moved in [apktool_ground_truth.csv](apktool_ground_truth.csv). The original candidate labels and saved algorithm results were not changed.

A later, **retrospective sensitivity analysis** considered semantic ownership of `mFrameworkDirectory`. Both classes retain a declaration with that name at `40d427e5`, but only Framework's field is used; its reads/writes moved with `getFrameworkDirectory`. Under this alternative, the ten methods and this one field are treated as moved. It tests label sensitivity rather than replacing the as-run primary labels. The authors' MapperHelper example also marks `msIdSkip` removed although its old declaration remains in [`Mapper_after.java`](../../results/event_a/source/Mapper_after.java), illustrating ambiguity without establishing a universal labeling rule.

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

These are the before-source/candidate signatures. Framework spells the nested parameter as `ARSCDecoder.FlagsOffset[]`; the original imports that same nested type as `FlagsOffset`. The [compact method mapping](RESULTS_SUMMARY.json) verifies the ten removals/additions with this qualification accounted for.

## Fixed-partition sensitivity experiment

The saved v4 groups were held fixed while the alternative truth partition was rescored with the repository's `mojo.MoJo` evaluator. This sensitivity calculation did not rerun an algorithm or overwrite saved outputs. Rescoring with the as-run declaration-only labels reproduces the three original overall scores.

**Scale warning:** the existing runner calls these values MoJoFM, but applies the upstream transformation `max(0, (raw MoJoFM percentage - 50) / 50)`. The percentages below are this transformed score multiplied by 100, not raw MoJoFM. Both forms are retained in [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json).

| Fixed v4 partition | Declaration-only as run | Semantic-field sensitivity |
| --- | ---: | ---: |
| Bavota | 65.52% | 62.06% |
| ClassSplitter | 62.06% | 58.62% |
| ClassSplitter without position | 55.18% | 51.72% |

For example, ClassSplitter's raw MoJoFM is 81.03% under the as-run convention and 79.31% under the sensitivity convention. The ranking remains the same; neither score establishes transfer because structural input failed validation and only one external case was examined. ClassSplitter's saved partition does not recover all ten moved methods as one extracted group.

## Provenance

| Candidate | Result location | Bavota / ClassSplitter / without position (transformed overall) |
| --- | --- | --- |
| v2 | archived v2 result | 0.6552 / 0.6552 / 0.5172 |
| v3 | archived v3 result | 0.6552 / 0.6206 / 0.5518 |
| v4 | archived v4 result | 0.6552 / 0.6206 / 0.5518 |

Each row uses its own versioned input and cache, seed 2026, the same named embedding model and the original zero-moved-field labels. These are different inputs, not repeated measurements of one validated dataset. [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json) records verified input, result and cache SHA-256 hashes, plus the saved v4 partition indices. Full RSF truth/candidate partitions for both sensitivity scenarios are preserved in the private archive. The original labels are unchanged.
