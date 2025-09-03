# AI Ops Agent 🛠️🤖

A prompt-driven terminal AI agent that installs **Nephio R5** and **O-RAN** components (and more in the future).  
It uses your own LLM API key (OpenAI, Anthropic, etc.), asks clarifying questions, and safely executes commands.

## Features
- CLI interface (`aiops`)
- Secure config in `~/.config/aiops/config.yaml`
- Dry-run mode & confirmations
- Pluggable "skills" (installers for Nephio, O-RAN, etc.)
- Open source & extensible

## Install
```bash
git clone https://github.com/YOURNAME/aiops-agent.git
cd aiops-agent
pip install -e .
```
## Usage

```bash
# Login with your own LLM key
aiops login --provider openai --model gpt-4o-mini --env-var OPENAI_API_KEY

# Dry-run install plan
aiops install "Install Nephio R5 and O-RAN components" --dry-run

# Execute interactively
aiops install "Install Nephio R5 and O-RAN components"
```