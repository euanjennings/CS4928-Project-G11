# Event A — Decomposing God Classes

Event A tests whether ClassSplitter's M2 advantage transfers to two held-out classes from different projects: MapperHelper from Mapper (case 13) and NetClient from Mindustry (case 3490).

Using the M2 method, supplied similarity cache and seed 2026, ClassSplitter's mean overall score was **0.3839**, compared with **0.4386** for the Bavota baseline. The mean difference changed from approximately **+0.1605** at M2 to **−0.0547**, so the predicted advantage did not transfer to these cases.

| Material | Location |
|---|---|
| Prediction, cases and decision criteria | [PREDICTION.md](extension/event_a/PREDICTION.md) |
| Method, results, positional examples and design implication | [REPORT.md](results/event_a/REPORT.md) |
| Environment and reproduction commands | [README.md](extension/event_a/README.md) |
| Primary scores and final partitions | [primary/result.json](results/event_a/primary/result.json) |
| Validation results | [validation.json](results/event_a/validation.json) |
| Member-pair analysis | [position_pairs.csv](results/event_a/position_pairs.csv) |
| Source versions and audit | [source_audit.json](results/event_a/source_audit.json) |

The primary result, repeated-seed checks and exploratory diagnostics form one evaluation. Diagnostics are reported separately because they change the method being evaluated. The conclusion is limited to the selected cases and the supplied cached similarities.
