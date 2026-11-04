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

We downloaded the code before and after the change.

We ran the same Gradle library tests on both versions.

Before: BUILD SUCCESSFUL
After: BUILD SUCCESSFUL

This shows the selected tests passed in both versions.
It does not prove the design is better.

## 7. Work Still to Do

- Confirm this case with the group.
- Measure cohesion and coupling.
- Determine whether ClassSplitter and Bavota need to be
  run on this case.

## 8. Code Versions

Before: 9c495cae
After: 40d427e5