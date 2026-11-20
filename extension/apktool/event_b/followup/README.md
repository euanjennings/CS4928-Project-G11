# Event B — retrospective follow-up

This folder adds a **retrospective verification** of Event B. It was written on 2026-11-20, after the original Event B experiment (`660e4aa`), in response to review. The original [Event B README](../README.md), patches, tests and JUnit results are unchanged and remain the reported experiment.

## Why

1. The original comparison used the developers' historical before and after commits. It did not test our own M4 decision, the field cleanup.
2. `run_ck_pair.py` cannot measure Event B: it only rebuilds `40d427e5` and applies the cleanup.
3. The original patch lacked the `dir == null` check used by the neighbouring `listFrameworkDirectory()`, and the four tests did not cover a failure path.

## What is here

| File | Purpose |
| --- | --- |
| `run_event_b_followup.py` | Harness. Refuses to run unless it and its inputs are committed. |
| `framework-after-v2.patch`, `androlibresources-before-v2.patch` | Same feature as the originals, adding the `dir == null` check. Both add an identical method body. |
| `FrameworkCacheSummaryTest.java`, `AndrolibResourcesCacheSummaryTest.java` | The four original tests plus `rejectsFramePathThatIsAFile`. |

The harness measures six states: each of `9c495cae` (historical before), `40d427e5` (pre-M4) and `40d427e5` + `cleanup.patch` (our M4 state), with and without the feature. For each, it runs CK on all tracked Java files plus the added test (options `false 0 false`, as in D5) and the **full** Gradle test suite with `--rerun-tasks`. New tests are counted separately from existing regression tests.

| Comparison | States | Question it answers |
| --- | --- | --- |
| (a) | `pre_m4_feature` vs `m4_feature` | Did **our** M4 cleanup make the feature easier to add? |
| (b) | `hist_before_feature` vs `pre_m4_feature` | Did the **developers'** Framework extraction make it easier? |

`Framework.java` is byte-identical in both (a) states, because the cleanup only changes `AndrolibResources`. Comparison (a) is therefore expected to show no difference.

## Run

Requirements: Java 17 on `PATH` (the Apktool Gradle 8.1.1 wrapper does not run on Java 23), a full Apktool clone with `git config core.longpaths true`, and the same CK JAR used for D5.

```powershell
python extension/apktool/event_b/followup/run_event_b_followup.py `
    --apktool-repo C:\src\Apktool --ck-jar C:\tools\ck.jar --work C:\t
```

Output goes to a new `run_<UTC timestamp>/` folder here. It contains `manifest.json` (G11 commit, input hashes, CK JAR hash, Java and Gradle versions, commands, test totals and CK rows per state), per-state CK CSVs, JUnit XML, `testcases.json` and logs. Commit the whole run folder unchanged, then add the interpretation **below** the original text in [../README.md](../README.md), headed as a retrospective follow-up.
