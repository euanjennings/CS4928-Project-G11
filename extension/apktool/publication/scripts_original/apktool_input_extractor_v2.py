from pathlib import Path
import csv
import re

import javalang
import apktool_input_extractor as original


# Preserve the original function.
previous_get_source_text = original.get_source_text


def corrected_source_text(
    source, node, tokens, offsets, line_starts
):
    code = previous_get_source_text(
        source, node, tokens, offsets, line_starts
    )

    # javalang may begin at the return type instead
    # of the Java declaration's access modifier.
    start = (
        line_starts[node.position.line - 1]
        + node.position.column
        - 1
    )

    line_start = line_starts[node.position.line - 1]
    prefix = source[line_start:start].strip()

    modifier_pattern = (
        r"\b(public|private|protected|static|final|"
        r"abstract|synchronized|native|strictfp|"
        r"transient|volatile)\b"
    )

    if prefix and re.search(modifier_pattern, prefix):
        code = prefix + " " + code

    return code


def qualifier_field(qualifier, field_names):
    if not qualifier:
        return None

    parts = qualifier.split(".")

    if parts[0] == "this" and len(parts) > 1:
        candidate = parts[1]
    else:
        candidate = parts[0]

    return candidate if candidate in field_names else None


def corrected_field_visits(method, field_names):
    visits = []

    for _, reference in method.filter(
        javalang.tree.MemberReference
    ):
        # Direct field references.
        if (
            reference.member in field_names
            and reference.qualifier in (None, "", "this")
        ):
            visits.append(reference.member)

        # Qualified references such as config.frameworkDirectory.
        field = qualifier_field(
            reference.qualifier, field_names
        )

        if field:
            visits.append(field)

    for _, invocation in method.filter(
        javalang.tree.MethodInvocation
    ):
        # Calls such as LOGGER.severe(...).
        field = qualifier_field(
            invocation.qualifier, field_names
        )

        if field:
            visits.append(field)

    return visits


# Apply the corrections without editing the original script.
original.get_source_text = corrected_source_text
original.get_field_visits = corrected_field_visits

# Create a separate output. Never overwrite version 1.
original.OUTPUT = (
    original.ROOT / "apktool_classsplitter_candidate_v2.csv"
)


def main():
    original.main()

    with original.OUTPUT.open(
        newline="", encoding="utf-8"
    ) as file:
        rows = list(csv.DictReader(file))

    method = next(
        row for row in rows
        if row["name"] == "getFrameworkDirectory()"
    )

    print()
    print("Verification:")
    print("Source begins:", method["full text"].splitlines()[0])
    print("Field visits:", method["visits"])

    expected_fields = [
        "mFrameworkDirectory",
        "config",
        "LOGGER",
    ]

    missing = [
        field
        for field in expected_fields
        if f"{original.CLASS_FULL_NAME}+{field}"
        not in method["visits"]
    ]

    if missing:
        print("WARNING: Missing field references:", missing)
    else:
        print("All three expected local fields were identified.")

    print()
    print(
        "This remains a candidate input. "
        "External Java references are not fully resolved."
    )


if __name__ == "__main__":
    main()