import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self, model: str, api_key_env: str = "OPENAI_API_KEY"):
        self.model = model
        key = os.getenv(api_key_env)
        if not key:
            raise RuntimeError(f"{api_key_env} not set in environment")
        self.client = OpenAI(api_key=key)

    def chat(self, messages, **kwargs):
        # DEBUG: print request content
        import json
        print("=== OpenAI Request ===")
        print(json.dumps(messages, indent=2))  # pretty-print the messages array
        print("=====================")

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return {"text": resp.choices[0].message.content}
