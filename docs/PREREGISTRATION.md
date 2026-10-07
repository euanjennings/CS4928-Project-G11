# M1 preregistration — Group G11

**Status: DRAFT — complete every `[FILL IN: ...]` before freezing.**

- Paper: Chen et al., *A Position-Aware Approach to Decomposing God Classes*, ASE 2024.
- Public artefact: https://github.com/ClassSplitter/ClassSplitter
- Date agreed by the group: [FILL IN: date]
- Group members: [FILL IN: names]
- Project-pack bounded target: [FILL IN: confirm the allowed target/sample]
- Week 5 specification: *Freeze the Reproduction Plan* (supplied by Sean).
- Coordinator status: [FILL IN: NOT YET / BLOCKED / READY, date and evidence].
- Planned freeze: after the coordinator confirms READY, the reviewed plan commit tagged `M1_PLAN`.

The Week 5 specification requires the exact RQs from the assigned project pack. That pack has not yet been supplied in this conversation or located in this repository. Earlier AI-generated RQs and experimental suggestions are provisional and must not replace assigned questions. All proposed choices below must be checked against the pack before freezing.

### Scope boundary

Use only the initial material released for this project. Do not inspect or analyse held-out or Change Event material before its release. New-project mining, position perturbations and embedding recomputation are not authorised by this template; include them only if the assigned pack requires or permits them at this stage.

Out of scope for M1: the full study, unreleased material, and unassigned experiments. M1 establishes the plan and feasibility; substantial reproduction begins after READY and the freeze.

## 1. Prior knowledge and scope

The repository notes in [DEVIATIONS.md](DEVIATIONS.md) describe earlier setup checks, but Sean reports that he has not personally run them. Their provenance and verification by the group remain [FILL IN: who ran the checks, when, and where the evidence is stored; or state that the claims are unverified]. We have seen these reported results while planning and will disclose that prior knowledge. They do not establish that this device can run the experiment.

The setup notes report overall MoJoFM near 0.496 for ClassSplitter and 0.334 for the baseline. These are claims in the existing notes, not results verified during this planning session. We will verify the paper's reported numbers and table before freezing.

Initial device checks on 2026-10-07 found an unprepared Python 3.14 environment. Sean then created `.venv312`, installed the dependencies, and successfully completed the three-case feasibility run recorded below. Java 23.0.2 was used rather than the README's JDK 21; record this version deviation and check any pack-specific requirement before formal execution.

Known deviations: D1 repairs the baseline's reference to `group.members` to use `group.units`. The baseline randomly assigns fields that no methods visit. Details and evidence are in [DEVIATIONS.md](DEVIATIONS.md).

## 2. RQ1 — bounded reproduction

**Assigned RQ1: [FILL IN: copy exactly from the project pack].**

- Source anchor: [FILL IN: section/table/figure/claim/experiment and page].
- Target statement: [FILL IN: exact original result and the output our bounded reproduction will produce].
- RQ1 out of scope: [FILL IN].

Earlier suggested interpretation, subject to the assigned RQ: compare ClassSplitter and the Bavota baseline against historical developer splits using MoJoFM.

### Cases and published target

- Source/version: upstream commit `459d796d3256de428330bff693f14cf442097338`, subject to the project pack's version requirement.
- Sample size/range: [FILL IN: exact bounded size/range from the pack or justified group decision]. The catalogue contains 133 cases; this does not automatically make all 133 the M1 sample.
- Runner catalogue: `upstream/Implementation/experienments/GodClassRefactorDictionary.csv`.
- Sample IDs: [FILL IN: exact runner indices, or an unambiguous rule producing them].
- Selection rule and exclusions: [FILL IN: rule, reasons and handling of excluded cases].
- Unit of analysis: one historical class-refactoring case. Cases from the same project may be related; this limits claims of independence.
- ID mapping: runner `index` is different from the catalogue's `last index` and the filename prefix. Record both IDs and the data filename with results.
- Paper table/page: [FILL IN: table number, page and source link].
- Published overall means: ClassSplitter [FILL IN: value]; Bavota [FILL IN: value].
- Paper score scale: [FILL IN: 0–1 or 0–100; convert consistently to 0–1].

### Method and measurements

Proposed procedure, to confirm against the assigned RQ: use `repro/run_repro.py`, the documented D1 fix and the shipped embedding cache. Preserve all original case records. Run sequentially because upstream writes shared temporary files.

Formal command: [FILL IN: exact command with selected IDs, seed and output path].

Seed configuration: [FILL IN: seed(s), repetitions and why they are needed for the assigned target]. Thirty seeds (0 through 29) were previously suggested as a randomness audit; they are not a requirement of the supplied Week 5 specification.

If repeating seeds, report a paper-compatible reproduction separately from the randomness audit and state which run/aggregation answers the original claim. For an across-seed paired analysis, average scores within each case and treat cases, rather than repeated runs, as the observations. Do not claim to reproduce a single-draw paper mean with a seed average without explaining the methodological difference.

- Primary metric: [FILL IN: metric matching the assigned target, e.g. overall MoJoFM].
- Secondary metrics: [FILL IN: include only relevant metrics, e.g. method-only/field-only MoJoFM and wins/ties/losses].
- Comparison/analysis: [FILL IN: the paper's analysis and any explicitly justified group audit]. A paired Wilcoxon test was suggested earlier but is not an automatic requirement. Any test must match the claim and sample; record treatment of zero differences and related cases.
- Ties: absolute score difference at most [FILL IN: numerical tolerance, e.g. 0.000001].
- If auditing upstream `ttest_ind`, report it separately and explain that both techniques were evaluated on the same cases.
- Randomness audit: report the range of baseline means across seeds and whether the overall advantage changes direction. This concerns the variation covered by the runner's seed, not a guarantee that every source of nondeterminism is controlled.
- Failed/invalid cases: record the error and retain the case in the failure log. Report achieved coverage. If missing or invalid evidence prevents the planned comparison, classify it as INCONCLUSIVE / BLOCKED rather than NOT REPRODUCED.

### Decision rules — agree before the formal runs

- Criterion for the original claim: [FILL IN: exact defensible rule matching the source result, including any numerical tolerance and its justification]. A universal tolerance or p-value is not appropriate for every target.
- REPRODUCED: a valid completed bounded run satisfies the criterion above.
- NOT REPRODUCED: a valid completed bounded run fails that criterion. Explain the observed difference; a nonsignificant test alone does not prove equivalence.
- INCONCLUSIVE / BLOCKED: the comparison cannot be interpreted because execution, data, environment or evidence is incomplete or invalid.
- If randomness sensitivity is part of the assigned RQ: [FILL IN: audit scope and quantitative instability criterion].

Expected result: [FILL IN: prediction tied to the assigned source claim]. Earlier notes suggest full-dataset means near 0.50 versus 0.33, but these do not define expected values for a smaller bounded sample. Verify the paper anchor and explain the prediction.

Evidence: per-case CSVs, environment records, seeds, failure logs, analysis scripts, summaries and the committed code state.

## 3. Assigned RQ2 and its target

**Assigned RQ2: [FILL IN: copy exactly from the project pack, if assigned].**

### Cases and target comparison

- Proposed sample: exactly **3 external historical Extract Class cases**, subject to coordinator approval.
- Sources: [FILL IN: repository names/URLs and fixed commit ranges], outside the authors' datasets.
- Case identifiers: record each repository, original class file, pre-refactoring commit and refactoring commit.
- Selection rule: select the first three eligible cases chronologically, breaking ties by repository URL and commit hash; exclude authors' dataset cases and cases without traceable member mappings.
- God-class eligibility: [FILL IN: specify the detection rule/tool and version].
- Unit of analysis: one historical Extract Class refactoring case; cases from the same project may be related.
- Reference decomposition: the developer's actual split, with original methods and fields mapped to their resulting classes.
- Source anchor: [FILL IN: paper section/table establishing the original ClassSplitter–Bavota advantage], plus the selected refactoring commits.
- Target comparison: compare ClassSplitter and Bavota's mean MoJoFM on the three external cases; there are no published external-case means to reproduce.
- Score scale: report MoJoFM consistently on the **0–1 scale**, where higher means closer agreement with the developer's split.
- Detailed case: choose the first selected case with passing, runnable baseline tests, before inspecting comparative scores.

- Inputs and preparation: [FILL IN].
- Procedure, tool/configuration and material parameters: [FILL IN].
- Metric and comparison with the original claim: [FILL IN].
- Expected result and source-based reason: [FILL IN].
- REPRODUCED criterion: [FILL IN].
- NOT REPRODUCED: valid completed evidence fails that criterion.
- INCONCLUSIVE / BLOCKED: incomplete or invalid evidence prevents interpretation.
- Evidence files/commands: [FILL IN].
- Out of scope at M1 and material reserved for later release: [FILL IN].

Do not replace the assigned RQ with the earlier new-project transfer or position-perturbation suggestions. If later transfer/design work is required, follow the pack's scope and release schedule and preserve pre-event predictions.

## 4. Completed feasibility check

Sean ran this command before M1 on 2026-10-07:

```powershell
.\.venv312\Scripts\python.exe repro/run_repro.py --ids 1 2 3 --out results/smoke_sean.csv
```

- Runner cases: 1, 2 and 3, all from initial published material.
- Seed: 2026 (runner default).
- Result: both techniques completed all three cases and wrote CSV/JSON outputs.
- Overall means observed: Bavota 0.4665; ClassSplitter 0.6790; ClassSplitter won 3/3 cases.
- Environment: Python 3.12.3; Java 23.0.2; package versions recorded in the JSON.
- Code commit recorded: `7fad2afe991d8fe721b5d50e4e91ce70afbe7da8`; working tree was dirty. This was a feasibility run, not a frozen formal reproduction.
- Evidence: `results/smoke_sean.csv` and `results/smoke_sean.json` (currently local; [FILL IN: durable evidence location accessible to the group/coordinator]).

These outcomes are prior observations and will be disclosed. They demonstrate feasibility for three cases, not full-study reproduction. Do not select the formal sample or change success criteria to favour these observed scores.

## 5. Coordinator checkpoint, freeze and amendments

Complete the blanks using the assigned pack and source study, obtain group review and enter concise evidence-linked M1 entries in Student Tracker.xlsx. Show the coordinator the exact RQs, source anchors, bounded sample, executable method, expected results, decision rules and feasibility evidence.

Only after the coordinator confirms READY, freeze the plan and tag the reviewed commit `M1_PLAN`. Then begin the bounded reproduction. READY, NOT YET and BLOCKED are formative checkpoint statuses.

After freezing, preserve the original plan. Add dated amendments explaining changes, their reasons and whether relevant results had already been inspected. Record predictions before executing each later Change Event analysis.

| Date | Amendment | Reason | Results already inspected? | Evidence |
| --- | --- | --- | --- | --- |
| [FILL IN if needed] | | | | |
