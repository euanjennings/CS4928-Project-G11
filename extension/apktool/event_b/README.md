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
