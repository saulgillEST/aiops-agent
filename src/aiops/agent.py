from aiops.skills import SKILLS

def select_skill(prompt: str):
    """
    Naive skill selection: keyword match in skill descriptions.
    """
    for name, meta in SKILLS.items():
        if any(k.lower() in prompt.lower() for k in [name, meta["description"]]):
            return meta
    return None

def plan_task(prompt: str):
    """
    Returns a plan dict with actions (skills to run) and summary.
    """
    skill = select_skill(prompt)
    if skill:
        return {
            "actions": [{"run": "skill", "cmd": skill["name"], "params": {}}],
            "summary": f"Selected skill: {skill['name']}"
        }
    return {"actions": [], "summary": "No matching skill found"}
