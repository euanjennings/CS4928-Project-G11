"""Event B retrospective follow-up: build, test and CK-measure six Apktool source states.

This is a RETROSPECTIVE verification added after the original Event B experiment
(commit 660e4aa). It does not replace that experiment, its README or its evidence.

States (Apktool commit + patches applied in order + test file added):

    hist_before          9c495cae
    hist_before_feature  9c495cae + androlibresources-before-v2.patch + AndrolibResourcesCacheSummaryTest
    pre_m4               40d427e5
    pre_m4_feature       40d427e5 + framework-after-v2.patch + FrameworkCacheSummaryTest
    m4                   40d427e5 + cleanup.patch
    m4_feature           40d427e5 + cleanup.patch + framework-after-v2.patch + FrameworkCacheSummaryTest

Comparison (a), our M4 decision:        pre_m4(_feature)      vs m4(_feature)
Comparison (b), developers' extraction: hist_before(_feature) vs pre_m4(_feature)

For each state the script makes a detached `git worktree` of the Apktool clone, applies
the patches with `git apply`, copies the test file, runs CK on every tracked .java file
plus the added test (options `false 0 false`, as in D5), then runs the FULL Gradle test
suite with `--rerun-tasks`. JUnit XML, CK CSVs, logs, source hashes and the environment
are written to a new output directory. Worktrees are removed afterwards; the clone's
checked-out files are never modified.

The harness refuses to run unless this script and its inputs are committed and unmodified
in the G11 repository, so every run is tied to a committed state.

Usage (Windows PowerShell, Java 17 on PATH):

    python extension/apktool/event_b/followup/run_event_b_followup.py `
        --apktool-repo C:\\src\\Apktool --ck-jar C:\\tools\\ck.jar --work C:\\t

Use a short --work path on Windows to avoid long-path failures, and set
`git config core.longpaths true` in the Apktool clone first.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
G11 = HERE.parents[3]
CLEANUP = G11 / "extension/apktool/publication/cleanup.patch"
BEFORE = "9c495cae295dbff3aab378da4a889d8b926f081a"
AFTER = "40d427e5bdf5c204c58022cef3b369f34e19b043"
TEST_DIR = "brut.apktool/apktool-lib/src/test/java/brut/androlib/res"
RESULTS_DIR = "brut.apktool/apktool-lib/build/test-results/test"
GRADLE_TASK = ":brut.apktool:apktool-lib:test"
CK_ARGS = ["false", "0", "false"]
CLASSES = ["brut.androlib.res.AndrolibResources", "brut.androlib.res.Framework"]
CK_COLUMNS = ["totalMethodsQty", "totalFieldsQty", "loc", "cbo", "wmc", "lcom*"]

FW_PATCH = HERE / "framework-after-v2.patch"
AR_PATCH = HERE / "androlibresources-before-v2.patch"
FW_TEST = HERE / "FrameworkCacheSummaryTest.java"
AR_TEST = HERE / "AndrolibResourcesCacheSummaryTest.java"

STATES = {
    "hist_before":         (BEFORE, [], None),
    "hist_before_feature": (BEFORE, [AR_PATCH], AR_TEST),
    "pre_m4":              (AFTER, [], None),
    "pre_m4_feature":      (AFTER, [FW_PATCH], FW_TEST),
    "m4":                  (AFTER, [CLEANUP], None),
    "m4_feature":          (AFTER, [CLEANUP, FW_PATCH], FW_TEST),
}
NEW_TEST_CLASSES = {"brut.androlib.res.FrameworkCacheSummaryTest",
                    "brut.androlib.res.AndrolibResourcesCacheSummaryTest"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd, cwd=None, log=None, check=True):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if log:
        Path(log).write_text(f"$ {' '.join(map(str, cmd))}\n{proc.stdout}\n{proc.stderr}",
                             encoding="utf-8")
    if check and proc.returncode:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(map(str, cmd))}\n"
                           f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return proc


def git(*args, cwd=G11, check=True):
    return run(["git", *args], cwd=cwd, check=check).stdout.strip()


def require_committed():
    inputs = [Path(__file__).resolve(), CLEANUP, FW_PATCH, AR_PATCH, FW_TEST, AR_TEST]
    rel = [p.relative_to(G11).as_posix() for p in inputs]
    for r in rel:
        if run(["git", "ls-files", "--error-unmatch", r], cwd=G11, check=False).returncode:
            sys.exit(f"Not committed: {r}. Commit the harness and its inputs before running.")
    dirty = git("status", "--porcelain", "--", *rel)
    if dirty:
        sys.exit(f"Uncommitted changes to harness inputs:\n{dirty}")
    return {r: sha(G11 / r) for r in rel}


def gradle_wrapper(worktree):
    return str(Path(worktree) / "gradlew.bat") if os.name == "nt" else "./gradlew"


def environment(sample_worktree):
    java = run(["java", "-version"], check=False)
    wrapper = gradle_wrapper(sample_worktree)
    gradle = run([wrapper, "--version", "--no-daemon"], cwd=sample_worktree, check=False)
    return {
        "java_version": (java.stderr or java.stdout).strip(),
        "gradle_version": gradle.stdout.strip(),
        "python": sys.version,
        "platform": platform.platform(),
    }


def ck_rows(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = {r["class"]: r for r in csv.DictReader(f)}
    picked = {}
    for cls in CLASSES:
        if cls in rows:
            picked[cls] = {c: rows[cls].get(c) for c in CK_COLUMNS}
    return len(rows), picked


def summarise_tests(xml_dir):
    cases = {}
    for xml in sorted(Path(xml_dir).glob("TEST-*.xml")):
        suite = ET.parse(xml).getroot()
        for tc in suite.iter("testcase"):
            if tc.find("failure") is not None:
                outcome = "failed"
            elif tc.find("error") is not None:
                outcome = "error"
            elif tc.find("skipped") is not None:
                outcome = "skipped"
            else:
                outcome = "passed"
            cases[f"{tc.get('classname')}#{tc.get('name')}"] = outcome

    def count(keys):
        totals = {"tests": 0, "passed": 0, "failed": 0, "error": 0, "skipped": 0}
        for k in keys:
            totals["tests"] += 1
            totals[cases[k]] += 1
        return totals

    new = [k for k in cases if k.split("#")[0] in NEW_TEST_CLASSES]
    existing = [k for k in cases if k not in new]
    return cases, {"existing_tests": count(existing), "new_tests": count(new)}


def measure_state(name, repo, ck_jar, work, out, skip_tests, skip_ck):
    commit, patches, test_file = STATES[name]
    wt = work / name
    dest = out / name
    dest.mkdir()
    run(["git", "-C", str(repo), "worktree", "add", "--detach", str(wt), commit],
        log=dest / "worktree.log")
    record = {"apktool_commit": commit, "patches": [], "added_test": None}
    try:
        for patch in patches:
            run(["git", "-C", str(wt), "apply", "--check", str(patch)])
            run(["git", "-C", str(wt), "apply", str(patch)])
            record["patches"].append({"file": patch.relative_to(G11).as_posix(), "sha256": sha(patch)})
        if test_file:
            shutil.copy2(test_file, wt / TEST_DIR / test_file.name)
            record["added_test"] = {"file": test_file.relative_to(G11).as_posix(), "sha256": sha(test_file)}

        status = run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=wt).stdout
        changed = [entry[3:] for entry in status.split("\0") if entry]
        record["changed_source_sha256"] = {rel: sha(wt / rel) for rel in changed}
        expected = len(patches) + (1 if test_file else 0)
        if len(changed) < (1 if test_file else 0) or (patches and not changed):
            raise RuntimeError(f"{name}: expected changed files after {expected} input(s), got {changed}")

        if not skip_ck:
            java_files = git("ls-files", "--cached", "--others", "--exclude-standard", "*.java",
                             cwd=wt).splitlines()
            src = work / f"{name}_cksrc"
            for rel in java_files:
                (src / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(wt / rel, src / rel)
            ck_out = dest / "ck"
            ck_out.mkdir()
            cmd = ["java", "-jar", str(ck_jar), str(src), *CK_ARGS, str(ck_out)]
            proc = run(cmd, log=ck_out / "run.log", check=False)
            record["ck"] = {"command": [Path(c).name if c == str(ck_jar) else c for c in cmd],
                            "java_files": len(java_files), "exit_code": proc.returncode}
            if proc.returncode == 0:
                n, picked = ck_rows(ck_out / "class.csv")
                record["ck"].update(class_rows=n, classes=picked,
                                    class_csv_sha256=sha(ck_out / "class.csv"))
            shutil.rmtree(src, ignore_errors=True)

        if not skip_tests:
            cmd = [gradle_wrapper(wt), GRADLE_TASK, "--rerun-tasks", "--no-daemon", "--console=plain"]
            proc = run(cmd, cwd=wt, log=dest / "gradle.log", check=False)
            xml_out = dest / "junit"
            xml_out.mkdir()
            for xml in (wt / RESULTS_DIR).glob("TEST-*.xml"):
                shutil.copy2(xml, xml_out / xml.name)
            cases, totals = summarise_tests(xml_out)
            (dest / "testcases.json").write_text(json.dumps(cases, indent=2, sort_keys=True),
                                                 encoding="utf-8")
            record["tests"] = {"command": cmd, "exit_code": proc.returncode, **totals}
    finally:
        run(["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)], check=False)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--apktool-repo", type=Path, required=True)
    p.add_argument("--ck-jar", type=Path, required=True)
    p.add_argument("--work", type=Path, required=True, help="short scratch directory, e.g. C:\\t")
    p.add_argument("--out", type=Path, help="new output directory (default: a dated folder next to this script)")
    p.add_argument("--states", nargs="+", choices=list(STATES), default=list(STATES))
    p.add_argument("--skip-tests", action="store_true")
    p.add_argument("--skip-ck", action="store_true")
    a = p.parse_args()

    inputs = require_committed()
    started = datetime.now(timezone.utc)
    out = (a.out or HERE / f"run_{started.strftime('%Y%m%dT%H%M%SZ')}").resolve()
    out.mkdir(parents=True, exist_ok=False)
    work = a.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    repo, ck_jar = a.apktool_repo.resolve(), a.ck_jar.resolve()
    for c in (BEFORE, AFTER):
        git("cat-file", "-e", f"{c}^{{commit}}", cwd=repo)

    manifest = {
        "purpose": "Retrospective Event B follow-up; not the original Event B experiment (660e4aa).",
        "started_utc": started.isoformat(),
        "g11_commit": git("rev-parse", "HEAD"),
        "g11_harness_inputs_sha256": inputs,
        "ck_jar_sha256": sha(ck_jar),
        "ck_options": CK_ARGS,
        "states": {},
    }
    env_wt = work / "_env"
    run(["git", "-C", str(repo), "worktree", "add", "--detach", str(env_wt), AFTER])
    try:
        manifest["environment"] = environment(env_wt)
    finally:
        run(["git", "-C", str(repo), "worktree", "remove", "--force", str(env_wt)], check=False)

    for name in a.states:
        print(f"[{datetime.now(timezone.utc):%H:%M:%S}] {name} ...", flush=True)
        manifest["states"][name] = measure_state(name, repo, ck_jar, work, out, a.skip_tests, a.skip_ck)
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"\nWritten to {out}\n")
    print(f"{'state':22} {'existing tests (pass/fail/err/skip)':38} {'new tests':16} AndrolibResources / Framework (methods, LOC, CBO, WMC, LCOM*)")
    for name, r in manifest["states"].items():
        t = r.get("tests", {})
        ex, nw = t.get("existing_tests", {}), t.get("new_tests", {})
        ext = f"{ex.get('tests','-')}: {ex.get('passed','-')}/{ex.get('failed','-')}/{ex.get('error','-')}/{ex.get('skipped','-')}"
        nwt = f"{nw.get('tests','-')}: {nw.get('passed','-')}/{nw.get('failed','-')}"
        ck = r.get("ck", {}).get("classes", {})
        cks = " | ".join(
            ",".join(str(ck[c].get(k)) for k in ["totalMethodsQty", "loc", "cbo", "wmc", "lcom*"])
            for c in CLASSES if c in ck)
        print(f"{name:22} {ext:38} {nwt:16} {cks}")


if __name__ == "__main__":
    main()
