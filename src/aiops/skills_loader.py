# src/aiops/skills_loader.py

import os
from pathlib import Path
import frontmatter

SKILLS_DIR = Path(__file__).parent / "skills"

def load_skills():
    skills = {}
    for fname in os.listdir(SKILLS_DIR):
        if fname.endswith(".md"):
            path = os.path.join(SKILLS_DIR, fname)
            doc = frontmatter.load(path)
            skills[doc["name"]] = {
                "intents": doc.get("intents", []),
                "keywords": doc.get("keywords", []),
                "system_prompt": doc.content.strip()
            }
    return skills
