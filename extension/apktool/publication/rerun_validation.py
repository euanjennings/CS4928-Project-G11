"""Run an unchanged archived diagnostic in a fresh temporary layout."""
import argparse
import importlib.util
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", choices=["initial", "members"], required=True)
    args = p.parse_args()
    work = Path(tempfile.mkdtemp(prefix="cs4928_validation_"))
    for name in ["apktool_input_extractor.py", "apktool_input_extractor_v2.py"]:
        shutil.copy2(HERE / "scripts_original" / name, work / name)
    for rel in ["results/event_a/source/Mapper_before.java", "upstream/dataset/refactor_example_position/13+MapperHelper+MapperTemplate.csv"]:
        dest = work / "CS4928-Project-G11" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    name = "mapper_validation.py" if args.version == "initial" else "mapper_validation_members_v2.py"
    spec = importlib.util.spec_from_file_location("diagnostic", HERE / "scripts_original" / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.locate_week9 = lambda: work
    module.main()
    print("Local output only; ignore the archived script's upload suggestion.")


if __name__ == "__main__":
    main()
