"""Exploratory Apktool comparison: ClassSplitter versus Bavota."""

import csv
import hashlib
import json
import os
import random
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

EXPERIMENTS = (
    ROOT / "upstream" / "Implementation" / "experienments"
)

CANDIDATE = HERE / "apktool_classsplitter_candidate_v2.csv"
GROUND_TRUTH = HERE / "apktool_ground_truth.csv"
RESULTS = HERE / "results"

MODEL = "sentence-transformers/all-mpnet-base-v2"
SEED = 2026


def read_csv(path):
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


def validate_input():
    candidate = read_csv(CANDIDATE)
    truth = read_csv(GROUND_TRUTH)

    if len(candidate) != 60 or len(truth) != 60:
        raise ValueError("Expected 60 members in each input.")

    for candidate_row, truth_row in zip(candidate, truth):
        for column in ("index", "name", "removed"):
            if candidate_row[column] != truth_row[column]:
                raise ValueError(
                    f"Ground-truth mismatch: {column}"
                )

    extracted = [
        row for row in truth
        if row["removed"].lower() == "true"
    ]

    if len(extracted) != 10:
        raise ValueError("Expected exactly 10 extracted methods.")

    print("Input validation passed.")
    print("Original members:", len(candidate))
    print("Extracted methods:", len(extracted))

    return extracted


def prepare_case():
    from god_class import GodClass

    case_data = {
        "index": 9999,
        "last index": 9999,
        "data path": str(CANDIDATE),
        "origin class": "brut.androlib.res.AndrolibResources",
        "extract type": "Extract Class",
    }

    case = GodClass(pd.DataFrame([case_data]))

    for column in (
        "inner invocations",
        "external invocations",
        "calls",
        "visits",
    ):
        case.data_frame[column] = (
            case.data_frame[column]
            .astype("object")
            .where(case.data_frame[column].notna(), "")
        )

    case.data_frame["removed"] = (
        case.data_frame["removed"]
        .astype(str)
        .str.lower()
        .eq("true")
    )

    return case


def get_groups(algorithm):
    groups = []

    for group in algorithm.groups:
        members = sorted(
            group.get_members(),
            key=lambda member: member.get_index()
        )

        groups.append([
            {
                "index": member.get_index(),
                "name": member.get_name(),
                "type": (
                    "Method" if member.is_method() else "Field"
                ),
            }
            for member in members
        ])

    return groups


def measure(algorithm):
    return {
        "overall": float(
            algorithm.get_mojofm(field=True)
        ),
        "methods": float(
            algorithm.get_mojofm(field=False)
        ),
        "fields": float(
            algorithm.get_field_mojofm()
        ),
    }


def run_classsplitter(case, cache_path, use_position):
    from cluster import ClusterSeparate

    algorithm = ClusterSeparate(
        case,
        model_name=MODEL,
        cache_path=str(cache_path),
    )

    if not use_position:
        algorithm.set_use_similarity({
            "PS": 0,
            "MS": 1,
            "CS": 1,
        })

    algorithm.separate_to_group()
    algorithm.split_group_by_position()
    algorithm.merge_adjacent_single_method()
    algorithm.merge_separate_group()
    algorithm.handle_fields()

    return algorithm


def main():
    if sys.flags.optimize:
        raise RuntimeError(
            "Do not use optimized Python execution."
        )

    extracted = validate_input()

    RESULTS.mkdir(parents=True, exist_ok=True)

    os.chdir(EXPERIMENTS)
    sys.path.insert(0, str(EXPERIMENTS))

    import matplotlib
    matplotlib.use("Agg")

    from baseline1 import Baseline1

    random.seed(SEED)

    case = prepare_case()

    print("\nRunning Bavota baseline...", flush=True)

    bavota = Baseline1(case)
    bavota.original_graph_to_chain()
    bavota.original_chain_to_groups()
    bavota.handel_fields()

    print("\nRunning ClassSplitter...", flush=True)

    cache_path = RESULTS / "apktool_similarity_cache.json"

    classsplitter = run_classsplitter(
        case,
        cache_path,
        use_position=True,
    )

    print(
        "\nRunning ClassSplitter without position...",
        flush=True,
    )

    without_position = run_classsplitter(
        case,
        cache_path,
        use_position=False,
    )

    algorithms = {
        "bavota": bavota,
        "classsplitter": classsplitter,
        "classsplitter_without_position": without_position,
    }

    results = {
        "project": "Apktool",
        "before_commit": "9c495cae",
        "after_commit": "40d427e5",
        "seed": SEED,
        "model": MODEL,
        "input_status": (
            "EXPLORATORY: external Java references "
            "are not fully resolved"
        ),
        "input_hashes": {
            path.name: hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in (CANDIDATE, GROUND_TRUTH)
        },
        "ground_truth_extracted": [
            row["name"] for row in extracted
        ],
        "algorithms": {},
    }

    for name, algorithm in algorithms.items():
        results["algorithms"][name] = {
            "mojofm": measure(algorithm),
            "groups": get_groups(algorithm),
        }

    output = RESULTS / "comparison.json"

    output.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print("\nRESULTS")

    for name, data in results["algorithms"].items():
        scores = data["mojofm"]

        print(
            f"{name}: "
            f"overall={scores['overall']:.4f}, "
            f"methods={scores['methods']:.4f}, "
            f"fields={scores['fields']:.4f}"
        )

    print("\nSaved:", output)
    print(
        "WARNING: Results are preliminary until "
        "external Java references are validated."
    )


if __name__ == "__main__":
    main()