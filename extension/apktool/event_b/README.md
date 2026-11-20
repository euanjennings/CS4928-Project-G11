# Event B - Framework Cache Statistics

## 1. Background

For Event B, we used the historical Apktool extraction examined in our Week 9 M4 work. In that refactoring, framework-related methods were moved from the large `AndrolibResources` class into a separate `Framework` class.

We compared two historical Apktool commits:

- **Before extraction:** `9c495cae` – `AndrolibResources`
- **After extraction:** `40d427e5` – `Framework`

Our frozen M4 baseline in the G11 repository is `PRE_EVENT_B` (`b8124f8`).

## 2. Prediction

We wanted to add a feature that counts cached framework APK files and reports their total size in bytes.

We predicted that this would be simpler in the decomposed design because the feature could be added directly to `Framework`, without changing unrelated code in `AndrolibResources`.

## 3. Implementation

We first checked the historical Java source. Both versions already had a `listFrameworkDirectory()` method that lists framework APK filenames, but neither calculated the number of files or their combined size.

We added a method called `getFrameworkCacheSummary()` to both versions:

- In the original version, we added it to `AndrolibResources.java`.
- In the extracted version, we added it to `Framework.java`.

The method counts regular `.apk` files, adds their sizes in bytes, and ignores other files and directories.

We used the same logic in both versions so we could compare the results.

## 4. Testing and Results

We wrote four JUnit tests covering an empty directory, two APK files, a non-APK file, and a directory ending in `.apk`.

**Before extraction (9c495cae):**

Modified class: AndrolibResources.java
Production files changed: 1
Lines added: 21
JUnit tests: 4 passed, 0 failed, 0 skipped
Build: Successful

**After extraction (40d427e5):**

Modified class: Framework.java
Production files changed: 1
Lines added: 18
JUnit tests: 4 passed, 0 failed, 0 skipped
Build: Successful

Both implementations worked as expected. The main difference was where the new responsibility was added, rather than the number of files changed.

## 5. Design Decision

We considered two options for the extracted design:

1. **Add the method to the existing `Framework` class.** This keeps framework-related functionality together and avoids creating another class. The downside is that `Framework` becomes slightly larger.
2. **Create a separate class for cache statistics.** This would separate the new feature further, but seemed unnecessary for such a small change.

We chose the first option because `Framework` already handles framework-directory operations. No further extraction was needed.

## 6. Reproduction

The original Apktool source is available at https://github.com/iBotPeaches/Apktool.

To reproduce our tests:

1. Check out the two historical commits listed above in separate directories. On Windows, enable `git config core.longpaths true` before checkout.
2. Apply the relevant patch from this folder at the root of the matching Apktool checkout:

   - `androlibresources-before.patch`
   - `framework-after.patch`

3. Copy the matching JUnit test file into `brut.apktool/apktool-lib/src/test/java/brut/androlib/res/`.
4. Using Java 17, run the corresponding test command from the Apktool repository root.

**Before extraction:**

```bash
./gradlew :brut.apktool:apktool-lib:test \
  --tests brut.androlib.res.AndrolibResourcesCacheSummaryTest \
  --no-daemon --console=plain
```

**After extraction:**

```bash
./gradlew :brut.apktool:apktool-lib:test \
  --tests brut.androlib.res.FrameworkCacheSummaryTest \
  --no-daemon --console=plain
```

The test source files, patches and JUnit XML results are saved in this folder. Both recorded runs passed all four tests.

## 7. Conclusion

Our results partly support the Week 9 decision to keep the extracted `Framework` class.

Both versions needed only one production file change, so we cannot claim that extraction reduced the amount of work. However, in the decomposed design, the new feature could be added directly to `Framework` rather than making the already large `AndrolibResources` class larger.

We therefore kept the existing design and accepted a small increase in the size of `Framework` instead of introducing another class.

Our tests covered only this feature, not the full Apktool test suite. We also did not test performance or measure changes in coupling. The method was tested directly and was not connected to Apktool's command-line interface.

---

## 8. Retrospective follow-up (added 2026-11-20, after the results above)

Everything above this line is the original Event B report from `660e4aa` (13 Nov 2026) and is unchanged. This section was added on 2026-11-20 in response to review. It is a retrospective verification, not a new prediction.

### Why

1. Sections 1–7 compare the developers' historical before and after commits. They did not test our own M4 decision, the field cleanup in [`cleanup.patch`](../publication/cleanup.patch).
2. The original patches were not formatted identically, and the `Framework` version lacked the `dir == null` check used by the neighbouring `listFrameworkDirectory()`. The "21 vs 18 lines added" in section 4 therefore reflects formatting, not design.
3. Only the four new tests were run, and coupling was not measured.

### Method

The [harness](followup/run_event_b_followup.py) was committed in `db385e6` before it was run, and the script refuses to run on uncommitted inputs. It builds six Apktool states. For each, it runs CK on all tracked Java files with the D5 options (`false 0 false`) and the **full** `apktool-lib` Gradle test suite with `--rerun-tasks`.

| State | Apktool source |
| --- | --- |
| `hist_before` / `hist_before_feature` | `9c495cae`, without / with [`androlibresources-before-v2.patch`](followup/androlibresources-before-v2.patch) |
| `pre_m4` / `pre_m4_feature` | `40d427e5`, without / with [`framework-after-v2.patch`](followup/framework-after-v2.patch) |
| `m4` / `m4_feature` | `40d427e5` + `cleanup.patch`, without / with `framework-after-v2.patch` |

Both v2 patches add an identical method body. The [new tests](followup/FrameworkCacheSummaryTest.java) are the four original tests plus `rejectsFramePathThatIsAFile`.

- **Comparison (a), our M4 decision:** `pre_m4_feature` vs `m4_feature`.
- **Comparison (b), the developers' extraction:** `hist_before_feature` vs `pre_m4_feature`.

### Run and evidence

- Run [`run_20261120T175326Z`](followup/run_20261120T175326Z/manifest.json), 2026-11-20 17:53–18:10 UTC. Java 17.0.20.1, with Gradle 8.1.1 also running on JVM 17.0.20.1. CK was rebuilt at `8a1ef91` (JAR SHA-256 `542dd253…`; see [D9](../../../docs/DEVIATIONS.md)).
- The commit, input hashes, environment, commands and per-state results are in [`manifest.json`](followup/run_20261120T175326Z/manifest.json). Per-state test outcomes, CK class tables and Gradle logs are in the state folders.
- The other 273 raw files (JUnit XML, CK method tables, tool logs) are in [`raw_outputs.zip`](followup/run_20261120T175326Z/raw_outputs.zip), SHA-256 `7cabfcb0b367d36a2c7c42b58b11ba509c115bf95997fecfc0b98fbf05b3514a`.
- **CK check:** `pre_m4` and `m4` reproduce the D5 class tables exactly, with 166 rows × 51 columns each and 0 differences. The follow-up numbers are therefore comparable with D5.
- A first attempt on the same day stopped on the Windows 260-character path limit before writing any manifest. None of its output is used (see D9).

### Results

Tests: every state ran 176 existing tests with 175 passed, 1 skipped, 0 failed and 0 errors, and the testcase identities and outcomes were identical across all six states. In each `_feature` state, all 5 new tests passed.

CK (methods / fields / LOC / CBO / WMC / LCOM*):

| State | `AndrolibResources` | `Framework` |
| --- | --- | --- |
| `hist_before` | 45 / 15 / 784 / 38 / 194 / 0.908 | – |
| `hist_before_feature` | 46 / 15 / 803 / 38 / 200 / 0.910 | – |
| `pre_m4` | 35 / 15 / 613 / 35 / 150 / 0.897 | 11 / 3 / 180 / 10 / 45 / 0.727 |
| `pre_m4_feature` | 35 / 15 / 613 / 35 / 150 / 0.897 | 12 / 3 / 199 / 10 / 51 / 0.750 |
| `m4` | 35 / 14 / 612 / 35 / 150 / 0.890 | 11 / 3 / 180 / 10 / 45 / 0.727 |
| `m4_feature` | 35 / 14 / 612 / 35 / 150 / 0.890 | 12 / 3 / 199 / 10 / 51 / 0.750 |

The new method itself has 19 LOC, WMC 6 and CBO 2 in every version. It uses no fields directly and reaches the directory through `getFrameworkDirectory()`.

### Interpretation

- **(a) Our M4 cleanup made no difference to this feature.** `Framework.java` is byte-identical with and without the cleanup, and the feature adds the same +1 method, +19 LOC and +6 WMC in both. The only `AndrolibResources` difference (−1 field, −1 LOC, LCOM* 0.897 → 0.890) is the cleanup itself, as already reported in D5. This result does not count for or against the cleanup.
- **(b) The developers' extraction changed where the feature lands, not how big it is.** The change is the same size in both versions: +1 method, +19 LOC, +6 WMC, no change in CBO, and one production file plus one test file. Before the extraction, the method joins a 784-LOC class with LCOM* 0.908, and LCOM* rises slightly to 0.910. After it, the method joins a 180-LOC class whose responsibility is the framework directory. The feature's only collaborator, `getFrameworkDirectory()`, belongs to that class. `Framework`'s LCOM* also rises slightly (0.727 → 0.750), because the method uses no fields directly, so the metrics do not show a cohesion gain from the placement.
- **The null check:** `getFrameworkDirectory()` either returns a directory or throws, so `dir == null` can never be true. The check is defensive code, kept to mirror `listFrameworkDirectory()`. It is identical in both versions and does not affect the comparison. `rejectsFramePathThatIsAFile` confirms that a bad framework path makes `getFrameworkCacheSummary()` fail cleanly through Apktool's existing "path is a file" check, not through our branch. The "cannot list the directory" branch is also untested, because it is hard to trigger reliably on every operating system.

### Verdict on the Week 9 decision

**Partly supported, unchanged from section 7.** With matched patches and the full test suite, both designs needed the same amount of change and kept all existing test outcomes. The extraction's benefit here is placement: the feature sits next to the method it depends on, in a smaller class, instead of enlarging `AndrolibResources`. Our own M4 cleanup had no measurable effect on this feature.

**What this does not show:** It covers one small feature in one environment (Windows, Java 17). CK measures structure, not effort or readability, and LCOM* is field-based. The feature is still not connected to Apktool's command-line interface, and performance was not tested.
