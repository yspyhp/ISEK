# Configuration

Isek uses a YAML-based configuration system and a `.env` file to simplify setup and deployment. Through these configurations, you control core behaviors, models, networking, logging, agent-specific settings, and sensitive credentials like API keys.

## Basic Structure

An Isek configuration typically includes:

* **Agent settings** (`agent`)
* **Distributed mode settings** (`distributed`)
* **LLM and Embedding model configurations** (`llm`, `embedding`)
* **Registry settings** for agent discovery (`registry`)
* **Environment variables** (`.env`) for sensitive information

## Example YAML

.. code-block:: yaml

```
agent:
  debug: true
  persona_path: "path/to/persona.yml"

distributed: true

distributed.server:
  host: "localhost"
  port: 8080

llm: "openai"
llm.openai:
  api_key: "${OPENAI_API_KEY}"
  model_name: "gpt-4o"

embedding: "openai"
embedding.openai:
  api_key: "${OPENAI_API_KEY}"
  model_name: "text-embedding-3-small"

registry: "etcd"
registry.etcd:
  host: "127.0.0.1"
  port: 2379
```

## Example `.env` File

Store sensitive credentials safely in a `.env` file:

.. code-block:: ini

```
OPENAI_API_KEY=your-openai-api-key
```

## Agent Configuration

The `agent` section defines basic behaviors:

* `debug`: Enables detailed logging if set to `true`.
* `persona_path`: Specifies the file path to load your agent's persona definition.

## Distributed Mode

Enable or disable distributed mode:

* `distributed`: Set `true` for network-enabled agents; `false` for single, local agents.
* `distributed.server`: Defines the host and port your agent listens to.

## LLM and Embeddings

Specify your language model (LLM) and embedding model:

* **LLM settings** (`llm`): Define the backend model (e.g., OpenAI) and required parameters.
* **Embedding settings** (`embedding`): Similar to LLM, specifies the embedding service and parameters.

## Registry Configuration

The registry is used by distributed agents for peer discovery:

* Set `registry` to either `"etcd"` (production-grade distributed registry) or `"isek_center"` (simple demo registry).

## Example Usage in Python

Load your configuration and initialize an agent:

.. code-block:: python

```
from isek.config import IsekConfig

config = IsekConfig("path/to/config.yml")
agent = config.load_agent()

agent.run("What is today's task?")
```

## Best Practices

* Always store sensitive information, such as API keys, in a secure `.env` file.
* Reference environment variables in your YAML configuration using the `${VARIABLE_NAME}` syntax.
* Keep persona definitions and model configurations organized in separate, easily manageable files.
* Enable debug mode during development for detailed logging.
