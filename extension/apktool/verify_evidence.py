"""Check the compact Apktool evidence; optionally compare the private originals.

Usage: python extension/apktool/verify_evidence.py [--archive PATH]
PATH is the new private archive root, not the earlier 20261105 archive.
No files are written.
"""

import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_hash_matches(path, expected):
    if sha(path) == expected:
        return True
    if path != HERE / "apktool_ground_truth.csv":
        return False
    data = path.read_bytes()
    # Reconstruct historical CRLF bytes only from the LF-only ground truth.
    return b"\r" not in data and hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest() == expected


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def test_results(path):
    totals = Counter()
    outcomes = Counter()
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".xml")]
        for name in names:
            suite = ET.fromstring(archive.read(name))
            for key in ("tests", "failures", "errors", "skipped"):
                totals[key] += int(suite.get(key, 0))
            for case in suite.iter("testcase"):
                outcome = next((key for key in ("failure", "error", "skipped") if case.find(key) is not None), "passed")
                outcomes[(case.get("classname"), case.get("name"), outcome)] += 1
    totals["xml_files"] = len(names)
    return dict(totals), outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="compare original files in the private archive")
    args = parser.parse_args()
    data = json.loads((HERE / "RESULTS_SUMMARY.json").read_text(encoding="utf-8"))
    truth = csv_rows(HERE / "apktool_ground_truth.csv")
    check(len(truth) == 60, "ground truth member count")
    check(sum(row["removed"] == "True" for row in truth) == 10, "declaration-only moved-method count")
    check(sum(row["name"] == "mFrameworkDirectory" and row["type"] == "Field" for row in truth) == 1, "ambiguous field")
    check(data["method_mapping"]["before_ordinary_methods"] == 43, "before method count")
    check(len(data["method_mapping"]["moved_before_signatures"]) == 10, "moved method count")

    ar = "brut.androlib.res.AndrolibResources"
    metrics = data["metrics"]
    before = metrics["matched_pristine_after"][ar]
    after = metrics["matched_cleanup_after"][ar]
    expected_changes = {"totalFieldsQty": ("15", "14"), "privateFieldsQty": ("14", "13"),
                        "loc": ("613", "612"), "lcom*": ("0.8971428", "0.8897959"),
                        "assignmentsQty": ("99", "98"), "variablesQty": ("73", "72")}
    for key in set(before) | set(after):
        if key in expected_changes:
            check((before[key], after[key]) == expected_changes[key], f"metric change {key}")
        else:
            check(before[key] == after[key], f"unexpected metric change {key}")
    check(metrics["matched_pristine_after"]["brut.androlib.res.Framework"] ==
          metrics["matched_cleanup_after"]["brut.androlib.res.Framework"], "Framework metrics")
    tests = data["tests"]
    for side in ("baseline", "cleanup"):
        check(tests[side] == {"tests": 176, "failures": 0, "errors": 0, "skipped": 1, "xml_files": 42}, f"{side} tests")
    check(tests["identity_outcome_differences"] == 0, "testcase outcomes")
    validation = data["validation"]["mapper_members_v2_20261104_164526_337995"]
    for key, count in {"matched": 50, "index_match": 50, "calls_match": 21,
                       "visits_match": 30, "inner invocations_match": 37}.items():
        check(validation[key] == count, f"validation {key}")
    check(data["mismatch_example_summary"]["missing_call_occurrences"] == 563, "missing calls")
    before_test = data["historical_before_tests"]
    check((before_test["tests"], before_test["passed"], before_test["skipped"],
           before_test["failures"], before_test["errors"], before_test["exit_code"]) ==
          (176, 175, 1, 0, 0, 0), "historical-before test result")
    for version in ("2", "3", "4"):
        provenance = data["algorithm_provenance"][version]
        candidate = HERE / "publication/inputs" / f"apktool_classsplitter_candidate_v{version}.csv"
        cache_folder = "results" if version == "2" else f"results_v{version}"
        cache = HERE / cache_folder / "apktool_similarity_cache.json"
        for name, expected in provenance["input_hashes_verified"].items():
            path = HERE / "apktool_ground_truth.csv" if name == "apktool_ground_truth.csv" else candidate
            check(path.is_file() and input_hash_matches(path, expected), f"version {version} input {name}")
        check(cache.is_file() and sha(cache) == provenance["cache_sha256"], f"version {version} cache")
    for algorithm, groups in data["saved_v4_group_indices"].items():
        check(sorted(index for group in groups for index in group) == list(range(1, 61)),
              f"saved v4 partition {algorithm}")
    check(len(data["saved_v4_group_indices"]["bavota"]) == 1,
          "saved Bavota no-split result")
    for convention, scores in data["sensitivity"].items():
        for algorithm, result in scores.items():
            raw = result["raw_mojofm_percent"]
            check(abs(max(0, (raw - 50) / 50) - result["upstream_transformed_score"]) < 1e-10,
                  f"transformed score {convention}/{algorithm}")

    if args.archive:
        originals = args.archive.resolve() / "extension" / "apktool" / "publication"
        for relative, expected in data["original_evidence_sha256"].items():
            path = HERE / "publication/cleanup.patch" if relative == "cleanup.patch" else originals / relative
            check(path.is_file() and sha(path) == expected, f"archived original {relative}")
        for side, relative in (("baseline", "evidence/baseline_xml.zip"),
                               ("cleanup", "evidence/cleanup_xml.zip")):
            totals, outcomes = test_results(originals / relative)
            check(totals == tests[side], f"archived {side} XML totals")
            if side == "baseline":
                prior = outcomes
            else:
                check(outcomes == prior, "archived testcase identities and outcomes")
        for side, relative in (("matched_pristine_after", "ck_pristine_20261104/class.csv"),
                               ("matched_cleanup_after", "ck_cleanup_20261104/class.csv")):
            rows = {row["class"]: row for row in csv_rows(originals / relative)}
            check(len(rows) == 166, f"archived {side} CK row count")
            for cls, values in metrics[side].items():
                check(all(rows[cls][key] == value for key, value in values.items()), f"archived {side} {cls}")
        for side, relative in (("historical_before", "evidence/metrics-before/class.csv"),
                               ("historical_after", "evidence/metrics-after/class.csv")):
            rows = {row["class"]: row for row in csv_rows(originals / relative)}
            for cls, values in metrics[side].items():
                check(all(rows[cls][key] == value for key, value in values.items()), f"archived {side} {cls}")
        comparisons = csv_rows(originals / "evidence/mapper_members_v2_20261104_164526_337995/matched_member_comparison.csv")
        check(len(comparisons) == 50, "archived validation row count")
        for key, expected in validation.items():
            if key.endswith("_match"):
                check(sum(row[key] == "True" for row in comparisons) == expected, f"archived validation {key}")
        for name, relative in (("sensitivity", "verified/sensitivity.json"),
                               ("algorithm_provenance", "verified/provenance.json"),
                               ("method_mapping", "verified/method_mapping.json"),
                               ("tests", "verified/tests.json"),
                               ("validation", "verified/validation.json")):
            original = json.loads((originals / relative).read_text(encoding="utf-8"))
            check(original == data[name], f"archived {name}")
        saved_v4 = json.loads((args.archive.resolve() / "extension/apktool/results_v4/comparison.json").read_text(encoding="utf-8"))
        for algorithm, result in saved_v4["algorithms"].items():
            groups = [[int(member["index"]) for member in group] for group in result["groups"]]
            check(groups == data["saved_v4_group_indices"][algorithm], f"archived v4 {algorithm}")
        before_zip = args.archive.resolve() / "followup_20261105/historical_before_tests/successful_test_xml.zip"
        check(sha(before_zip) == before_test["original_xml_zip_sha256"], "historical-before XML hash")
        before_totals, before_cases = test_results(before_zip)
        check(before_totals == {"tests": 176, "failures": 0, "errors": 0,
                                "skipped": 1, "xml_files": 42}, "historical-before XML totals")
        _, after_cases = test_results(originals / "evidence/baseline_xml.zip")
        check(before_cases == after_cases, "historical before/after testcase identities")
        print("Compact evidence and archived originals verified.")
    else:
        print("Compact evidence verified; original-file comparison requires --archive.")


if __name__ == "__main__":
    main()
