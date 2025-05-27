
<!-- Banner Image -->
<p align="center">
  <img src="assets/banner_cn.png" alt="Isek Banner" width="100%" />
</p>

<h1 align="center">Isek：去中心化的 Agent-to-Agent (A2A) 网络</h1>

<p align="center">
  <a href="https://pypi.org/project/isek/"><img src="https://img.shields.io/pypi/v/isek" alt="PyPI 版本" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="许可证：MIT" /></a>
  <a href="mailto:team@isek.xyz"><img src="https://img.shields.io/badge/contact-team@isek.xyz-blue" alt="邮箱" /></a>
</p>

<h4 align="center">
    <a href="README.md">English</a> |
    <a href="README_CN.md">中文</a>
</h4>

---

**Isek** 是一个用于构建智能、协作的 Agent-to-Agent (A2A) 系统的去中心化Agent网络框架。Isek 中的Agent能够自主发现其他节点、共享上下文并协同完成任务，形成一个自组织的去中心化网络。

Isek 原生集成大型语言模型（LLM）和易用的 CLI，帮助开发者和研究人员快速原型开发、部署并管理智能体网络。

> 🧪 **ISEK 正在积极开发中。** 欢迎贡献代码、反馈建议及实验。

---

## 🌟 功能亮点

- **🧠 去中心化协作：**  
  无单点故障的自动节点发现与其他Agent协作。

- **🌐 分布式部署：**  
  支持多节点或云端部署，具备可扩展性与鲁棒性。

- **🗣️ LLM 加持智能：**  
  内建支持 OpenAI 等模型，便于自然交互与推理。

- **🔌 模块化易扩展：**  
  可轻松自定义Agent、集成新模型或扩展功能。

- **💻 开发者友好 CLI：**  
  简洁命令行界面，轻松配置与控制Agent。

---

## 📦 安装方式

```bash
pip install isek
```

> 依赖 **Python 3.9+**

---

## 🚀 快速开始

### 1️⃣ 设置环境变量

创建 `.env` 文件：

```env
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

### 2️⃣ 启动注册中心

```bash
isek registry
```

### 3️⃣ 启动Agent

```python
from dotenv import load_dotenv
from isek.agent.distributed_agent import DistributedAgent

load_dotenv()
agent = DistributedAgent()
agent.build(daemon=True)
agent.run_cli()
```

你现在可以在终端中与去中心化Agent交互了！

---

## 🧪 CLI 命令

```bash
isek clean       # 清理临时文件
isek --help      # 查看可用命令
```

---

## 🧱 项目结构

```
isek/
├── examples                   # 示例脚本
├── isek                       # 核心功能模块
│   ├── agent                  # Agent逻辑
│   ├── constant               # 常量定义
│   ├── embedding              # 向量嵌入模块
│   ├── node                   # 节点编排
│   ├── llm                    # LLM 接口
│   ├── util                   # 工具函数
│   ├── cli.py                 # CLI 入口
│   ├── isek_config.py         # 配置管理
│   └── isek_center.py         # 本地注册协调器
├── script                     # 工具脚本（如 clean.py）
├── pyproject.toml             # 构建与依赖配置
└── README.md                  # 项目总览与文档
```

---

## ⚙️ 配置说明

主要配置文件：

- `isek/default_config.yaml`：内建默认配置，方便快速部署。

---

## 🤝 贡献方式

我们欢迎合作者、研究人员与早期用户！

- 💬 通过 [GitHub Issues](https://github.com/your-repo/issues) 提出建议或问题
- 📧 联系我们：[team@isek.xyz](mailto:team@isek.xyz)
- 📄 阅读 [贡献指南](CONTRIBUTION.md)

---

## 📜 许可证

本项目遵循 [MIT License](LICENSE)。

---

<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br />
  <em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>
