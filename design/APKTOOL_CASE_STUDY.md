# Apktool Design Case Study — Working Draft

## 1. Research Question

Research Question 2: Can ClassSplitter's findings help us
make design decisions about real Java projects?

## 2. What We Looked At

Project: Apktool

Original class: AndrolibResources

New class: Framework

Apktool's developers moved framework-related code out of
AndrolibResources and into a separate Framework class.

This is called an Extract Class refactoring.

## 3. The Design Problem

AndrolibResources was responsible for several different jobs.

Separating framework management could make the code easier
to understand, maintain and test.

## 4. Options Considered

1. Do nothing and keep the original class.
2. Extract framework-related code into a new class.
3. Make smaller changes within the original class.

## 5. Design Decision

The original Apktool developers chose Option 2.

We are examining that decision to see whether it was
reasonable. Our group's final recommendation is not yet confirmed.

## 6. Tests and Results

### What We Tested

We downloaded two versions of Apktool:

- Before refactoring: `9c495cae`
- After refactoring: `40d427e5`

The second version contains the Extract Class change.

### Test Command

We ran this command on both versions:

    .\gradlew.bat :brut.apktool:apktool-lib:test --no-daemon --console=plain

We used Java 17 and Gradle 8.1.1.

### Test Results

| Version | Result | Build time |
| --- | --- | --- |
| Before refactoring | BUILD SUCCESSFUL | 1m 45s |
| After refactoring | BUILD SUCCESSFUL | 1m 26s |

Both versions passed the selected library tests.

The second run reused previously completed build tasks,
so the build times cannot be used to compare performance.

### Code Changes

We also ran:

    git diff --stat 9c495cae 40d427e5

Results:

- 6 files changed.
- 261 lines added.
- 224 lines removed.
- A new class called `Framework.java` was created.
- `AndrolibResources.java` had much of its framework-related
  code removed.

### What These Results Mean

The selected tests passed before and after the refactoring.

This suggests the change did not introduce failures
detected by those tests.

However, passing tests does not prove the design improved.

We have not yet measured cohesion or coupling, or compared
ClassSplitter against Bavota on this example.

## 7. Work Still to Do

- Confirm this case with the group.
- Measure cohesion and coupling.
- Determine whether ClassSplitter and Bavota need to be
  run on this case.

## 8. Code Versions

Before: 9c495cae
After: 40d427e5