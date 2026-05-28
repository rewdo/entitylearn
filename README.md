# EntityLearn

> 🧠 实体驱动的 AI 知识场景引擎 — 让领域知识可编程、可测试、可共享

> 🧠 Entity-Driven AI Knowledge & Scene Engine — Make domain knowledge programmable, testable, and shareable

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](https://github.com/entitylearn/entitylearn)

---

## 📖 核心概念 | Core Concepts

### 什么是 EntityLearn？

EntityLearn 是一个**实体驱动的 AI 知识场景框架**。它把领域知识组织为三个核心抽象：

1. **实体 Agent** — 扮演领域中的具体角色（如网络工程师、客服代表），拥有知识源、行为准则和人格设定
2. **场景 Scene** — 编排多个 Agent 的对话/交互流程，模拟真实工作场景
3. **知识包 Pack** — 封装领域知识的独立分发单元，包含 agents、scenes、knowledge、tests

```
┌─────────────────────────────────┐
│          知识包 (Pack)          │
│  ┌─────────┐  ┌─────────────┐  │
│  │ Agents  │  │   Scenes    │  │
│  │ 实体角色  │  │   交互场景   │  │
│  └─────────┘  └─────────────┘  │
│  ┌─────────┐  ┌─────────────┐  │
│  │Knowledge│  │    Tests    │  │
│  │ 知识文档  │  │   自动化测试  │  │
│  └─────────┘  └─────────────┘  │
└─────────────────────────────────┘
```

**核心理念：** 知识不应该散落在提示词里。它应该被结构化、版本化、可测试。

### What is EntityLearn?

EntityLearn is an **entity-driven AI knowledge & scene framework**. It organizes domain knowledge into three core abstractions:

1. **Entity Agent** — Plays a specific role in the domain (e.g., network engineer, customer service rep), with knowledge sources, behavioral guidelines, and persona settings
2. **Scene** — Orchestrates multi-agent dialogue/interaction flows, simulating real-world scenarios
3. **Pack** — An independent distributable unit encapsulating domain knowledge, including agents, scenes, knowledge, and tests

**Core philosophy:** Knowledge shouldn't be scattered in prompts. It should be structured, versioned, and testable.

---

## 🚀 快速开始 | Quick Start

### 环境要求 | Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (推荐 / Recommended)

### 安装 | Installation

```bash
# 克隆仓库
git clone https://github.com/entitylearn/entitylearn.git
cd entitylearn

# 安装依赖
pip install -e ".[dev]"

# 或使用 uv
uv pip install -e ".[dev]"
```

### 运行示例场景 | Run Example Scene

```bash
# 校验知识包
entitylearn validate packs/networking

# 运行场景测试
entitylearn test packs/networking

# 列出所有可用实体
entitylearn entities list

# 启动交互式场景
entitylearn play networking --scene bgp-peering-troubleshoot
```

### 启动 Web UI | Launch Web UI

```bash
entitylearn serve

# 访问 http://localhost:8000
```

---

## 📁 项目结构 | Project Structure

```
entitylearn/
├── core/                        # 核心引擎
│   ├── entitylearn/             # Python 包
│   │   ├── api/                 # FastAPI 接口
│   │   ├── loader/              # Pack 加载器
│   │   ├── models/              # 数据模型
│   │   ├── retrieval/           # RAG 检索
│   │   ├── runtime/             # 场景运行时
│   │   └── validation/          # Schema 校验
│   └── tests/                   # 核心测试
├── docs/                        # 文档
│   ├── schema/                  # JSON Schema 定义
│   ├── architecture.md          # 架构文档
│   ├── quickstart.md            # 快速开始
│   └── roadmap.md               # 路线图
├── packs/                       # 知识包
│   ├── networking/              # 网络领域示例包
│   └── templates/               # 模板文件
├── frontend/                    # Web 前端
├── docker/                      # Docker 配置
├── pyproject.toml               # 项目配置
└── README.md
```

---

## 📚 文档 | Documentation

| 文档 | 说明 |
|------|------|
| [快速开始](docs/quickstart.md) | 5 分钟上手指南 |
| [架构文档](docs/architecture.md) | 系统架构与设计 |
| [贡献指南](docs/contribution-guide.md) | 参与开发的技术指南 |
| [路线图](docs/roadmap.md) | 版本规划与里程碑 |

---

## 🤝 贡献 | Contributing

我们欢迎所有形式的贡献！特别欢迎贡献新的知识包（Pack）。

- 📦 [贡献知识包](CONTRIBUTING.md#如何贡献知识包)
- 💻 [贡献代码](CONTRIBUTING.md#如何贡献代码)
- 📖 [行为准则](CODE_OF_CONDUCT.md)

---

## 🛡️ 安全 | Security

发现安全漏洞？请参见 [SECURITY.md](SECURITY.md) 了解报告流程。

---

## 📄 许可 | License

本项目基于 [MIT License](LICENSE) 开源。

Copyright (c) 2026 EntityLearn Contributors
