# Apktool extractor validation — 4 November 2026

**Verdict: full feature equivalence failed.** Corrected member identities are usable diagnostic evidence, but the calls, visits and resulting structural similarities are not validated. The external transfer component of RQ2 remains inconclusive.

## Evidence and checks

The reference pair is [`Mapper_before.java`](../../results/event_a/source/Mapper_before.java) and the authors' [`13+MapperHelper+MapperTemplate.csv`](../../upstream/dataset/refactor_example_position/13+MapperHelper+MapperTemplate.csv). Both original Windows diagnostic folders are preserved in the private archive. Their metadata records source, reference and extractor SHA-256 hashes and javalang 0.13.0.

We independently reran both archived diagnostic scripts in isolated temporary layouts. Their candidate CSVs, comparison CSVs and summaries reproduce the originals. The original Apktool extractors were not modified. [Recomputed counts](RESULTS_SUMMARY.json) also agree with the saved comparison CSVs.

| Check | Original v2 diagnostic | Targeted member/signature correction |
| --- | ---: | ---: |
| Reference / candidate members | 50 / 41 | 50 / 50 |
| Exact name/type matches | 38 | 50 |
| Missing / extra identities | 12 / 3 | 0 / 0 |
| Parser exceptions | 0 | 0 |
| Index agreement | 0/38 | 50/50 |
| Inner invocations | 31/38 | 37/50 |
| Calls | 13/38 | 21/50 |
| Field visits | 21/38 | 30/50 |
| Full Java token sequence | 34/38 | 45/50 |
| Annotations | 14/38 | 22/50 |
| External invocations | 38/38 | 50/50 |

The external-invocation comparison matches empty representations. It does not test cross-type binding. Invocation/visit comparisons use token multisets, preserving occurrence counts; full text is compared as Java tokens. Exact identity and index agreement do not establish semantic feature equivalence.

## Concrete remaining mismatches

The raw examples, including both reference and candidate values, remain in the private archive. The compact summary identifies representative failures.

- Nested signatures: the original diagnostic collapsed `newSelectKeyMappedStatement(MappedStatement,EntityHelper.EntityColumn)` to `...EntityColumn`, and erased `List<ResultMapping>` in `processMap` and `toPropertySet`. The targeted diagnostic restores these identities and nested enum/class members.
- Ownership and incoming calls: the reference attributes calls to `Config`, including `getSelectReturnType`, `getBEFORE` and `getIDENTITY`. The candidate uses `MapperHelper` for those tokens and misses `EntityHelper.EntityColumn` calls such as `getGenerator` and `getProperty`.
- Field ownership: `setUUID(String)` has reference visits `Config+config` and `Config+UUID`; the candidate emits `MapperHelper+config` and `MapperHelper+UUID`. This shows disagreement with the authors' encoding, not independent proof that every reference owner is semantically correct.
- Shadowing: `processMap` declares a local `Map cameHumpMap` (source line 825), whereas the nested Config also declares a field of that name (line 110). The candidate emits two `MapperHelper+cameHumpMap` field visits for the local map; the reference has no field visits for this method.
- Missing calls: `getDatabaseDialect(String)` has 18 reference `String+equalsIgnoreCase(String)` occurrences and no candidate calls. Across the 50 identities, **563 reference call-token occurrences are absent**, independently counted as the reference-minus-candidate multiset difference.

These failures affect structural input, not merely formatting. The group did not implement a binding-aware extractor after the diagnostic showed substantial call and field-visit disagreement; the external comparison was therefore treated as exploratory. There is no validated structural matrix or valid external transfer verdict.

## Version lineage and interpretation

The private archive retains v1–v4 and both diagnostics. Inspection confirms v2 repairs declaration-text/modifier handling and field-qualifier handling; v3 adds local inner-invocation information and a bounded overload correction; v4 adds heuristic client-call information. Human review identified problems in the earlier extractor. The targeted Mapper correction is a separate diagnostic and was **not** silently substituted into the Apktool algorithm inputs.

The preserved v2/v3/v4 algorithm inputs and their result hashes are recorded in [RESULTS_SUMMARY.json](RESULTS_SUMMARY.json). All three result files name seed 2026 and `sentence-transformers/all-mpnet-base-v2`. Input hashes match the copied originals. Historical package versions and the exact edited invocation used for v3/v4 were not recorded in those JSONs, so provenance is incomplete at that level. The archived portable runner supplies explicit version selection for future reproduction.

See [README](README.md) for diagnostic reruns and [the ground-truth sensitivity report](GROUND_TRUTH_SENSITIVITY.md). Exploratory results are pipeline checks only. MapperHelper and NetClient are from the authors' dataset and do not supply the missing external cases.
