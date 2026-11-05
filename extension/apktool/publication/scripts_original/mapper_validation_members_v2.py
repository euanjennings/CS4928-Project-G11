"""Test targeted member and signature fixes against the authors' MapperHelper data.

Run from the CS4928-Project-G11 directory with the interpreter containing
javalang 0.13.0. This is a read-only diagnostic for project source files.
It writes a new timestamped folder beside the group repository.

This version adds nested enum/class members and retains qualified/generic
parameter types. It does not modify the original Apktool extractors, repair
call or field bindings, score algorithms, or certify parser equivalence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


COLUMNS = [
    "index", "name", "type", "inner invocations", "external invocations",
    "calls", "visits", "length", "lines", "modifier", "annotation",
    "full text", "removed",
]
REL_SOURCE = Path("results/event_a/source/Mapper_before.java")
REL_REFERENCE = Path(
    "upstream/dataset/refactor_example_position/13+MapperHelper+MapperTemplate.csv"
)
PACKAGE_CLASS = "com.github.abel533.mapper.MapperHelper"


def locate_week9() -> Path:
    current = Path.cwd().resolve()
    candidates = [current, current.parent]
    for directory in candidates:
        if (directory / "CS4928-Project-G11" / REL_SOURCE).is_file():
            return directory
    raise SystemExit(
        "Run this from CS4928-Project-G11 or its Week_9 parent folder. "
        "Mapper_before.java could not be found."
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_tokens(value: str) -> Counter[str]:
    return Counter(value.split())


def normalize_code_tokens(source: str, javalang) -> list[str] | None:
    try:
        return [token.value for token in javalang.tokenizer.tokenize(source)]
    except Exception:
        return None


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def type_name(java_type) -> str:
    """Render qualified and parameterized Java types without dropping details."""
    parts = []
    node = java_type
    while node is not None:
        piece = node.name
        arguments = getattr(node, "arguments", None) or []
        if arguments:
            rendered = []
            for argument in arguments:
                if argument.type is None:
                    arg_text = "?"
                else:
                    arg_text = type_name(argument.type)
                if getattr(argument, "pattern_type", None):
                    arg_text = f"? {argument.pattern_type} {arg_text}"
                rendered.append(arg_text)
            piece += "<" + ",".join(rendered) + ">"
        parts.append(piece)
        node = getattr(node, "sub_type", None)
    return ".".join(parts) + "[]" * len(java_type.dimensions or [])


def exact_signature(method) -> str:
    parameters = ",".join(
        type_name(parameter.type) + ("..." if parameter.varargs else "")
        for parameter in method.parameters
    )
    return f"{method.name}({parameters})"


def discover_members(java_class, javalang) -> list[dict]:
    """Flatten nested fields/methods in Java source order for this test."""
    members = []

    def visit(declaration):
        if isinstance(declaration, javalang.tree.FieldDeclaration):
            for field in declaration.declarators:
                members.append({
                    "kind": "Field", "name": field.name, "node": declaration
                })
        elif isinstance(declaration, javalang.tree.MethodDeclaration):
            members.append({
                "kind": "Method", "name": exact_signature(declaration),
                "node": declaration
            })
        elif isinstance(declaration, javalang.tree.ConstructorDeclaration):
            members.append({
                "kind": "Constructor", "name": exact_signature(declaration),
                "node": declaration
            })
        elif isinstance(declaration, javalang.tree.EnumDeclaration):
            # The authors represent the nested enum itself as one Field row.
            # Enum constants are not separate rows in this reference example.
            members.append({
                "kind": "Field", "name": declaration.name,
                "node": declaration
            })
            for child in declaration.body.declarations:
                visit(child)
        elif isinstance(declaration, javalang.tree.ClassDeclaration):
            # The author's example flattens nested Config fields but does not
            # include a separate row for the Config class declaration.
            for child in declaration.body:
                visit(child)

    for declaration in java_class.body:
        visit(declaration)
    return members


def build_candidate(source: str, original, javalang) -> tuple[list[dict], list[str]]:
    tree = javalang.parse.parse(source)
    java_class = next((item for item in tree.types if item.name == "MapperHelper"), None)
    if java_class is None:
        raise ValueError("MapperHelper class not found in the Java source")

    members = discover_members(java_class, javalang)
    field_names = {m["name"] for m in members if m["kind"] == "Field"}
    local_methods = defaultdict(list)
    for member in members:
        if member["kind"] in {"Method", "Constructor"}:
            node = member["node"]
            local_methods[(node.name, len(node.parameters))].append(member["name"])

    field_visitors = defaultdict(list)
    member_visits = {}
    for member in members:
        if member["kind"] not in {"Method", "Constructor"}:
            continue
        visits = original.get_field_visits(member["node"], field_names)
        member_visits[member["name"]] = visits
        for field in set(visits):
            field_visitors[field].append(member["name"])

    line_starts = [0] + [match.end() for match in re.finditer("\n", source)]
    tokens = list(javalang.tokenizer.tokenize(source))
    offsets = [
        line_starts[token.position.line - 1] + token.position.column - 1
        for token in tokens
    ]

    rows = []
    errors = []
    for index, member in enumerate(members, start=1):
        node, name, kind = member["node"], member["name"], member["kind"]
        try:
            if isinstance(node, javalang.tree.EnumDeclaration):
                start = line_starts[node.position.line - 1] + node.position.column - 1
                end = source.index("{", start)
                code = source[start:end].strip()
            else:
                code = original.get_source_text(
                    source, node, tokens, offsets, line_starts
                )
        except Exception as exc:
            code = ""
            errors.append(f"{name}: {type(exc).__name__}: {exc}")

        if kind == "Field":
            incoming = " ".join(field_visitors[name])
            outgoing_calls = ""
            visits = ""
        else:
            incoming = ""
            outgoing_calls = " ".join(
                original.get_local_calls(node, local_methods)
            )
            visits = " ".join(
                f"{PACKAGE_CLASS}+{field}" for field in member_visits[name]
            )

        rows.append({
            "index": index,
            "name": name,
            "type": "Method" if kind == "Constructor" else kind,
            "inner invocations": incoming,
            "external invocations": "",  # The v2 extractor does not resolve them.
            "calls": outgoing_calls,
            "visits": visits,
            "length": len(code),
            "lines": code.count("\n") + 1 if code else 0,
            "modifier": sum(original.MODIFIERS.get(v, 0) for v in node.modifiers),
            "annotation": " ".join("@" + a.name for a in node.annotations),
            "full text": code,
            "removed": "",  # Never invent Mapper ground truth.
        })

    return rows, errors


def main() -> None:
    week9 = locate_week9()
    group_repo = week9 / "CS4928-Project-G11"
    source_path = group_repo / REL_SOURCE
    reference_path = group_repo / REL_REFERENCE

    if not reference_path.is_file():
        raise SystemExit(f"Reference file not found: {reference_path}")
    if not (week9 / "apktool_input_extractor_v2.py").is_file():
        raise SystemExit("Missing Week_9/apktool_input_extractor_v2.py")

    sys.path.insert(0, str(week9))
    try:
        import javalang
        import apktool_input_extractor_v2 as v2
    except ImportError as exc:
        raise SystemExit(
            f"Required import failed: {exc}. Run with the temporary cs4928-venv "
            "interpreter that has javalang 0.13.0."
        ) from exc

    original = v2.original
    original.CLASS_FULL_NAME = PACKAGE_CLASS
    source = source_path.read_text(encoding="utf-8-sig")

    with reference_path.open(newline="", encoding="utf-8-sig") as handle:
        reference = list(csv.DictReader(handle))
    if not reference or list(reference[0]) != COLUMNS:
        raise SystemExit("Reference file has an unexpected column schema")

    candidate, extraction_errors = build_candidate(source, original, javalang)
    ref_by_key = {(r["name"], r["type"]): r for r in reference}
    cand_by_key = {(r["name"], r["type"]): r for r in candidate}

    if len(ref_by_key) != len(reference) or len(cand_by_key) != len(candidate):
        raise SystemExit("Duplicate name/type identities found; manual review needed")

    missing = [r["name"] for r in reference if (r["name"], r["type"]) not in cand_by_key]
    extra = [r["name"] for r in candidate if (r["name"], r["type"]) not in ref_by_key]

    fields_to_compare = [
        "index", "inner invocations", "external invocations", "calls", "visits",
        "length", "lines", "modifier", "annotation", "full text",
    ]
    token_columns = {"inner invocations", "external invocations", "calls", "visits"}
    results = []
    agreement = Counter()
    for candidate_row in candidate:
        key = (candidate_row["name"], candidate_row["type"])
        expected = ref_by_key.get(key)
        if expected is None:
            continue
        row = {"name": candidate_row["name"], "type": candidate_row["type"]}
        for column in fields_to_compare:
            actual_value = str(candidate_row[column])
            expected_value = str(expected[column])
            if column in token_columns:
                same = count_tokens(actual_value) == count_tokens(expected_value)
            elif column == "full text":
                actual_tokens = normalize_code_tokens(actual_value, javalang)
                expected_tokens = normalize_code_tokens(expected_value, javalang)
                same = (actual_tokens is not None and expected_tokens is not None
                        and actual_tokens == expected_tokens)
            elif column == "annotation":
                same = " ".join(actual_value.split()) == " ".join(expected_value.split())
            else:
                same = actual_value == expected_value
            row[column + "_match"] = str(same)
            agreement[column] += int(same)
        results.append(row)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    output_dir = week9 / f"mapper_members_v2_{timestamp}"
    output_dir.mkdir(exist_ok=False)
    write_csv(output_dir / "mapper_candidate.csv", COLUMNS, candidate)
    compare_columns = ["name", "type"] + [c + "_match" for c in fields_to_compare]
    write_csv(output_dir / "matched_member_comparison.csv", compare_columns, results)

    summary = [
        "MAPPERHELPER TARGETED MEMBER/SIGNATURE DIAGNOSTIC (NOT A VALIDATION PASS)",
        "Apktool v2 logic with nested member and qualified signature corrections.",
        "External Java bindings remain unresolved; originals are unchanged.",
        "",
        f"Reference members: {len(reference)}",
        f"Extractor members: {len(candidate)}",
        f"Exactly matched identities (name and type): {len(results)}",
        f"Missing reference members: {len(missing)}",
        f"Extra extractor members: {len(extra)}",
        f"Extraction errors: {len(extraction_errors)}",
        "",
        "AGREEMENT AMONG MATCHED IDENTITIES",
    ]
    for column in fields_to_compare:
        summary.append(f"  {column}: {agreement[column]}/{len(results)}")
    summary += [
        "",
        "MISSING FROM EXTRACTOR (FIRST 30)",
        *[f"  - {name}" for name in missing[:30]],
        "",
        "EXTRA IN EXTRACTOR (FIRST 30)",
        *[f"  - {name}" for name in extra[:30]],
        "",
        "EXTRACTION ERRORS (FIRST 30)",
        *[f"  - {error}" for error in extraction_errors[:30]],
        "",
        "CAUTION: Equal token sequences do not establish equivalent symbol binding.",
        "Do not use this diagnostic output as an algorithm input.",
    ]
    (output_dir / "summary.txt").write_text("\n".join(summary) + "\n", encoding="utf-8")
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "javalang_version": getattr(javalang, "__version__", "unknown"),
        "source_sha256": sha256(source_path),
        "reference_sha256": sha256(reference_path),
        "extractor_v1_sha256": sha256(week9 / "apktool_input_extractor.py"),
        "extractor_v2_sha256": sha256(week9 / "apktool_input_extractor_v2.py"),
        "reference_rows": len(reference),
        "candidate_rows": len(candidate),
        "matched_member_rows": len(results),
        "status": "targeted_member_signature_diagnostic_only",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print("\n".join(summary[:17]))
    print("\nResults saved:", output_dir)
    print("Upload summary.txt and matched_member_comparison.csv for review.")


if __name__ == "__main__":
    main()
