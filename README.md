
# Isek: Distributed Multi-Agent Framework

Isek is a robust, lightweight, and highly scalable distributed multi-agent framework specifically engineered to streamline the coordination, collaboration, and autonomous operation of intelligent agents across distributed environments. Featuring seamless integration with large language models (LLMs), flexible node operations, and easy-to-use command-line interactions, Isek empowers efficient and scalable multi-agent orchestration through cooperative autonomy.

---

## Key Features

- **Multi-Agent Management:**
  Easily deploy and manage intelligent agents to perform complex distributed tasks efficiently.

- **Cooperative Autonomy:**
  Enables intelligent agents to autonomously collaborate, communicate, and make coordinated decisions in distributed scenarios.

- **LLM Integration:**
  Built-in support for integrating Large Language Models such as OpenAI, enabling advanced NLP functionalities.

- **Modular Design:**
  Highly modular architecture ensures ease of maintenance, scalability, and flexibility for customization.

- **Lightweight and User-Friendly:**
  Designed for easy adoption, providing a streamlined user experience without complex setup or heavy dependencies.

---

## Installation

### Prerequisites

- Python >= 3.8
- [Hatch](https://hatch.pypa.io/) (recommended)

### Local Installation


Dependencies are specified in `pyproject.toml`. To install all project dependencies:

```bash
pip install -e .
```

---

## Get Started

Before running examples or other tasks, first configure your API key in a `.env` file:

```bash
OPENAI_MODEL_NAME=your_model_name_here
OPENAI_BASE_URL=your_base_url_here
OPENAI_API_KEY=your_api_key_here
```

Then start the local registry:

```bash
isek registry
```

Next, execute example scripts:

List available examples:

```bash
isek example list
```

Run a specific example:

```bash
isek example run <example_name>

isek example run distributed_agent_demo
```

---

## Usage

Isek provides straightforward CLI commands to manage your distributed agent tasks:

- **System Cleanup**

Run the cleanup script to clear temporary files or reset configurations:

```bash
isek clean
```

Use the following command for detailed help:

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

## Contributing

Community contributions are welcomed!

- Submit suggestions or issues via the GitHub repository.
- Email the Isek Team directly at [sparks@isek.xyz](mailto:sparks@isek.xyz).

---

## License

This project is open-sourced under the [MIT License](LICENSE).
