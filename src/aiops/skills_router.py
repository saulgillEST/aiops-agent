# src/aiops/skills_router.py
import json
from .llm.openai_client import OpenAIClient

class SkillRouter:
    def __init__(self, client: OpenAIClient, skills: dict):
        self.client = client
        self.skills = skills

    def _make_skill_summaries(self):
        summaries = []
        for name, skill in self.skills.items():
            summaries.append({
                "name": name,
                "description": skill.get("description", ""),
                "intents": skill.get("intents", []),
            })
        return summaries

    def select_skills(self, user_input: str) -> list[str]:
        summaries = self._make_skill_summaries()

        router_prompt = f"""
You are a skill router. 
Given the user request and the available skills, choose the most relevant skill(s) by name. 
Return only a JSON array of skill names. 

User request: "{user_input}"

Available skills:
{json.dumps(summaries, indent=2)}
"""
        response = self.client.ask_router(router_prompt)

        try:
            skill_names = json.loads(response)
            return [s for s in skill_names if s in self.skills]
        except Exception:
            return []
