from pathlib import Path
import csv
import subprocess
import javalang

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "apktool-study"

JAVA_PATH = (
    "brut.apktool/apktool-lib/src/main/java/"
    "brut/androlib/res/"
)

BEFORE = "9c495cae"
AFTER = "40d427e5"


def load_class(commit, filename, class_name):
    result = subprocess.run(
        [
            "git", "-C", str(REPO),
            "show", f"{commit}:{JAVA_PATH}{filename}"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )

    tree = javalang.parse.parse(result.stdout)

    return next(
        item for item in tree.types
        if item.name == class_name
    )


def parameter_type(parameter):
    node = parameter.type

    while getattr(node, "sub_type", None) is not None:
        node = node.sub_type

    name = node.name.split(".")[-1]
    dimensions = "[]" * len(parameter.type.dimensions or [])

    return name + dimensions + (
        "..." if parameter.varargs else ""
    )


def method_signature(method):
    parameters = ",".join(
        parameter_type(p) for p in method.parameters
    )

    return f"{method.name}({parameters})"


def get_members(java_class):
    members = []

    for item in java_class.body:
        line = item.position.line if item.position else ""

        if isinstance(item, javalang.tree.FieldDeclaration):
            for field in item.declarators:
                members.append({
                    "type": "Field",
                    "name": field.name,
                    "line": line,
                })

        elif isinstance(item, javalang.tree.MethodDeclaration):
            members.append({
                "type": "Method",
                "name": method_signature(item),
                "line": line,
            })

        elif isinstance(item, javalang.tree.ConstructorDeclaration):
            members.append({
                "type": "Constructor",
                "name": method_signature(item),
                "line": line,
            })

    return members


def main():
    before = get_members(
        load_class(
            BEFORE,
            "AndrolibResources.java",
            "AndrolibResources",
        )
    )

    after_original = get_members(
        load_class(
            AFTER,
            "AndrolibResources.java",
            "AndrolibResources",
        )
    )

    after_framework = get_members(
        load_class(
            AFTER,
            "Framework.java",
            "Framework",
        )
    )

    remaining_methods = {
        row["name"]
        for row in after_original
        if row["type"] == "Method"
    }

    framework_methods = {
        row["name"]
        for row in after_framework
        if row["type"] == "Method"
    }

    moved_methods = {
        row["name"]
        for row in before
        if row["type"] == "Method"
        and row["name"] not in remaining_methods
    }

    # Verify the extracted methods match the new class.
    if moved_methods != framework_methods:
        raise ValueError(
            "Method mapping mismatch. "
            f"Moved: {sorted(moved_methods)}; "
            f"Framework: {sorted(framework_methods)}"
        )

    if len(moved_methods) != 10:
        raise ValueError(
            f"Expected 10 moved methods, found {len(moved_methods)}"
        )

    original_fields = {
        row["name"]
        for row in before
        if row["type"] == "Field"
    }

    remaining_fields = {
        row["name"]
        for row in after_original
        if row["type"] == "Field"
    }

    if original_fields != remaining_fields:
        raise ValueError("Original field mapping has changed")

    output = ROOT / "apktool_ground_truth.csv"

    if output.exists():
        raise FileExistsError(
            f"{output} already exists. It will not be overwritten."
        )

    with output.open(
        "x", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "index",
            "name",
            "type",
            "line",
            "removed",
        ])

        for index, member in enumerate(before, start=1):
            removed = (
                member["type"] == "Method"
                and member["name"] in moved_methods
            )

            writer.writerow([
                index,
                member["name"],
                member["type"],
                member["line"],
                removed,
            ])

    print("Original members:", len(before))
    print("Extracted methods:", len(moved_methods))
    print("Extracted fields:", len(original_fields - remaining_fields))
    print("Ground-truth file:", output)

    print("\nExtracted method signatures:")
    for name in sorted(moved_methods):
        print("-", name)


if __name__ == "__main__":
    main()