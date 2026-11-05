"""Create publication derivatives from the preserved private handover package.

Run from any directory. Refuses an existing destination. Original files are
never edited. Private inputs are intentionally excluded from the staging list.
The published derivatives suffice for verification; regeneration needs originals.
"""
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "handover_20261104"
DEST = HERE.parent / "publication"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    return data.decode("utf-8-sig")


def metric_copy(data):
    reader = csv.DictReader(io.StringIO(decode(data)))
    fields = reader.fieldnames
    rows = list(reader)
    for row in rows:
        path = row["file"].replace("\\", "/")
        match = re.search(r"(?:^|/)(brut\.[^/]+/.*)$", path)
        if not match:
            raise ValueError(f"Unrecognised source path: {path}")
        row["file"] = match.group(1)
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


def xml_copy(data):
    # Preserve every suite and testcase attribute except hostname. Remove only
    # environment properties and console streams, not failure/error/skip nodes.
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as original, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dest:
        for name in original.namelist():
            root = ET.fromstring(original.read(name))
            for element in root.iter():
                element.attrib.pop("hostname", None)
                for child in list(element):
                    if child.tag in {"properties", "system-out", "system-err"}:
                        element.remove(child)
            dest.writestr(name, ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return out.getvalue()


def main():
    DEST.mkdir(exist_ok=False)
    mapping = []
    roots = {"inputs", "scripts_original", "source", "verified", "ck_pristine_20261104", "ck_cleanup_20261104", "evidence"}
    singles = {"cleanup.patch", "historical_refactoring.patch", "verify_evidence.py", "rerun_validation.py", "rerun_exploratory.py", "run_ck_pair.py"}
    excluded = {"case_study_before_handover.md", "ck_rerun_manifest.json"}
    for path in sorted(SOURCE.rglob("*")):
        rel = path.relative_to(SOURCE)
        if not path.is_file() or "__pycache__" in rel.parts:
            continue
        if rel.parts[0] not in roots and rel.as_posix() not in singles:
            continue
        if path.name in excluded or path.name.startswith("build") or any(part in {"validation_initial", "validation_members"} for part in rel.parts):
            continue
        data = path.read_bytes()
        action = "byte-identical copy"
        result = data
        if path.name in {"class.csv", "method.csv"}:
            result = metric_copy(data)
            action = "file column made repository-relative; every other CSV value unchanged"
        elif path.suffix == ".zip":
            result = xml_copy(data)
            action = "XML hostname, properties and console streams removed; all test result attributes/nodes retained"
        elif path.name.startswith("apktool-") and path.suffix == ".log":
            text = decode(data).replace("\r\r\n", "\n").replace("\r\n", "\n")
            # javac's source warning wraps the long local project prefix.
            text = re.sub(r"Note: [A-Za-z]:.*?apktool-after-cleanup-study\\", "Note: <APKTOOL>/", text, flags=re.DOTALL)
            result = text.encode("utf-8")
            action = "UTF-16 decoded to UTF-8 with LF lines; javac local source-path prefix replaced by <APKTOOL>; build/test output retained"
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result)
        mapping.append({"path": rel.as_posix(), "original_sha256": sha(data), "published_sha256": sha(result), "transformation": action})
    original = (SOURCE / "ck_run_manifest.json").read_bytes()
    manifest = json.loads(original)
    manifest["jar_path"] = "<CK_JAR>"
    manifest["publication_note"] = "Commands use portable placeholders. Original CSV hashes retained separately; published hashes cover path-normalized derivatives."
    for name, run in manifest["runs"].items():
        run["command"] = ["java", "-jar", "<CK_JAR>", f"<{name.upper()}_JAVA>", "false", "0", "false", f"<OUTPUT_{name.upper()}>"]
        run["original_class_csv_sha256"] = run.pop("class_csv_sha256")
        run["published_class_csv_sha256"] = sha((DEST / f"ck_{name}_20261104/class.csv").read_bytes())
    data = json.dumps(manifest, indent=2).encode() + b"\n"
    (DEST / "ck_run_manifest.json").write_bytes(data)
    mapping.append({"path": "ck_run_manifest.json", "original_sha256": sha(original), "published_sha256": sha(data), "transformation": "absolute paths replaced by portable placeholders; original and derivative CSV hashes distinguished"})
    (DEST / "PUBLICATION_PROVENANCE.json").write_text(json.dumps({"date": "2026-11-05", "originals": "Retained locally in handover_20261104, excluded from publication", "files": mapping}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(mapping)} publication files without changing originals.")


if __name__ == "__main__":
    main()
