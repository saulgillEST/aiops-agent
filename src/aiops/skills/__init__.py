import importlib
import pathlib

SKILLS = {}

skills_path = pathlib.Path(__file__).parent
for f in skills_path.glob("*.py"):
    if f.name == "__init__.py":
        continue
    mod = importlib.import_module(f".{f.stem}", package="aiops.skills")
    if hasattr(mod, "skill"):
        SKILLS[mod.skill["name"]] = mod.skill
