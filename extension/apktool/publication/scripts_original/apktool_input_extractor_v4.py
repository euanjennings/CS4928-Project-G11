"""Apktool input validation: incoming calls from the pre-refactoring commit.

Keeps version 2 intact and writes a new, explicitly provisional CSV.
"""

from collections import defaultdict
from pathlib import Path
import csv
import re
import subprocess

import javalang


ROOT = Path(__file__).resolve().parent
REPO = ROOT / "apktool-study"
SOURCE = ROOT / "apktool_classsplitter_candidate_v2.csv"
OUTPUT = ROOT / "apktool_classsplitter_candidate_v4.csv"
REVISION = "9c495cae"
CLASS_NAME = "AndrolibResources"
PREFIX = "brut.androlib.res.AndrolibResources+"

CLIENT_FILES = (
    "brut.apktool/apktool-cli/src/main/java/brut/apktool/Main.java",
    "brut.apktool/apktool-lib/src/main/java/brut/androlib/ApkBuilder.java",
    "brut.apktool/apktool-lib/src/main/java/brut/androlib/ApkDecoder.java",
    "brut.apktool/apktool-lib/src/main/java/brut/androlib/res/data/ResTable.java",
    "brut.apktool/apktool-lib/src/test/java/brut/androlib/TestUtils.java",
    "brut.apktool/apktool-lib/src/test/java/brut/androlib/aapt1/SharedLibraryTest.java",
    "brut.apktool/apktool-lib/src/test/java/brut/androlib/aapt2/BuildAndDecodeTest.java",
    "brut.apktool/apktool-lib/src/test/java/brut/androlib/androlib/InvalidSdkBoundingTest.java",
)


def load_revision(path):
    result = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{REVISION}:{path}"],
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
    dims = "[]" * len(parameter.type.dimensions or [])
    return name + dims + ("..." if parameter.varargs else "")


def signature(method):
    return method.name + "(" + ",".join(
        parameter_type(p) for p in method.parameters
    ) + ")"


def is_resource_type(type_node):
    return getattr(type_node, "name", "").split(".")[-1] == CLASS_NAME


def signature_arity(value):
    params = value.split("(", 1)[1].rstrip(")")
    if not params:
        return 0
    depth = 0
    count = 1
    for char in params:
        if char == "<":
            depth += 1
        elif char == ">":
            depth -= 1
        elif char == "," and depth == 0:
            count += 1
    return count


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Output exists: {OUTPUT}")

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames
        rows = list(reader)

    if len(rows) != 60:
        raise ValueError(f"Expected 60 class members, found {len(rows)}")

    by_name = {row["name"]: row for row in rows}
    targets = defaultdict(list)
    method_arity = defaultdict(list)
    for row in rows:
        if row["type"] == "Method":
            method_name = row["name"].split("(", 1)[0]
            arity = signature_arity(row["name"])
            method_arity[(method_name, arity)].append(row["name"])
            row["inner invocations"] = ""
        row["external invocations"] = ""

    # Calls are outgoing; "inner invocations" lists incoming callers.
    local_edges = 0
    for caller in rows:
        if caller["type"] != "Method":
            continue
        outgoing = caller["calls"].split()
        if caller["name"] == "publicizeResources(File)":
            if not re.search(
                r"\bpublicizeResources\s*\(\s*data\s*\)",
                caller["full text"],
            ):
                raise ValueError("Cannot verify overload call")
            outgoing.append(PREFIX + "publicizeResources(byte[])")
            caller["calls"] = " ".join(outgoing)
        for target in outgoing:
            if not target.startswith(PREFIX):
                raise ValueError(f"Unrecognized outgoing call: {target}")
            short = target[len(PREFIX):]
            if short not in by_name:
                raise ValueError(f"Unknown internal target: {short}")
            targets[short].append(caller["name"])
            local_edges += 1

    if local_edges != 38:
        raise ValueError(f"Expected 38 local calls, got {local_edges}")

    def resolve(invocation):
        key = (invocation.member, len(invocation.arguments or []))
        choices = method_arity.get(key, [])
        if len(choices) == 1:
            return choices[0]
        if key == ("publicizeResources", 1):
            arg = invocation.arguments[0]
            if (
                isinstance(arg, javalang.tree.ClassCreator)
                and getattr(arg.type, "name", None) == "File"
            ):
                return "publicizeResources(File)"
        raise ValueError(f"Cannot uniquely resolve call: {key} ({choices})")

    external_calls = 0
    external_fields = 0
    for path in CLIENT_FILES:
        unit = javalang.parse.parse(load_revision(path))
        package = unit.package.name if unit.package else ""

        for java_class in unit.types:
            if not isinstance(java_class, javalang.tree.ClassDeclaration):
                continue
            resource_fields = {
                item.name
                for field in java_class.fields
                if is_resource_type(field.type)
                for item in field.declarators
            }

            for caller in [*java_class.methods, *java_class.constructors]:
                caller_name = f"{package}.{java_class.name}+{signature(caller)}"
                variables = set(resource_fields)

                for parameter in caller.parameters:
                    if is_resource_type(parameter.type):
                        variables.add(parameter.name)
                for _, declaration in caller.filter(javalang.tree.LocalVariableDeclaration):
                    if is_resource_type(declaration.type):
                        variables.update(item.name for item in declaration.declarators)

                field_sites = set()
                for _, invocation in caller.filter(javalang.tree.MethodInvocation):
                    qualifier = invocation.qualifier or ""
                    if qualifier.removeprefix("this.") in variables:
                        target = resolve(invocation)
                        targets[target].append(caller_name)
                        external_calls += 1
                    else:
                        parts = qualifier.removeprefix("this.").split(".")
                        if len(parts) >= 2 and parts[0] in variables:
                            field = parts[1]
                            if field in by_name and by_name[field]["type"] == "Field":
                                line = invocation.position.line if invocation.position else -1
                                field_sites.add((field, line))

                for _, reference in caller.filter(javalang.tree.MemberReference):
                    qualifier = (reference.qualifier or "").removeprefix("this.")
                    if qualifier in variables and reference.member in by_name:
                        if by_name[reference.member]["type"] == "Field":
                            line = reference.position.line if reference.position else -1
                            field_sites.add((reference.member, line))

                for _, creator in caller.filter(javalang.tree.ClassCreator):
                    if not is_resource_type(creator.type):
                        continue
                    ctor_name = ("AndrolibResources(Config)"
                                 if len(creator.arguments or []) == 1
                                 else "AndrolibResources()")
                    targets[ctor_name].append(caller_name)
                    external_calls += 1
                    for selector in creator.selectors or []:
                        if isinstance(selector, javalang.tree.MethodInvocation):
                            target = resolve(selector)
                            targets[target].append(caller_name)
                            external_calls += 1

                for field, _ in field_sites:
                    targets[field].append(caller_name)
                    external_fields += 1

    for row in rows:
        incoming = targets[row["name"]]
        if row["type"] == "Method":
            row["inner invocations"] = " ".join(
                call for call in incoming if "+" not in call
            )
            row["external invocations"] = " ".join(
                call for call in incoming if "+" in call
            )
        else:
            # Keep the already validated internal field visitors from version 2.
            row["external invocations"] = " ".join(
                call for call in incoming if "+" in call
            )

    with OUTPUT.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print("Version 4 written:", OUTPUT)
    print("Rows:", len(rows))
    print("Internal incoming call edges:", local_edges)
    print("External incoming method/constructor edges:", external_calls)
    print("External field access sites:", external_fields)
    print("WARNING: Outgoing calls/field bindings still need full symbol resolution.")


if __name__ == "__main__":
    main()
