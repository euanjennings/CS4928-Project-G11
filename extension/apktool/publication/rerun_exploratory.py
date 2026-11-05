"""Opt-in algorithm rerun on archived candidate features; NOT validation evidence.

Copies the existing runner and evaluator dependencies into a temporary workspace
so original outputs, upstream RSF files, and the Git index are never overwritten.
Requires the project's scientific Python dependencies. Uses the preserved cache.
"""
import argparse
import importlib.util
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", choices=[2, 3, 4], type=int, required=True)
    args = p.parse_args()
    work = Path(tempfile.mkdtemp(prefix="cs4928_exploratory_"))
    exp = work / "experiments"
    exp.mkdir()
    original = ROOT / "upstream/Implementation/experienments"
    for source in original.glob("*.py"):
        shutil.copy2(source, exp / source.name)
    shutil.copytree(original / "mojo", exp / "mojo")
    results = work / "results"
    results.mkdir()
    folder = "results" if args.version == 2 else f"results_v{args.version}"
    shutil.copy2(HERE.parent / folder / "apktool_similarity_cache.json", results / "apktool_similarity_cache.json")
    spec = importlib.util.spec_from_file_location("runner", HERE.parent / "run_apktool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.EXPERIMENTS = exp
    module.CANDIDATE = HERE / "inputs" / f"apktool_classsplitter_candidate_v{args.version}.csv"
    module.GROUND_TRUTH = HERE / "inputs/apktool_ground_truth.csv"
    module.RESULTS = results
    print("EXPLORATORY ONLY. Output:", results)
    module.main()


if __name__ == "__main__":
    main()
