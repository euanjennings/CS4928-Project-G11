"""Audit the proposed working-tree submission without touching the Git index.

Writes only submission lists/reports. Requires the private originals for full
derivative checks; the publication verifier independently works after cloning.
"""
import ast
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APK = HERE.parent
PUB = APK / "publication"
RAW = APK / "handover_20261104"
if not RAW.is_dir():
    RAW = ROOT.parent / "CS4928_Private_Archive_20261105" / "extension/apktool/handover_20261104"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=ROOT, env=ENV).decode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    return data.decode("utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")


def csv_values(data):
    return [{k: v for k, v in row.items() if k != "file"} for row in csv.DictReader(io.StringIO(decode(data)))]


def xml_result(data):
    root = ET.fromstring(data)
    for node in root.iter():
        node.attrib.pop("hostname", None)
        for child in list(node):
            if child.tag in {"system-out", "system-err", "properties"}:
                node.remove(child)
    return ET.tostring(root)


def main():
    index_hash = sha((ROOT / ".git/index").read_bytes())
    ai_hash = sha((ROOT / "docs/AI_USE.md").read_bytes())
    approved = {".gitattributes", "design/APKTOOL_CASE_STUDY.md", "docs/PREREGISTRATION.md", "docs/DEVIATIONS.md"}
    approved.update("extension/apktool/" + name for name in ["VALIDATION_REPORT.md", "GROUND_TRUTH_SENSITIVITY.md", "INDEPENDENT_CLEANUP_EXPERIMENT.md", "run_apktool.py", "apktool_classsplitter_candidate_v2.csv", "apktool_ground_truth.csv"])
    for folder in [PUB, APK / "results", APK / "results_v3", APK / "results_v4"]:
        approved.update(p.relative_to(ROOT).as_posix() for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    support = ["README.md", "prepare_publication.py", "audit_submission.py", "STAGE_PATHS.txt", "EXCLUDE_PATHS.tsv", "FILE_MANIFEST.json", "CHECKS.json", "LINK_CHECK.json", "PORTABLE_CHECK.json"]
    approved.update("extension/apktool/submission/" + name for name in support)
    (HERE / "STAGE_PATHS.txt").write_text("\n".join(sorted(approved)) + "\n", encoding="utf-8")
    excluded = []
    for p in sorted(RAW.rglob("*")):
        if p.is_file():
            reason = "Private original retained; submit curated publication derivative where applicable"
            if p.name.startswith("build"):
                reason = "Environment/build troubleshooting log; unnecessary for outcome verification"
            elif p.name.startswith(("initial_", "final_")) or p.name in {"local_paths.json", "safeguards.json", "tracker_extract.json", "manifest.json", "FINAL_VERIFICATION.json", "LOCAL_HANDOVER_PROGRESS.md"}:
                reason = "Local audit, paths, stale inventory or unrelated tracker data"
            elif "validation_initial" in p.parts or "validation_members" in p.parts:
                reason = "Duplicate diagnostic rerun; original diagnostic and agreement summary retained"
            excluded.append((("extension/apktool/handover_20261104/" + p.relative_to(RAW).as_posix()), reason))
    excluded += [(".github/workflows/apktool.yml", "Untracked workflow moved to sibling private archive; exclude from submission"), ("CODEX_HANDOVER_CS4928_G11_P04_2026-11-04.md", "Handover moved to sibling private archive; contains machine paths"), ("docs/AI_USE.md", "No edits authorized; existing tracked disclosure retained"), ("**/__pycache__/**; *.pyc; .venv*/**", "Generated interpreter/dependency files"), ("Temporary CK/Maven directories, complete review ZIP and CK JAR outside repository", "Local tools/archives, not a source submission")]
    (HERE / "EXCLUDE_PATHS.tsv").write_text("path\treason\n" + "\n".join("\t".join(row) for row in excluded) + "\n", encoding="utf-8")
    provenance = json.loads((PUB / "PUBLICATION_PROVENANCE.json").read_text())
    originals_available = RAW.is_dir()
    for item in provenance["files"]:
        data = (PUB / item["path"]).read_bytes()
        assert sha(data) == item["published_sha256"], item["path"]
        if not originals_available:
            continue
        original = (RAW / item["path"]).read_bytes()
        assert sha(original) == item["original_sha256"], item["path"]
        if item["path"].endswith(("class.csv", "method.csv")):
            assert csv_values(data) == csv_values(original)
        if item["path"].endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as a, zipfile.ZipFile(io.BytesIO(original)) as b:
                assert a.namelist() == b.namelist()
                for name in a.namelist():
                    assert xml_result(a.read(name)) == xml_result(b.read(name)), name
    privacy_hits = []
    for name in sorted(approved):
        path = ROOT / name
        if not path.exists():
            continue  # Reports created below have no machine-path payload.
        data = path.read_bytes()
        if path.suffix == ".zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                texts = [(n, decode(z.read(n))) for n in z.namelist()]
        else:
            texts = [("", decode(data))]
        for member, text in texts:
            if re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/(?:Users|home)/|hostname=[\"'](?![\"'])", text):
                privacy_hits.append({"file": name, "member": member})
        if path.suffix == ".py":
            ast.parse(decode(data))
    head = set(git("ls-tree", "-r", "--name-only", "HEAD").splitlines())
    projected = head | approved
    links = []
    for name in sorted(projected):
        if not name.endswith(".md") or not (ROOT / name).exists():
            continue
        text = (ROOT / name).read_text(encoding="utf-8-sig")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        targets = re.findall(r"\]\((<[^>]+>|(?:[^()\n]|\([^()]*\))+)\)", text)
        for target in targets:
            target = target.strip().strip("<>")
            if re.match(r"[a-zA-Z]+:", target) or target.startswith("//"):
                continue
            target, _, anchor = unquote(target).partition("#")
            dest = (ROOT / name).parent / target if target else ROOT / name
            try:
                rel = dest.resolve().relative_to(ROOT).as_posix()
            except ValueError:
                rel = "OUTSIDE_REPOSITORY"
            exists = rel in projected or any(p.startswith(rel.rstrip("/") + "/") for p in projected)
            anchor_ok = True
            if anchor and exists and rel.endswith(".md"):
                content = (ROOT / rel).read_text(encoding="utf-8-sig")
                headings = re.findall(r"^#{1,6}\s+(.+)$", content, flags=re.MULTILINE)
                slugs = {re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-") for heading in headings}
                anchor_ok = anchor in slugs or f'id="{anchor}"' in content
            links.append({"source": name, "target": target + ("#" + anchor if anchor else ""), "resolved": rel, "exists_in_proposed_commit": exists, "anchor_valid": anchor_ok, "upstream_import": name.startswith("upstream/")})
    failures = [x for x in links if not x["exists_in_proposed_commit"] or not x["anchor_valid"]]
    (HERE / "LINK_CHECK.json").write_text(json.dumps({"scope": "Relative Markdown links in projected committed Markdown files; external URL availability not tested", "links": links, "failures": failures}, indent=2) + "\n", encoding="utf-8")
    attributes = git("check-attr", "text", "--", "extension/apktool/publication/inputs/apktool_classsplitter_candidate_v4.csv", "extension/apktool/results_v4/comparison.json")
    assert all(line.endswith("text: unset") for line in attributes.splitlines())
    checks = {"date": "2026-11-05", "approved_files": len(approved), "publication_source_hashes_match": originals_available, "publication_derivative_hashes_match": True, "all_non_path_ck_values_unchanged": originals_available, "all_xml_result_nodes_unchanged": originals_available, "machine_path_findings": privacy_hits, "authored_link_failures": [x for x in failures if not x["upstream_import"]], "upstream_link_failures": [x for x in failures if x["upstream_import"]], "byte_preservation_attributes_verified": True, "index_unchanged": index_hash == sha((ROOT / ".git/index").read_bytes()), "ai_use_unchanged": ai_hash == sha((ROOT / "docs/AI_USE.md").read_bytes())}
    (HERE / "CHECKS.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    manifest = {n: {"bytes": (ROOT / n).stat().st_size, "sha256": sha((ROOT / n).read_bytes())} for n in sorted(approved) if not n.endswith("/FILE_MANIFEST.json")}
    (HERE / "FILE_MANIFEST.json").write_text(json.dumps({"note": "Working-tree bytes, preserved by scoped attributes for Apktool files; manifest excludes itself", "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
