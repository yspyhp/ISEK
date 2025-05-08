# Fast Create Agent
Here we show you how to quickly build your agent through ISEK. You can build a single agent or a distributed agent according to your needs.

---

## 📦 Installation

```bash
  pip install isek
```

---

## 🚀 Start Your Single Agent

### 1. Set Your API Environment

Create a `.env` file at the root:

```env
OPENAI_MODEL_NAME=your_model_name
OPENAI_BASE_URL=your_base_url
OPENAI_API_KEY=your_api_key
```

### 2. Try different startup methods

#### Start with default configuration

```bash
  python create_single_agent_demo.py fast_create
```

#### Start the agent and customize your own LLM

```bash
  python create_single_agent_demo.py statement_llm_create
```

#### Fully customize and start the agent

```bash
  python create_single_agent_demo.py custom_create
```

---

## 🌐 Start Your Distributed Agent

### 1. Set Your API Environment

Create a `.env` file at the root:

```env
OPENAI_MODEL_NAME=your_model_name
OPENAI_BASE_URL=your_base_url
OPENAI_API_KEY=your_api_key
```

### 2. Start the Local Registry

```bash
  isek registry
```

### 3. Try different startup methods

#### Start with default configuration

```bash
  python create_distributed_agent_demo.py fast_create
```

#### Start the agent and customize your own LLM

```bash
  python create_distributed_agent_demo.py statement_llm_create
```

#### Fully customize and start the agent

```bash
  python create_distributed_agent_demo.py custom_create
```
