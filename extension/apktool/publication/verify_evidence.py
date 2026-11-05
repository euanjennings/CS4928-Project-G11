"""Recompute preserved test outcomes, validation counts and fixed-partition sensitivity.

Uses only stdlib and the repository's shipped Java MoJo evaluator. Output must
not exist. No algorithms are retrained and no original files are overwritten.
"""
import argparse
import csv
import hashlib
import json
import subprocess
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tests(path):
    outcomes = Counter()
    totals = Counter()
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            root = ET.fromstring(z.read(name))
            totals.update({k: int(root.get(k, 0)) for k in ("tests", "failures", "errors", "skipped")})
            for t in root.iter("testcase"):
                status = next((k for k in ("failure", "error", "skipped") if t.find(k) is not None), "passed")
                outcomes[(t.get("classname"), t.get("name"), status)] += 1
        totals["xml_files"] = len(z.namelist())
    return dict(totals), outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    a, ai = tests(HERE / "evidence/baseline_xml.zip")
    b, bi = tests(HERE / "evidence/cleanup_xml.zip")
    result = {"baseline": a, "cleanup": b, "identity_outcome_differences": sum((ai-bi).values()) + sum((bi-ai).values())}
    (out / "tests.json").write_text(json.dumps(result, indent=2))
    with (out / "testcases.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["class", "test", "outcome", "baseline_count", "cleanup_count"])
        for key in sorted(ai.keys() | bi.keys()): w.writerow([*key, ai[key], bi[key]])
    counts = {}
    for name in ("mapper_validation_20261104_161640_027932", "mapper_members_v2_20261104_164526_337995"):
        data = rows(HERE / "evidence" / name / "matched_member_comparison.csv")
        counts[name] = {k: sum(r[k] == "True" for r in data) for k in data[0] if k.endswith("_match")}
        counts[name]["matched"] = len(data)
    (out / "validation.json").write_text(json.dumps(counts, indent=2))
    truth = rows(HERE / "inputs/apktool_ground_truth.csv")
    comparisons = {}
    for version, folder in [(2, "results"), (3, "results_v3"), (4, "results_v4")]:
        p = HERE.parent / folder / "comparison.json"
        j = json.loads(p.read_text())
        hashes = {n: sha(HERE / "inputs" / n) for n in j["input_hashes"]}
        assert hashes == j["input_hashes"], (version, hashes, j["input_hashes"])
        comparisons[str(version)] = {"json_sha256": sha(p), "input_hashes_verified": hashes, "seed": j["seed"], "model": j["model"], "cache_sha256": sha(p.parent / "apktool_similarity_cache.json"), "scores": {n:d["mojofm"] for n,d in j["algorithms"].items()}}
    (out / "provenance.json").write_text(json.dumps(comparisons, indent=2))
    j = json.loads((HERE.parent / "results_v4/comparison.json").read_text())
    sensitivity = {}
    for convention in ("declarations_zero_fields", "semantic_one_field"):
        scores = {}
        for alg, data in j["algorithms"].items():
            assert sorted(int(m["index"]) for g in data["groups"] for m in g) == sorted(int(r["index"]) for r in truth)
            gp = out / f"{convention}_{alg}.rsf"
            gp.write_text("".join(f"contain c{i} {m['index']}\n" for i,g in enumerate(data["groups"]) for m in g))
            tp = out / f"{convention}_truth.rsf"
            tp.write_text("".join(f"contain c{r['removed'].lower() == 'true' or (convention == 'semantic_one_field' and r['name'] == 'mFrameworkDirectory')} {r['index']}\n" for r in truth))
            raw = subprocess.check_output(["java", "-cp", str(ROOT / "upstream/Implementation/experienments"), "mojo.MoJo", str(gp), str(tp), "-fm"], text=True)
            raw = float(raw.strip()); score = max(0, (raw-50)/50)
            scores[alg] = {"raw_mojofm_percent": raw, "upstream_transformed_score": score}
            if convention == "declarations_zero_fields":
                assert abs(score-data["mojofm"]["overall"]) < 1e-10
        sensitivity[convention] = scores
    (out / "sensitivity.json").write_text(json.dumps(sensitivity, indent=2))
    print(json.dumps({"tests": result, "sensitivity": sensitivity}, indent=2))


if __name__ == "__main__":
    main()
