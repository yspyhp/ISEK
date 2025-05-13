# Isek: Decentralized Agent-to-Agent (A2A) Network

> **Building the Internet of Agents**

**Isek** is a decentralized agent network framework designed for building intelligent, collaborative agent-to-agent (A2A) systems. Agents in Isek autonomously discover peers, share context, and cooperatively solve tasks, forming a self-organizing, decentralized society.

With native integration of large language models (LLMs) and a user-friendly CLI, Isek empowers developers and researchers to quickly prototype, deploy, and manage intelligent agent networks.

> 🧪 **ISEK is under active development.** Contributions, feedback, and experiments are highly welcome.

---

## 🌟 Key Features

* **Decentralized Cooperation:**
  Autonomous agent discovery and direct agent-to-agent collaboration without central points of failure.

* **Distributed Deployment:**
  Deploy agents seamlessly across multiple nodes or cloud environments for scalability and resilience.

* **LLM-Enhanced Intelligence:**
  Built-in integration with models like OpenAI for enhanced reasoning, planning, and natural language interactions.

* **Modular and Extensible:**
  Easy to customize, integrate new models, and extend functionalities.

* **Developer-Friendly CLI:**
  Simplified CLI for easy agent setup and management with minimal friction.

---

## 📦 Installation

```bash
pip install isek
```

> Requires **Python 3.8+**

---

## 🚀 Quick Start

### 1. Set Up Environment

Create a `.env` file:

```env
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

### 2. Start Registry

```bash
isek registry
```

### 3. Launch Agent

```python
from dotenv import load_dotenv
from isek.agent.distributed_agent import DistributedAgent

load_dotenv()
agent = DistributedAgent()
agent.build(daemon=True)
agent.run_cli()
```

Interact with your decentralized agent directly from your terminal.

---

## 🧪 CLI Commands

```bash
isek clean       # Clean temporary files
isek --help      # View available commands
```

---

## Project Structure

```
isek/
├── examples                   # Demonstration scripts for using the Isek framework
├── isek                       # Core modules and logic
│   ├── agent                  # Agent-related functionalities
│   ├── constant               # Project-wide constants
│   ├── embedding              # Embedding-related functionalities
│   ├── node                   # Node management functionalities
│   ├── llm                    # LLM integrations
│   ├── util                   # Utility and helper functions
│   ├── cli.py                 # Command-line interface
│   ├── isek_config.py         # Main configuration file
│   └── isek_center.py         # Central orchestrator (local registry)
├── script                     # Utility scripts (e.g., clean.py)
├── pyproject.toml             # Build and project configuration
└── README.md                  # Project documentation
```

---

## Configuration

Main configurations are managed via:

- **`isek/default_config.yaml`**: Default settings for quick deployments.

---

## 🤝 Contributing

We welcome collaborators, researchers, and early adopters.
Please see our [Contribution Guidelines](CONTRIBUTION.md).
- 💬 Open issues or ideas via GitHub
- 📧 Contact us: [team@isek.xyz](mailto:team@isek.xyz)

---

## 📜 License

Licensed under [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br>
  <em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>

