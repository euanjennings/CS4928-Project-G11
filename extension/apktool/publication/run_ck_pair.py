"""Measure pristine 40d427e5 and the reviewed cleanup using one CK JAR.

Read-only git archive; no worktrees, index changes or changes to source checkouts.
Only tracked Java files are materialized, excluding generated build artifacts.
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--jar", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    repo, jar, out = args.repo.resolve(), args.jar.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cmd = ["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo)]
    commit = subprocess.check_output(cmd + ["rev-parse", "40d427e5"], text=True).strip()
    archive = subprocess.check_output(cmd + ["archive", "--format=zip", commit])
    temp = Path(tempfile.mkdtemp(prefix="cs4928_ck_"))
    target = "brut.apktool/apktool-lib/src/main/java/brut/androlib/res/AndrolibResources.java"
    field = b"    private File mFrameworkDirectory = null;\n\n"
    meta = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "commit": commit, "jar_sha256": digest(jar.read_bytes()), "scope": "all tracked Java files, main and test; no generated files", "use_jars": False, "partition": 0, "field_variable_csv": False, "ignored": ["CK default .git only"], "runs": {}}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for name in ("pristine", "cleanup"):
            hashes = {}
            for file in z.namelist():
                if not file.endswith(".java"):
                    continue
                data = z.read(file)
                if name == "cleanup" and file == target:
                    assert data.count(field) == 1
                    data = data.replace(field, b"", 1)
                dest = temp / name / file
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                hashes[file] = digest(data)
            dest = out / name
            dest.mkdir()
            command = ["java", "-jar", str(jar), str(temp/name), "false", "0", "false", str(dest)]
            run = subprocess.run(command, capture_output=True)
            (dest / "run.log").write_bytes(run.stdout + run.stderr)
            meta["runs"][name] = {"command": command, "exit_code": run.returncode, "source_sha256": hashes}
            if run.returncode:
                raise RuntimeError(f"CK {name} failed; inspect {dest / 'run.log'}")
            meta["runs"][name]["class_csv_sha256"] = digest((dest / "class.csv").read_bytes())
    (out / "manifest.json").write_text(json.dumps(meta, indent=2))
    print(out)


if __name__ == "__main__":
    main()
