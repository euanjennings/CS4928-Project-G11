from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parent

INPUT = ROOT / "apktool_classsplitter_candidate_v2.csv"
OUTPUT = ROOT / "apktool_classsplitter_candidate_v3.csv"

CLASS_PREFIX = "brut.androlib.res.AndrolibResources+"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input: {INPUT}")

    if OUTPUT.exists():
        raise FileExistsError(
            f"Version 3 already exists: {OUTPUT}"
        )

    with INPUT.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        rows = list(reader)

    if len(rows) != 60:
        raise ValueError("Expected 60 class members.")

    methods = {
        row["name"]
        for row in rows
        if row["type"] == "Method"
    }

    if len(methods) != 45:
        raise ValueError("Expected 45 method rows.")

    total_calls = 0
    methods_with_calls = 0

    for row in rows:
        if row["type"] != "Method":
            continue

        internal_calls = []

        for call in row["calls"].split():
            if not call.startswith(CLASS_PREFIX):
                raise ValueError(
                    f"Unexpected call format: {call}"
                )

            target = call[len(CLASS_PREFIX):]

            if target not in methods:
                raise ValueError(
                    f"Unknown local method: {target}"
                )

            internal_calls.append(target)

        # Resolve the known overloaded Java call.
        if row["name"] == "publicizeResources(File)":
            source = row["full text"]

            if not re.search(
                r"\bbyte\s*\[\s*\]\s+data\b",
                source
            ):
                raise ValueError(
                    "Cannot verify byte[] data declaration."
                )

            if not re.search(
                r"\bpublicizeResources\s*\(\s*data\s*\)",
                source
            ):
                raise ValueError(
                    "Cannot verify overloaded method call."
                )

            target = "publicizeResources(byte[])"

            if target not in methods:
                raise ValueError(
                    f"Missing overloaded target: {target}"
                )

            internal_calls.append(target)

        row["inner invocations"] = " ".join(
            internal_calls
        )

        total_calls += len(internal_calls)

        if internal_calls:
            methods_with_calls += 1

    if total_calls != 38:
        raise ValueError(
            f"Expected 38 calls, found {total_calls}"
        )

    with OUTPUT.open(
        "x", encoding="utf-8", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Version 3 generated successfully.")
    print("Total members:", len(rows))
    print("Method rows:", len(methods))
    print("Internal method calls:", total_calls)
    print("Methods with internal calls:", methods_with_calls)
    print("Output:", OUTPUT)

    print()
    print("VALIDATION STATUS")
    print("Member identities: preserved")
    print("Ground-truth labels: preserved")
    print("Known internal calls: corrected")
    print("External Java references: NOT YET RESOLVED")


if __name__ == "__main__":
    main()