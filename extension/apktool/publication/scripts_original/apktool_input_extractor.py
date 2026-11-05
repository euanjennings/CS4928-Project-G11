from pathlib import Path
from collections import defaultdict
from bisect import bisect_left
import csv
import re
import subprocess

import javalang


ROOT = Path(__file__).resolve().parent
REPO = ROOT / "apktool-study"

SOURCE_FILE = (
    "brut.apktool/apktool-lib/src/main/java/"
    "brut/androlib/res/AndrolibResources.java"
)

CLASS_NAME = "AndrolibResources"
CLASS_FULL_NAME = "brut.androlib.res.AndrolibResources"
BEFORE_COMMIT = "9c495cae"

GROUND_TRUTH = ROOT / "apktool_ground_truth.csv"
OUTPUT = ROOT / "apktool_classsplitter_candidate.csv"

MODIFIERS = {
    "public": 1,
    "private": 2,
    "protected": 4,
    "static": 8,
    "final": 16,
    "synchronized": 32,
    "volatile": 64,
    "transient": 128,
    "native": 256,
    "abstract": 1024,
    "strictfp": 2048,
}


def get_source():
    result = subprocess.run(
        [
            "git",
            "-C",
            str(REPO),
            "show",
            f"{BEFORE_COMMIT}:{SOURCE_FILE}",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )

    return result.stdout


def parameter_type(parameter):
    node = parameter.type

    while getattr(node, "sub_type", None) is not None:
        node = node.sub_type

    name = node.name.split(".")[-1]
    dimensions = "[]" * len(parameter.type.dimensions or [])

    return name + dimensions + (
        "..." if parameter.varargs else ""
    )


def signature(method):
    parameters = ",".join(
        parameter_type(p) for p in method.parameters
    )

    return f"{method.name}({parameters})"


def get_members(java_class):
    members = []

    for declaration in java_class.body:
        if isinstance(
            declaration,
            javalang.tree.FieldDeclaration,
        ):
            for field in declaration.declarators:
                members.append({
                    "kind": "Field",
                    "name": field.name,
                    "node": declaration,
                })

        elif isinstance(
            declaration,
            javalang.tree.MethodDeclaration,
        ):
            members.append({
                "kind": "Method",
                "name": signature(declaration),
                "node": declaration,
            })

        elif isinstance(
            declaration,
            javalang.tree.ConstructorDeclaration,
        ):
            members.append({
                "kind": "Constructor",
                "name": signature(declaration),
                "node": declaration,
            })

    return members


def get_source_text(source, node, tokens, offsets, line_starts):
    if node.position is None:
        raise ValueError("Declaration has no source position")

    start = (
        line_starts[node.position.line - 1]
        + node.position.column
        - 1
    )

    first = bisect_left(offsets, start)

    is_field = isinstance(
        node,
        javalang.tree.FieldDeclaration,
    )

    if is_field:
        depth = 0

        for i in range(first, len(tokens)):
            value = tokens[i].value

            if value == "{":
                depth += 1
            elif value == "}":
                depth -= 1
            elif value == ";" and depth == 0:
                return source[start:offsets[i] + 1]

    else:
        # Find the declaration's parameter list.
        parameter_start = None

        for i in range(first, len(tokens) - 1):
            if (
                tokens[i].value == node.name
                and tokens[i + 1].value == "("
            ):
                parameter_start = i + 1
                break

        if parameter_start is None:
            raise ValueError(
                f"Cannot find declaration: {node.name}"
            )

        parentheses = 0
        parameter_end = None

        for i in range(parameter_start, len(tokens)):
            value = tokens[i].value

            if value == "(":
                parentheses += 1
            elif value == ")":
                parentheses -= 1

                if parentheses == 0:
                    parameter_end = i
                    break

        if parameter_end is None:
            raise ValueError(
                f"Unclosed parameter list: {node.name}"
            )

        body_start = None

        for i in range(parameter_end + 1, len(tokens)):
            if tokens[i].value == "{":
                body_start = i
                break

            if tokens[i].value == ";":
                return source[start:offsets[i] + 1]

        if body_start is None:
            raise ValueError(
                f"Cannot find method body: {node.name}"
            )

        depth = 0

        for i in range(body_start, len(tokens)):
            value = tokens[i].value

            if value == "{":
                depth += 1
            elif value == "}":
                depth -= 1

                if depth == 0:
                    return source[start:offsets[i] + 1]

    raise ValueError("Cannot determine declaration boundary")


def get_field_visits(method, field_names):
    visits = []

    for _, reference in method.filter(
        javalang.tree.MemberReference
    ):
        if (
            reference.member in field_names
            and reference.qualifier in (None, "", "this")
        ):
            visits.append(reference.member)

    return visits


def get_local_calls(method, local_methods):
    calls = []

    for _, invocation in method.filter(
        javalang.tree.MethodInvocation
    ):
        if invocation.qualifier not in (None, "", "this"):
            continue

        candidates = local_methods.get(
            (invocation.member, len(invocation.arguments)),
            [],
        )

        if len(candidates) == 1:
            calls.append(
                f"{CLASS_FULL_NAME}+{candidates[0]}"
            )

    return calls


def main():
    if not GROUND_TRUTH.exists():
        raise FileNotFoundError(
            f"Missing ground truth: {GROUND_TRUTH}"
        )

    if OUTPUT.exists():
        raise FileExistsError(
            f"Output already exists: {OUTPUT}"
        )

    source = get_source()
    tree = javalang.parse.parse(source)

    java_class = next(
        item for item in tree.types
        if item.name == CLASS_NAME
    )

    members = get_members(java_class)

    with GROUND_TRUTH.open(
        newline="", encoding="utf-8"
    ) as file:
        ground_truth = list(csv.DictReader(file))

    if len(members) != len(ground_truth):
        raise ValueError(
            "Member count differs from ground truth"
        )

    for member, expected in zip(members, ground_truth):
        if (
            member["name"] != expected["name"]
            or member["kind"] != expected["type"]
        ):
            raise ValueError(
                f"Member mismatch: {member['name']}"
            )

    field_names = {
        member["name"]
        for member in members
        if member["kind"] == "Field"
    }

    local_methods = defaultdict(list)

    for member in members:
        if member["kind"] not in ("Method", "Constructor"):
            continue

        node = member["node"]
        local_methods[
            (node.name, len(node.parameters))
        ].append(member["name"])

    field_visitors = defaultdict(list)
    method_visits = {}

    for member in members:
        if member["kind"] not in ("Method", "Constructor"):
            continue

        visits = get_field_visits(
            member["node"],
            field_names,
        )

        method_visits[member["name"]] = visits

        for field_name in set(visits):
            field_visitors[field_name].append(
                member["name"]
            )

    line_starts = [0]

    for match in re.finditer("\n", source):
        line_starts.append(match.end())

    tokens = list(
        javalang.tokenizer.tokenize(source)
    )

    offsets = [
        line_starts[token.position.line - 1]
        + token.position.column
        - 1
        for token in tokens
    ]

    rows = []

    for index, (member, expected) in enumerate(
        zip(members, ground_truth),
        start=1,
    ):
        node = member["node"]
        name = member["name"]
        kind = member["kind"]

        code = get_source_text(
            source,
            node,
            tokens,
            offsets,
            line_starts,
        )

        if kind == "Field":
            inner_invocations = " ".join(
                field_visitors[name]
            )
            calls = ""
            visits = ""

        else:
            inner_invocations = ""

            calls = " ".join(
                get_local_calls(
                    node,
                    local_methods,
                )
            )

            visits = " ".join(
                f"{CLASS_FULL_NAME}+{field}"
                for field in method_visits[name]
            )

        modifier = sum(
            MODIFIERS.get(value, 0)
            for value in node.modifiers
        )

        annotations = " ".join(
            "@" + annotation.name
            for annotation in node.annotations
        )

        rows.append({
            "index": index,
            "name": name,
            "type": (
                "Method"
                if kind == "Constructor"
                else kind
            ),
            "inner invocations": inner_invocations,
            "external invocations": "",
            "calls": calls,
            "visits": visits,
            "length": len(code),
            "lines": code.count("\n") + 1,
            "modifier": modifier,
            "annotation": annotations,
            "full text": code,
            "removed": expected["removed"],
        })

    if len(rows) != 60:
        raise ValueError(
            f"Expected 60 members, found {len(rows)}"
        )

    if sum(
        row["removed"] == "True"
        for row in rows
    ) != 10:
        raise ValueError(
            "Expected exactly 10 extracted members"
        )

    columns = [
        "index",
        "name",
        "type",
        "inner invocations",
        "external invocations",
        "calls",
        "visits",
        "length",
        "lines",
        "modifier",
        "annotation",
        "full text",
        "removed",
    ]

    with OUTPUT.open(
        "x", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Input generation completed")
    print("Total members:", len(rows))
    print(
        "Method rows:",
        sum(row["type"] == "Method" for row in rows),
    )
    print(
        "Field rows:",
        sum(row["type"] == "Field" for row in rows),
    )
    print(
        "Methods with local field visits:",
        sum(
            bool(row["visits"])
            for row in rows
            if row["type"] == "Method"
        ),
    )
    print(
        "Extracted members:",
        sum(row["removed"] == "True" for row in rows),
    )
    print("Output:", OUTPUT)
    print()
    print("WARNING: This is a candidate input.")
    print(
        "External method calls and field bindings "
        "have not been fully resolved."
    )
    print(
        "Validate the extraction before using "
        "it for final algorithm scores."
    )


if __name__ == "__main__":
    main()