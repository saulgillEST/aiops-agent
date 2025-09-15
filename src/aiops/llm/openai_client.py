# src/aiops/llm/openai_client.py

from typing import Optional
import openai
from rich.console import Console


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.console = Console()

    # -----------------------------
    # Conversation Management
    # -----------------------------
    def create_conversation(self) -> str:
        """Create a new conversation on OpenAI and return its ID."""
        conv = self.client.conversations.create()
        return conv.id

    def delete_conversation(self, conv_id: str):
        """Delete a conversation by ID."""
        try:
            self.client.conversations.delete(conv_id)
            return True
        except Exception as e:
            self.console.print(f"⚠️ Failed to delete OpenAI conversation {conv_id}: {e}", style="red")
            return False


    def send_message(
            self,
            conversation_id: str,
            user_input: str,
            system_prompts: Optional[list[str]] = None,
            previous_response_id: Optional[str] = None,
    ):
        """
        Send a message into a conversation and return (response_text, response_id).
        """
        input_content = []

        # Add system prompts (skills)
        if system_prompts:
            for sp in system_prompts:
                input_content.append({"role": "system", "content": sp})

        # Add user input
        input_content.append({"role": "user", "content": user_input})

        # Build request params
        params = {
            "model": self.model,
            "input": input_content,
        }
        if conversation_id and not previous_response_id:
            params["conversation"] = conversation_id
        elif previous_response_id and not conversation_id:
            params["previous_response_id"] = previous_response_id
        else:
            # Ensure we don't send both at once (mutually exclusive)
            raise ValueError(
                "You must provide either a conversation_id or a previous_response_id, not both."
            )

        # Call API
        resp = self.client.responses.create(**params)

        # Extract assistant response
        try:
            text = resp.output[0].content[0].text
        except Exception:
            text = "(no response)"

        return text, resp.id

    # -----------------------------
    # Router (stateless skill selection)
    # -----------------------------
    def ask_router(self, router_prompt: str) -> str:
        """
        Ask a lightweight stateless question for skill routing.
        Returns plain text, expected to be JSON array.
        """
        resp = self.client.responses.create(
            model=self.model,
            input=[{"role": "user", "content": router_prompt}],
        )

        try:
            # TODO: Json parse and validate?
            return resp.output[0].content[0].text.strip("`\njson")
        except Exception:
            return "[]"
