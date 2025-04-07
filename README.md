
# Isek: Distributed Cooperative-Autonomous Multi-Agent Framework

**Isek** is a lightweight, modular, and distributed multi-agent framework built for the next generation of **cooperative autonomous systems**. Agents in Isek aren’t just isolated functions — they form a **decentralized society**, discovering peers, sharing context, and collaboratively solving complex tasks across nodes.

With built-in LLM integration and an intuitive CLI, Isek is ideal for researchers, developers, and builders designing intelligent, collaborative agents in distributed environments.

> 🧪 **Isek is under active development** — your feedback, experiments, and contributions are highly welcome.

---

## Key Features

- **Cooperative Autonomy:**
  Agents autonomously discover suitable peers in the network, communicate, and collaborate to complete tasks in a decentralized fashion.

- **Distributed Agent Orchestration:**
  Spin up and manage intelligent agents across multiple nodes with flexible task assignment and coordination..

- **LLM Integration:**
  Built-in support for integrating Large Language Models such as OpenAI, enabling advanced NLP functionalities.

- **Modular Design:**
  Highly modular architecture ensures ease of maintenance, scalability, and flexibility for customization.

- **Lightweight and User-Friendly:**
  Designed for easy adoption, providing a streamlined user experience without complex setup or heavy dependencies.

---

## 📦 Installation

```bash
pip install isek
```

**Python 3.8+** is required.

---

## 🚀 Quick Start

### 1. Set Your API Environment

Create a `.env` file at the root:

```env
OPENAI_MODEL_NAME=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

### 2. Start the Local Registry

```bash
isek registry
```

This launches a local orchestrator to manage distributed agents.

### 3. Explore the Examples

List available examples:

```bash
isek example list
```

Run a demo:

```bash
isek example run distributed_agent_demo
```

---

## 🧪 CLI Usage

Clean up configs and temp files:

```bash
isek clean
```

Show all available commands:

```bash
isek --help
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

## Testing

Tests are included and managed with `pytest`. To run tests:

```bash
hatch run pytest
```

Ensure tests cover new code submissions to maintain high-quality standards.

---

## 🤝 Contributing

We welcome collaborators, researchers, and early adopters.

- 💬 Open issues or ideas via GitHub
- 📧 Contact us: [team@isek.xyz](mailto:team@isek.xyz)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🌱 What’s Next?

- 🔄 Real-time P2P agent messaging  
- 🧭 Adaptive role assignment based on peer context  
- 🌐 Decentralized discovery protocol  
- 🧰 GUI Dashboard for agent orchestration  

Stay tuned — and help shape the future of distributed autonomous systems.

---

<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br>
  <em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>

