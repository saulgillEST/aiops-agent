# src/aiops/orchestrator.py

import sys
from pyexpat.errors import messages

from datetime import datetime
from rich.console import Console
from rich.table import Table
from .skills_loader import load_skills
from .skills_router import SkillRouter
import readline


class Orchestrator:
    def __init__(self, client, state_manager):
        self.client = client
        self.state_manager = state_manager
        self.skills = load_skills()
        self.router = SkillRouter(client, self.skills)
        self.console = Console()

    def start(self):
        """Start the interactive CLI loop."""
        self.console.print("🤖 AIOps Agent started. Type 'help' for commands.", style="green")

        while True:
            try:
                user_input = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n👋 Goodbye!", style="green")
                sys.exit(0)

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                self.console.print("👋 Exiting.", style="green")
                break
            elif user_input.lower() == "help":
                self.print_help()
                continue
            elif user_input.lower() == "list":
                self.list_conversations()
                continue
            elif user_input.lower() == "status":
                self.show_status()
                continue
            elif user_input.startswith("new "):
                _, title = user_input.split(" ", 1)
                self.new_conversation(title)
                continue
            elif user_input.startswith("switch "):
                _, conv_id = user_input.split(" ", 1)
                self.switch_conversation(conv_id)
                continue
            elif user_input.startswith("title "):
                _, new_title = user_input.split(" ", 1)
                self.rename_conversation(new_title)
                continue
            elif user_input.startswith("delete "):
                _, conv_id = user_input.split(" ", 1)
                self.delete_conversation(conv_id)
                continue
            elif user_input.lower() == "clear":
                self.clear_conversation()
                continue
            elif user_input.lower() == "history":
                self.history()
                continue

            # Otherwise, treat it as a user query
            self.handle_user_input(user_input)

    def print_help(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Command", justify="left")
        table.add_column("Description", style="cyan")

        table.add_row("help", "Show this help message")
        table.add_row("list", "List all conversations")
        table.add_row("status", "Show current active conversation")
        table.add_row("switch <id>", "Switch to another conversation")
        table.add_row("title <name>", "Rename current conversation")
        table.add_row("delete <id>", "Delete a conversation")
        table.add_row("clear", "Clear current conversation history")
        table.add_row("history", "Show last 10 messages in current conversation")
        table.add_row("exit", "Quit the application")
        self.console.print(table)

    def list_conversations(self):
        """
        Nicely list local conversations in a Rich table.
        Shows Active marker, local id, title, created time, #messages and last response id.
        """

        convs = self.state_manager.list_conversations()  # expected: dict {conv_id: meta, ...}

        if not convs:
            self.console.print("📭 No conversations yet. Create one with 'new <title>'.", style="yellow")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Active", width=6, justify="center")
        table.add_column("Local ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Created", style="green", width=20)
        table.add_column("#Msgs", justify="right")
        table.add_column("LastResp", style="yellow", no_wrap=True)

        active_id = self.state_manager.get_current_conversation()

        for cid, meta in convs.items():
            if meta is None:
                meta = {}

            # ⭐ active marker
            active_marker = "⭐" if cid == active_id else ""

            # Local ID
            local_id = str(cid)

            # Title
            title = meta.get("title") or "Untitled"

            # Created
            created = meta.get("created") or meta.get("created_at") or ""
            if isinstance(created, (int, float)):
                try:
                    created_s = datetime.fromtimestamp(float(created)).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    created_s = str(created)
            else:
                created_s = str(created)[:19] if created else ""

            # Number of messages
            messages = meta.get("messages") or []
            msg_count = len(messages) if isinstance(messages, (list, tuple)) else 0

            # Last response id
            last_resp = meta.get("last_response_id") or ""
            last_resp_short = (last_resp[:12] + "...") if last_resp and len(last_resp) > 15 else last_resp

            table.add_row(active_marker, local_id, title, created_s, str(msg_count), last_resp_short)

        self.console.print(table)

    def new_conversation(self, title="Untitled"):
        conv_id = self.client.create_conversation()
        self.state_manager.add_conversation(conv_id, title)
        self.state_manager.set_current_conversation(conv_id)
        self.console.print(f"✨ Created new conversation [{conv_id}] with title: '{title}'", style="green")

    def switch_conversation(self, conv_id):
        if self.state_manager.switch_conversation(conv_id):
            self.console.print(f"🔄  Switched to conversation {conv_id}", style="green")
        else:
            self.console.print(f"⚠️  Conversation {conv_id} not found.", style="red")

    def rename_conversation(self, new_title):
        conv_id = self.state_manager.get_current_conversation()
        if conv_id:
            self.state_manager.rename_conversation(conv_id, new_title)
            self.console.print(f"✏️ Renamed conversation {conv_id} → {new_title}", style="green")
        else:
            self.console.print("⚠️ No active conversation.", style="red")

    def delete_conversation(self, conv_id):
        if self.client.delete_conversation(conv_id):
            self.state_manager.delete_conversation(conv_id)
            self.console.print(f"🗑️ Deleted conversation {conv_id}", style="green")
        else:
            self.console.print(f"⚠️ Failed to delete conversation {conv_id} from OpenAI.", style="red")

    def history(self, limit=10):
        conv_id = self.state_manager.get_current_conversation()
        if conv_id:
            messages = self.state_manager.get_history(conv_id, limit)
            table = Table(title=f"History (last {limit})", show_lines=True)
            table.add_column("Role", style="cyan", width=12)
            table.add_column("Content", style="white")

            for msg in messages:
                table.add_row(msg["role"], msg["content"])

            self.console.print(table)
        else:
            self.console.print("⚠️ No active conversation to get history from.", style="red")

    def clear_conversation(self):
        conv_id = self.state_manager.get_current_conversation()
        if conv_id:
            self.state_manager.clear_conversation(conv_id)
            self.console.print(f"🧹 Cleared conversation {conv_id}", style="green")
        else:
            self.console.print("⚠️ No active conversation.", style="red")

    def show_status(self):
        conv_id = self.state_manager.get_current_conversation()
        if not conv_id:
            self.console.print("⚠️ No active conversation.", style="red")
            return
        conversations = self.state_manager.list_conversations()
        title = conversations.get(conv_id, {}).get("title", "Untitled")
        self.console.print(f"🟢 Active conversation: {conv_id} - {title}", style="green")

    def handle_user_input(self, user_input: str):
        """Route the user input to skills, send to OpenAI, and handle response."""

        # 1. Route to skills using AI
        chosen_skills = self.router.select_skills(user_input)
        if not chosen_skills:
            self.console.print("⚠️ No matching skills found. Proceeding with just user input.", style="yellow")
            system_prompts = None
        else:
            # 2. Collect system prompts
            system_prompts = [self.skills[name]["system_prompt"] for name in chosen_skills]

        # 3. Ensure a conversation exists
        conv_id = self.state_manager.get_current_conversation()
        if not conv_id:
            conv_id = self.client.create_conversation()
            self.state_manager.add_conversation(conv_id, title="Untitled")
            self.state_manager.set_current_conversation(conv_id)

        # 4. Get last response_id if conversation already has messages
        conv_meta = self.state_manager.list_conversations().get(conv_id, {})
        prev_resp_id = conv_meta.get("last_response_id")

        # 5. Send message to OpenAI
        response, resp_id = self.client.send_message(
            conversation_id=conv_id if not prev_resp_id else None,
            previous_response_id=prev_resp_id if prev_resp_id else None,
            user_input=user_input,
            system_prompts=system_prompts,
        )

        # 6. Save both user and assistant messages locally
        self.state_manager.update_conversation(
            conv_id, resp_id, user_input, response
        )

        # 7. Show response
        self.console.print(f"\n🤖 {response}\n", style="bold white")
