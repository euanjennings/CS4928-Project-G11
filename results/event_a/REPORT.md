# CS4928 G11 — Event A: Decomposing God Classes

The predicted ClassSplitter advantage did not transfer to these two held-out cases under the unchanged M2 method and supplied cache. The mean gap changed from approximately +0.1605 at M2 to −0.0547. This limits the generality of our M2 finding; it does not invalidate the reproduced M2 result.

## Cases and prediction

| Case | Project and original class | Parent (input) commit | Refactoring commit |
|---|---|---|---|
| 13 | Mapper: com.github.abel533.mapper.MapperHelper | 5fda159c7bcf1ec423ba27bd1bb4bacdcdd4b521 | 0586a42d5e36d8eab6a6e85f1a19d96adf861094 |
| 3490 | Mindustry: mindustry.core.NetClient | a64efce5a0a171d88675f3beccaa617641b8ba78 | 82742339a3f001ac5ddd7d1c5002738d999c8bfa |

The selected rows come from `upstream/dataset/GodClassRefactorForPositionStudyDictionary.csv`, a separate catalogue from M2's 133 cases. Neither selected class nor project occurs in M2's catalogue (see [source_audit.json](source_audit.json)). MapperHelper has 37 methods and 13 fields; NetClient has 47 methods and 14 fields. The input CSVs are named `13+MapperHelper+MapperTemplate.csv` and `3490+NetClient+Menus.csv` in `upstream/dataset/refactor_example_position/`.

Our stated prediction was a positive ClassSplitter mean advantage smaller than M2's approximately 0.1605. Bavota matching or exceeding ClassSplitter would challenge transfer; an equal or larger positive gap would reject the smaller-gap prediction. The hypothesis and decision criteria are recorded in [PREDICTION.md](../../extension/event_a/PREDICTION.md).

## Frozen method and primary results

The experiment wrapper uses the same upstream implementation, cache, model identifier, defaults and sequence of calls as `repro/run_repro.py`. Eight key input hashes, including the cache, original runner, M2 results, two case files and case catalogue, match the hashes preserved from the earlier execution; see [input comparison](provenance/input_comparison.json). Cases are processed as 13 then 3490, with Python random seed 2026. The algorithm is not tuned to the held-out outcomes. NumPy and Gensim defaults remain as in M2. The scorer compares partitions with the authors' retained/removed labels. Its reporting transform is `max(0, (raw MoJoFM percentage − 50) / 50)`.

| Case | CS overall | Bavota overall | CS methods | Bavota methods | CS fields | Bavota fields |
|---|---:|---:|---:|---:|---:|---:|
| MapperHelper | 0.2084 | 0.2500 | 0.2572 | 0.2572 | 0.0000 | 0.0910 |
| NetClient | 0.5594 | 0.6272 | 0.4222 | 0.5112 | 0.6924 | 1.0000 |
| Mean | **0.3839** | **0.4386** | 0.3397 | 0.3842 | 0.3462 | 0.5455 |

Raw overall MoJoFM percentages are 60.42 versus 62.50 for MapperHelper, and 77.97 versus 81.36 for NetClient. Each case has saved predicted and reference RSF files for all three metrics and both algorithms. Java MoJo is run again on each pair to verify the reported transform.

The primary evidence is [primary/result.json](primary/result.json). The primary run matched all twelve reference scores. A repeat compared scores and final partitions; 30 additional seeds checked sensitivity to the baseline's random assignment of unvisited fields. [validation.json](validation.json) records all checks, including the original M2 runner's 798 scores and its 12 held-out scores with only the catalogue redirected. [seed_summary.csv](seed_summary.csv) contains the seed comparison. The two selected cases provide a bounded transfer test rather than a population estimate.

## Where position helps and misleads

[position_pairs.csv](position_pairs.csv) traces the examples through every saved stage, using member indices and names from the input data.

* **Local help in NetClient:** the initial group `[37,38,41,43]` contains `effect`, `effectReliable`, `setRules` and `setPosition`. Splitting by position keeps `[37,38]` together and separates `[41]` and `[43]`. That distinction agrees with the later presentation-versus-state boundary. The final merge rejoins these responsibilities, so this is evidence of useful intermediate separation, not a successful final extraction.
* **Misleading separation in MapperHelper:** `setUUID` (11) and `getUUID` (15) are together initially but split apart by the positional step, despite sharing configuration state.
* **Misleading merging in MapperHelper:** the position-ordered singleton merge combines retained configuration methods, including `isCameHumpMap` (18), with removed SQL utilities, including `dynamicSQL` (23). Nearby declarations do not establish one responsibility.
* **A further NetClient limitation:** `setHudText` (30) and its reliable wrapper (32) are split apart by position even though both are extracted into Menus.

## Design implication

The developers moved 11 consecutive presentation methods, indices 30–40, from NetClient into `mindustry.ui.Menus`. The saved [source audit](source_audit.json) checks that all 11 declarations occur before the refactoring, disappear from NetClient afterwards, and occur in Menus. Original sources and exact URLs are in [source/provenance.json](source/provenance.json).

Neither algorithm recovers that extraction. Bavota retains all 61 NetClient members in one group, despite its higher score. ClassSplitter produces three groups and mixes all 11 moved methods with retained methods in its largest group. MapperHelper's final ClassSplitter result isolates only members 2, 3 and 4.

The Extract Class decision depends on shared responsibility, cohesion and coupling: UI presentation and network/world-state behavior have different reasons to change. Calls, shared fields and wrappers provide evidence for that boundary alongside physical proximity. The single-responsibility principle supports reviewing that separation; the evidence does not justify introducing a design pattern. This work evaluates proposed groupings and historical source changes; it does not implement or test a new refactoring in either project.

## Separate diagnostics and limitations

1. **Method-position diagnostic:** the authors' `PS=0, MS=1, CS=1` switch disables method position weighting and position steps, but retains field-position fallback. CS overall scores become 0.5834 (MapperHelper) and 0.5254 (NetClient), mean 0.5544. Thus the net contribution of these position mechanisms varies by case. This is a diagnostic, not a replacement for the frozen result.
2. **Structural cache sensitivity:** recalculating ClassSplitter's structural MS matrix in memory disagrees with 182/666 unordered method pairs for MapperHelper and 372/1081 for NetClient. Recomputed-MS scores are 0.2916 and 0.5932, mean 0.4424, slightly above Bavota's unchanged 0.4386. The primary claim therefore applies to the supplied cached setup. The origin of the discrepancies has not been established. The cache file itself remains unchanged.
3. **Reference-label limitation:** the dataset labels retained/removed members; these labels are not perfect proof of an actual move. For example, MapperHelper's field `msIdSkip` (20) is marked removed but remains declared in MapperHelper after the refactoring. We preserve the labels for comparability and disclose the limitation.

## Reproducibility

[extension/event_a/README.md](../../extension/event_a/README.md) documents the environment, primary experiment and complete validation suite. [input_manifest.json](../../extension/event_a/input_manifest.json) checks the delivered code and experimental inputs; [evidence_sha256.json](evidence_sha256.json) checks the supporting files.
