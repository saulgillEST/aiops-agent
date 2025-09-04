# 🛠️ AIOps Agent

**AIOps Agent** is an open-source, prompt-driven automation assistant for installing and managing projects like **Nephio** and **O-RAN**.

It uses [OpenAI’s API](https://platform.openai.com/) and a skill-based architecture to:

- Clone GitHub repos
- Parse READMEs or install docs
- Generate **safe, idempotent Bash scripts** for Ubuntu
- Run those scripts and report **success or failure**
- Suggest **troubleshooting steps** if something goes wrong
- Interactively ask for **next tasks**

---

## 🚀 Features
- 🧩 **Skill-based**: easy to add new installation “skills” for other projects.
- 📂 **Repo-driven installs**: point at a repo + relative README path.
- 🤖 **LLM-powered**: scripts and troubleshooting suggestions come from GPT models.
- 🖥️ **Interactive CLI**: guides you step-by-step, asking what to do next.

---

## 📦 Installation

Clone and install locally in editable mode:

```bash
git clone https://github.com/yourname/aiops-agent.git
cd aiops-agent
pip install -e .
```

---

## 🔑 Configuration

Set your **OpenAI API key** as an environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Alternatively, place it in a `.env` file and load it with `dotenv`.

---

## 🖥️ Usage

The CLI command is `aiops`.

### Install from a repo

```bash
aiops install "Install Nephio R5 components"
```

---

## ⚡ Quickstart Example

Example session installing from a repo:

```
$ aiops install "Install Nephio R5 release components"

📥 Cloning https://github.com/example/nephio.git
Generated script saved at ./nephio/install.sh

Do you want to execute this script now? [y/N]: y

# (script output here)

✅ Task completed successfully!
What would you like me to do next? > Configure Nephio plugins
```

If a script fails:

```
❌ Installation failed.
🔍 Analyzing logs...
💡 Suggested troubleshooting steps:
- Check if Docker is installed and running
- Ensure you have kubectl installed
- Run 'minikube start' before retrying

Do you want to retry, skip, or provide a manual instruction? > retry
```

---

## 🧩 Adding New Skills

Skills live in [`aiops/skills/`](aiops/skills/).  
Each skill is a Python file with a `skill` dictionary:

```python
skill = {
    "name": "install_from_repo",
    "description": "Clone a repo, parse README, generate/run install script",
    "parameters": {
        "repo_url": "GitHub repository URL",
        "ref": "Branch or tag (default: main)",
        "readme_rel_path": "Relative path to README"
    },
    "entrypoint": run
}
```

Add your file to the `skills/` folder and it will be auto-discovered.

---

## 🛠️ Development

Run from source:

```bash
python cli.py install "Install O-RAN components"
```

Run tests (if you add them):

```bash
pytest
```

---

## 📜 License

MIT License.  
Feel free to fork, extend, and contribute.

---

## 🤝 Contributing

Pull requests are welcome!  
If you’d like to add new skills, please follow the `skill` format in `aiops/skills/`.