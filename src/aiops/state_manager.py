# src/aiops/state_manager.py

import json
import os
import time
from typing import Optional
from rich.console import Console


class StateManager:
    def __init__(self, storage_path: str = "./.aiops_workspace/.aiops_state.json"):
        self.storage_path = storage_path
        self.state = {
            "conversations": {},
            "current_conversation": None,
        }
        self._load()
        self.console = Console()

    # -----------------------------
    # Persistence
    # -----------------------------
    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.state = json.load(f)
            except Exception:
                self.console.print("⚠️ Failed to load state file, starting fresh.", style="red")
                self.state = {"conversations": {}, "current_conversation": None}
        else:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.state, f, indent=2)

    # -----------------------------
    # Conversation Management
    # -----------------------------
    def add_conversation(self, conv_id: str, title: str = "Untitled"):
        if conv_id not in self.state["conversations"]:
            self.state["conversations"][conv_id] = {
                "id": conv_id,
                "title": title,
                "created": time.time(),
                "messages": [],  # list of {role, content, ts, response_id?}
                "last_response_id": None,
            }
            self.set_current_conversation(conv_id)
            self._save()

    def set_current_conversation(self, conv_id: str):
        if conv_id in self.state["conversations"]:
            self.state["current_conversation"] = conv_id
            self._save()

    def get_current_conversation(self) -> Optional[str]:
        return self.state.get("current_conversation")

    def list_conversations(self):
        return self.state.get("conversations")

    def switch_conversation(self, conv_id: str) -> bool:
        if conv_id in self.state["conversations"]:
            self.state["current_conversation"] = conv_id
            self._save()
            return True
        return False

    def rename_conversation(self, conv_id: str, new_title: str):
        if conv_id in self.state["conversations"]:
            self.state["conversations"][conv_id]["title"] = new_title
            self._save()

    def clear_conversation(self, conv_id: str):
        if conv_id in self.state["conversations"]:
            self.state["conversations"][conv_id]["messages"] = []
            self.state["conversations"][conv_id]["last_response_id"] = None
            self._save()

    def delete_conversation(self, conv_id: str):
        if conv_id in self.state["conversations"]:
            del self.state["conversations"][conv_id]
            if self.state["current_conversation"] == conv_id:
                self.state["current_conversation"] = None
            self._save()

    # -----------------------------
    # Message Management
    # -----------------------------
    def add_message(
            self,
            conv_id: str,
            role: str,
            content: str,
            response_id: Optional[str] = None,
    ):
        if conv_id not in self.state["conversations"]:
            raise ValueError(f"Conversation {conv_id} not found in state.")

        msg = {
            "role": role,
            "content": content,
            "ts": time.time(),
        }
        if response_id:
            msg["response_id"] = response_id
            self.state["conversations"][conv_id]["last_response_id"] = response_id

        self.state["conversations"][conv_id]["messages"].append(msg)
        self._save()

    def update_conversation(
            self,
            conv_id: str,
            response_id: str,
            user_input: str,
            assistant_response: str,
    ):
        """
        Add both user and assistant messages to the conversation.
        """
        self.add_message(conv_id, "user", user_input)
        self.add_message(conv_id, "assistant", assistant_response, response_id)

    def get_history(self, conv_id: str, limit: int = 10):
        """
        Return the last `limit` messages of the given conversation.
        """
        conv = self.state["conversations"][conv_id]
        if not conv:
            return []

        return conv["messages"][-limit:]
