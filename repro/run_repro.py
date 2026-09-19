"""Bounded reproduction runner: ClassSplitter vs. Bavota baseline (upstream Baseline1).

Mirrors cells 0 and 2 of upstream/Implementation/experienments/experienment_result.ipynb,
but writes per-class raw results (CSV) and an environment record (JSON) so the run is auditable.

Usage (from the repo root, venv active):
    python repro/run_repro.py                       # all 133 classes (~5-10 min)
    python repro/run_repro.py --ids 1 2 3           # a preregistered sample: values from the 'index'
                                                    # column of GodClassRefactorDictionary.csv (1-133),
                                                    # NOT the number prefix of the data file names
    python repro/run_repro.py --out results/m2_repro.csv

Notes:
  * Upstream code must run from its own folder: data paths are relative, and MoJoFM is computed by
    shelling out to `java mojo.MoJo group.rsf example.rsf -fm` with the current folder as classpath.
  * It writes group.rsf / example.rsf into that folder on every call, so never run two
    experiments at the same time from the same checkout.
"""
import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UPSTREAM_EXP = REPO / "upstream" / "Implementation" / "experienments"
MODEL = "sentence-transformers/all-mpnet-base-v2"
CACHE = "cache_time_all-mpnet-base-v2.json"


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""


def environment():
    pkgs = {}
    for p in ["numpy", "pandas", "scipy", "scikit-learn", "networkx", "gensim", "openai", "sentence-transformers"]:
        try:
            pkgs[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            pkgs[p] = None
    java = subprocess.run(["java", "-version"], capture_output=True, text=True)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git("rev-parse", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain")),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "java": (java.stderr or java.stdout).splitlines()[0] if (java.stderr or java.stdout) else None,
        "packages": pkgs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", type=int, nargs="*", help="dictionary 'index' values to run (default: all)")
    ap.add_argument("--out", default="results/repro_full.csv", help="output CSV, relative to repo root")
    ap.add_argument("--seed", type=int, default=2026,
                    help="seed for Python's random module: upstream Baseline1 puts never-visited fields "
                         "into a random group (unseeded), so baseline field/overall MoJoFM varies run to run")
    args = ap.parse_args()

    out = (REPO / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    env = environment()  # capture BEFORE writing outputs, so git_dirty reflects the code state

    os.chdir(UPSTREAM_EXP)
    sys.path.insert(0, str(UPSTREAM_EXP))
    import matplotlib
    matplotlib.use("Agg")
    from god_class import DictHandler
    from cluster import ClusterSeparate
    from baseline1 import Baseline1
    from scipy import stats

    import random
    random.seed(args.seed)

    classes = DictHandler("GodClassRefactorDictionary.csv").get_classes()
    if args.ids:
        wanted = set(args.ids)
        classes = [c for c in classes if c.get_index() in wanted]
        missing = wanted - {c.get_index() for c in classes}
        if missing:
            sys.exit(f"Unknown ids: {sorted(missing)}")

    rows, t0 = [], time.time()
    for n, c in enumerate(classes, 1):
        b = Baseline1(c)
        b.original_graph_to_chain()
        b.original_chain_to_groups()
        b.handel_fields()  # sic (upstream spelling)

        s = ClusterSeparate(c, model_name=MODEL, cache_path=CACHE)
        s.separate_to_group()
        s.split_group_by_position()
        s.merge_adjacent_single_method()
        s.merge_separate_group()
        s.handle_fields()

        rows.append({
            "index": c.get_index(),
            "data_file": os.path.basename(c.data_path),
            "origin_class": c.get_name(),
            "extract_type": c.get_type(),
            "baseline_mojofm": b.get_mojofm(field=True),
            "baseline_method_mojofm": b.get_mojofm(field=False),
            "baseline_field_mojofm": b.get_field_mojofm(),
            "classsplitter_mojofm": s.get_mojofm(field=True),
            "classsplitter_method_mojofm": s.get_mojofm(field=False),
            "classsplitter_field_mojofm": s.get_field_mojofm(),
        })
        print(f"[{n}/{len(classes)}] {c.get_index()} {c.get_name()}", flush=True)

    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    summary = {}
    for metric in ["mojofm", "method_mojofm", "field_mojofm"]:
        base = [r[f"baseline_{metric}"] for r in rows]
        cs = [r[f"classsplitter_{metric}"] for r in rows]
        diffs = [y - x for x, y in zip(base, cs)]
        entry = {
            "n": len(rows),
            "baseline_mean": round(sum(base) / len(base), 4),
            "classsplitter_mean": round(sum(cs) / len(cs), 4),
            "wins": sum(d > 0 for d in diffs),
            "ties": sum(d == 0 for d in diffs),
            "losses": sum(d < 0 for d in diffs),
            # What upstream's show_result.draw_compare reports (independent-samples t-test):
            "upstream_ttest_ind_p": float(stats.ttest_ind(base, cs).pvalue) if len(rows) > 1 else None,
        }
        # The data are paired (same class, two approaches), so also report paired tests:
        if len(rows) > 1:
            entry["paired_ttest_rel_p"] = float(stats.ttest_rel(base, cs).pvalue)
            if any(diffs):
                entry["wilcoxon_signed_rank_p"] = float(stats.wilcoxon(base, cs).pvalue)
        summary[metric] = entry

    record = {"args": vars(args), "runtime_s": round(time.time() - t0), "summary": summary,
              "environment": env}
    out.with_suffix(".json").write_text(json.dumps(record, indent=2))

    print(json.dumps(summary, indent=2))
    print(f"\nWrote {out.relative_to(REPO)} and {out.with_suffix('.json').relative_to(REPO)}")


if __name__ == "__main__":
    main()
