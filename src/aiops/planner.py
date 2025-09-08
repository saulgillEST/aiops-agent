import json
from typing import List, Dict

JSON_INSTRUCTIONS = """Respond ONLY as JSON with keys:
status (clarify|propose_script|revise_script|ready_to_run),
questions (list of strings),
script (string),
patch (string unified diff),
notes (string),
sources (list of strings).
"""

def build_messages(system_ctx: str, skill_ctx: str, docs_ctx: str, history: List[Dict], user_msg: str):
    msgs = [
        {"role": "system", "content": system_ctx + "\n" + JSON_INSTRUCTIONS},
        {"role": "system", "content": "SKILL CONTEXT:\n" + skill_ctx},
        {"role": "system", "content": "DOCS CONTEXT:\n" + docs_ctx},
    ]
    msgs.extend(history)
    msgs.append({"role": "user", "content": user_msg})
    return msgs

def parse_model_json(text: str):
    # tolerant parsing: extract first JSON object in text
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError('No JSON object found in model response')
    payload = text[start:end+1]
    return json.loads(payload)