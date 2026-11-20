# Student Tracker change history: group G11 row (excerpt)

Source: the shared class workbook *Student Tracker*, sheet **RQs and Milestones**, row 15 (G11). Read from Excel's **Show Changes** pane on 2026-11-20 by Euan Jennings and transcribed here. Excel shows times in the viewer's local time (Europe/Dublin). Irish summer time ended on 2026-10-25, so entries before that date are UTC+1. UTC is given for each entry.

Only cells belonging to G11's row are included. Two edits by members of other groups touched our cells and are omitted:
- On 2026-10-09 a pasted range briefly overwrote F15/G15; it was reverted within two minutes.
- On 2026-11-11 a pasted range (Q12:Q16) put unrelated text into Q15; it was replaced by our Event B prediction on 2026-11-12.

"Guest User" is how the workbook records an editor who was not signed in; the member cannot be identified from the history.

This transcript is the preserved record; the Show Changes pane keeps only a limited history.

| Local time | UTC | Editor | Cell | Content after the edit |
| --- | --- | --- | --- | --- |
| 2026-09-25 18:00 | 17:00 | Guest User | C15 (RQ1) | "Using the authors' published artefact and their dataset of 133 real-world God classes, does ClassSplitter reproduce its reported decomposition accuracy (mean MoJoFM) and its reported advantage over the Bavota baseline, and which properties of the artefact affect the stability of that result?" |
| 2026-09-25 18:03–18:04 | 17:03–17:04 | Guest User | D15 (RQ2) | "Does ClassSplitter's position-aware advantage transfer to Extract Class refactorings mined from Java projects outside the authors' dataset, and what does that imply for a concrete Extract Class decision (including no structural change) in one of those systems, verified by tests and cohesion/coupling metrics?" (C15 and D15 re-entered unchanged at 18:04; no later edits) |
| 2026-10-30 14:33 | 14:33 | Guest User | K15 (Event A prediction) | "For Event A, the held-out cases we've chosen are MapperHelper from Mapper (position-study case 13, parent commit 5fda159) and NetClient from Mindustry (position-study case 3490, parent commit a64efce). Neither was used in M2. Using the unchanged M2 decomposition method and seed 2026, we expect ClassSplitter to achieve a higher mean overall MoJoFM than the Bavota baseline, but with a smaller gap than M2's 0.1605. We'll compare both decompositions against the developers' actual splits. Positional proximity should help group methods with a shared responsibility, but may mislead when unrelated methods are adjacent or cohesive methods are scattered. If Bavota matches or exceeds ClassSplitter's mean, that would challenge whether M2's advantage transfers to these cases. An equal or larger gap would contradict our prediction of a smaller advantage." (three saves in the same minute; no later edits) |
| 2026-11-02 14:35 | 14:35 | Yanislav Iliev | L15 (Event A result) | Event A result: ClassSplitter 0.3839 vs Bavota 0.4386; prediction not supported (links `4df2d16`) |
| 2026-11-04 12:56–12:57 | same | Cian Gleeson | M15–P15 (design) | First design entries. O15: "…Our group did not implement the refactoring, and our final recommendation is pending." |
| 2026-11-05 09:16–09:18 | same | Cian Gleeson | M15–P15 | N15 alternatives: no change / remove the unused field / further Extract Class (e.g. AAPT packaging). O15: "We selected Option 2 … Further extraction was rejected because there was insufficient evidence that another split would improve cohesion or coupling." |
| 2026-11-05 15:54–15:56 | same | Cian Gleeson | M15–P15 | N15 Option 3: "Separate additional responsibilities such as packaging and resource decoding. Apktool's maintainers subsequently performed this in #3124, extracting AaptInvoker and ResourcesDecoder." O15: "…we no longer reject further extraction outright. The maintainers' subsequent extraction in #3124 demonstrates that further decomposition was feasible, although its quality impact requires separate evaluation." |
| 2026-11-09 15:25–15:26 | same | Cian Gleeson | P15 | Verification text reformatted (176 tests; fields, LOC, LCOM*, CBO, WMC) |
| 2026-11-12 20:02 | 20:02 | Yanislav Iliev | Q15 (Event B prediction) | "We predict that adding a feature to count cached framework APK files and report their total size will be simpler in the decomposed Apktool design. In the original design, this feature would add another responsibility to the already large AndrolibResources class. After the extraction, we expect the new feature to be contained within the Framework class without affecting unrelated code" (no later edits) |
| 2026-11-13 07:33–07:35 | same | Yanislav Iliev | R15 (Event B result) | Event B result, citing commit `660e4aa` |
| 2026-11-16 16:07 | same | Yanislav Iliev | R15 | GitHub link to the Event B README added |

## Comparison with the repository

| Prediction | Entered in the workbook (UTC) | Saved runs in the repository (UTC) | Commit containing the prediction and results |
| --- | --- | --- | --- |
| Event A (K15) | 2026-10-30 14:33 | 2026-11-02 12:35, a recovery replay of an original October execution whose time is not recorded (`results/event_a/primary/result.json`) | `2aae905`, 2026-11-02 13:52 |
| Event B (Q15) | 2026-11-12 20:02 | 2026-11-13 06:36 (JUnit XML `timestamp`, `extension/apktool/event_b/`) | `660e4aa`, 2026-11-13 07:31 |

Both prediction texts match the committed prediction files in substance. The Event B prediction was recorded before the test runs whose results are committed. The Event A prediction was recorded before the saved recovery replay; whether it preceded the original October execution is unverified. Neither history can exclude earlier unrecorded trials. See D10 in `docs/DEVIATIONS.md`.
