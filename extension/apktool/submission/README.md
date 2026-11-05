# Manual submission review - 5 November 2026

Use [STAGE_PATHS.txt](STAGE_PATHS.txt) as the exact proposed allowlist. Cian has staged these 95 files for review. [EXCLUDE_PATHS.tsv](EXCLUDE_PATHS.tsv) records files kept out of the submission and the reason for each. [CHECKS.json](CHECKS.json) records verification; [FILE_MANIFEST.json](FILE_MANIFEST.json) hashes the approved working-tree payload. Existing RQ1/upstream files already committed are dependencies, not new additions.

## Essential submission content

| Files | Why included |
| --- | --- |
| `design/APKTOOL_CASE_STUDY.md` | Exact frozen RQ2, independent decision, results and limits |
| `docs/PREREGISTRATION.md`, `docs/DEVIATIONS.md` | Retrospective amendment and disclosed departures; frozen plan retained |
| `extension/apktool/{VALIDATION_REPORT,GROUND_TRUTH_SENSITIVITY,INDEPENDENT_CLEANUP_EXPERIMENT}.md` | Validation failure, explicit labels and matched independent experiment |
| `extension/apktool/publication/` allowlisted files | Input/script lineage, raw diagnostic tables, relative-path CK class/method data, all test results, run parameters, source/patches, reproducibility wrappers and redaction provenance |
| `extension/apktool/results*/` comparison JSONs and matching caches | Exact versioned partitions and similarity inputs needed to verify saved exploratory scores |
| Existing root Apktool candidate/truth CSVs and `run_apktool.py` | Original runner provenance and dependency of the safe wrapper |
| `.gitattributes` | Preserve checksummed Apktool bytes across staging/checkout |
| `extension/apktool/submission/` allowlisted files | Explicit inclusion/exclusion lists, transformation code, audit and checksums |

The publication package is the only handover-derived evidence tree to submit. The original `handover_20261104/` was moved to the sibling `CS4928_Private_Archive_20261105/extension/apktool/` directory; it remains available locally and must not be submitted. Published derivatives are explicitly identified; no numeric metric or testcase outcome has been changed.

## Exclude from this submission

- `.github/workflows/apktool.yml`: moved to the sibling private archive while untracked and unstaged. Keep it excluded.
- `CODEX_HANDOVER_CS4928_G11_P04_2026-11-04.md`: moved to the sibling private archive; contains local instructions, machine layout and personal paths.
- Original `extension/apktool/handover_20261104/`: now in the sibling private archive. It contains private paths in CK CSVs/manifests and worktree inventories; hostnames and temporary paths inside XML ZIP console streams; UTF-16 build logs; stale Git snapshots, duplicate rerun diagnostics, older case-study draft and tracker extract. Publish only the curated derivatives.
- Virtual environments, `__pycache__`, compiled Python files, temporary CK/Maven copies, build caches, complete review ZIPs and the 20 MB CK binary. Keep these locally. The already committed upstream MoJo classes are required evaluator dependencies and must remain.
- `docs/AI_USE.md`: no change is included in this submission allowlist. The existing tracked disclosure remains part of repository history; only Cian updates it.

The machine-specific data found included the local Windows project hierarchy, a user profile/temporary-directory prefix, local Java/Maven locations and XML hostnames. The privacy check decodes UTF-16 logs and opens ZIP members; it does not merely scan filenames or UTF-8 text. Legitimate author names and source-code license attributions remain.

## Workflow decision

**Exclude the current workflow.** Inspection shows `push` triggers for `cian/week9-design`, plus `workflow_dispatch`. It installs the scientific dependency stack, executes the original fixed-v2 runner, overwrites `extension/apktool/results/` in the CI checkout and uploads that directory even after a failed run (`if: always()`). That is an exploratory algorithm rerun, not validation of the final v4 evidence or a Gradle test of the cleanup. Existing outputs could be uploaded after an early failure, making artifact interpretation ambiguous.

Changing only the trigger to manual-only would remove automatic runs but would leave those provenance/output issues. If CI is added later, prefer a separate manual evidence-verification workflow using `publication/verify_evidence.py`, a fresh output directory and explicit version/provenance checks. Do not publish the present workflow merely by removing `push`. No workflow file has been edited and no Actions run has been started.

## Verification scope

The audit models `HEAD` plus exactly the allowlisted working-tree files, excluding the new workflow and private archive. Relative Markdown links in authored project documentation are checked against that projected tree, not just the live filesystem; anchors are checked where present. Upstream-import documentation is reported separately, with pre-existing limitations distinguished. External HTTP links are unchanged and are not live availability guarantees.

The published evidence verifier was executed successfully: 176 tests, zero failures/errors, one skip on each side; zero identity/outcome differences; exact validation counts and fixed-partition scores. A [portable check](PORTABLE_CHECK.json) repeated it using only approved files and required HEAD-tracked evaluator/reference files in an isolated directory with no private handover tree; all five saved scientific outputs matched byte-for-byte. Every CK CSV column except `file` is compared with its original. XML comparisons retain all result-bearing nodes/attributes after removing only host/environment/console metadata. Original evidence, Git index and AI-use file hashes are checked separately. `.gitattributes` is verified using `git check-attr`; no temporary Git index or staging operation is used.

## Manual Git commands

Run from the repository root after reviewing the list. These commands are instructions for Cian only; they were not executed by the assistant. The workflow unstage command is unnecessary if it is already absent from the index.

```powershell
# Refuse to proceed if any other staged path is outside the reviewed allowlist.
$approvedPaths = @(Get-Content -LiteralPath extension/apktool/submission/STAGE_PATHS.txt)
$unexpectedPaths = @(git diff --cached --name-only | Where-Object { $_ -notin $approvedPaths })
if ($unexpectedPaths.Count -gt 0) {
    $unexpectedPaths
    throw 'Review these unexpected staged paths before continuing.'
}

# Stage only the exact listed files. Never use git add . or git add -A.
git --literal-pathspecs add --pathspec-from-file=extension/apktool/submission/STAGE_PATHS.txt
git diff --cached --check
git diff --cached --stat
git diff --cached --name-only
git diff --cached -- .gitattributes design/APKTOOL_CASE_STUDY.md docs/PREREGISTRATION.md docs/DEVIATIONS.md
```

Review the staged content before choosing a commit or push. No commit/push command is necessary to complete the requested staging preparation.
