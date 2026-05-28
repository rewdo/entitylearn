# EntityLearn 架构文档 | Architecture

> 本文档描述 EntityLearn 的系统架构、核心组件、数据流和扩展点。
> 最后更新：2026-05-28

---

## 📐 整体架构概览

EntityLearn 采用**分层架构**，从知识组织到场景运行形成清晰的抽象层次：

```
┌──────────────────────────────────────────────────────┐
│                    用户界面层                          │
│  ┌─────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │  Web UI     │  │  CLI Tool  │  │  API Client   │  │
│  │  (Next.js)  │  │  (entitylearn)│  │  (HTTP/SSE)  │  │
│  └──────┬──────┘  └─────┬──────┘  └───────┬──────┘  │
├─────────┴────────────────┴──────────────────┴────────┤
│                     API 层 (FastAPI)                   │
│  ┌──────────────────────────────────────────────┐    │
│  │  REST Endpoints  │  WebSocket  │  SSE Stream │    │
│  └──────────────────────┬───────────────────────┘    │
├──────────────────────────┴───────────────────────────┤
│                      核心引擎层                         │
│  ┌──────────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │   Runtime    │ │Retrieval │ │    Validation    │ │
│  │  场景运行时    │ │  RAG检索  │ │   Schema校验    │ │
│  └──────┬───────┘ └────┬─────┘ └────────┬─────────┘ │
│  ┌──────┴───────┐      │                │           │
│  │    Loader    │      │                │           │
│  │  Pack加载器   │◄─────┘                │           │
│  └──────┬───────┘                       │           │
│  ┌──────┴───────────────────────────────┴──────────┐ │
│  │                  Models (Pydantic)               │ │
│  │        数据模型: Agent, Scene, Pack, Test         │ │
│  └─────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│                      知识包层                          │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐             │
│  │ Agents  │  │ Scenes  │  │Knowledge │  ┌───────┐  │
│  │ .yaml   │  │ .yaml   │  │  .md     │  │ Tests │  │
│  └─────────┘  └─────────┘  └──────────┘  │ .yaml │  │
│                                          └───────┘  │
└──────────────────────────────────────────────────────┘
```

### 四层架构说明

| 层 | 职责 | 关键组件 |
|-----|------|---------|
| **Pack 层** | 知识组织与分发 | pack.yaml, agents, scenes, knowledge, tests |
| **Agent 层** | 角色定义与知识绑定 | Agent 定义文件 + Pydantic 模型 |
| **Scene 层** | 多 Agent 交互编排 | Scene 定义文件 + 流程引擎 |
| **Knowledge/Test 层** | 知识存储与质量保障 | Markdown 文档 + 测试 YAML |

---

## 🔧 核心引擎分层

### 1. Loader（加载器）

```
core/entitylearn/loader/
├── pack_loader.py      # Pack 加载入口
├── agent_loader.py     # Agent YAML 加载
├── scene_loader.py     # Scene YAML 加载
├── knowledge_loader.py # 知识文档加载
└── test_loader.py      # 测试用例加载
```

**职责：**
- 发现并加载 `packs/` 目录下的知识包
- 解析 YAML/Markdown 文件为 Pydantic 模型
- 验证引用的完整性（agent 引用了不存在的 knowledge 源等）
- 提供 Pack 资源索引

### 2. Runtime（运行时）

```
core/entitylearn/runtime/
├── scene_runner.py     # 场景执行引擎
├── dialogue_manager.py # 对话管理
├── agent_executor.py   # Agent 调用执行
└── context_manager.py  # 上下文窗口管理
```

**职责：**
- 按流程定义逐步执行场景
- 管理多 Agent 对话上下文
- 处理用户断点输入
- 流式输出场景进展

### 3. Retrieval（检索）

```
core/entitylearn/retrieval/
├── embedder.py         # 文本向量化
├── vector_store.py     # 向量存储
├── retriever.py        # 检索接口
└── reranker.py         # 结果重排序
```

**职责：**
- 将知识文档向量化并索引
- 根据查询检索相关片段
- 支持语义搜索和关键词搜索
- 可插拔的 embedding 和存储后端

### 4. API（接口）

```
core/entitylearn/api/
├── routes/
│   ├── packs.py        # 知识包管理 API
│   ├── agents.py       # Agent 查询 API
│   ├── scenes.py       # 场景执行 API
│   └── search.py       # 知识检索 API
├── middleware.py       # 中间件
└── server.py           # 服务启动
```

**职责：**
- 提供 RESTful API
- WebSocket 支持实时对话
- SSE 支持流式输出
- 请求验证和错误处理

---

## 🖥 前端架构

```
frontend/
├── src/
│   ├── app/            # Next.js App Router
│   ├── components/     # UI 组件
│   │   ├── AgentCard/  # Agent 信息卡片
│   │   ├── ScenePlayer/ # 场景播放器
│   │   ├── ChatInterface/ # 聊天界面
│   │   └── PackBrowser/ # 知识包浏览器
│   ├── pages/          # 页面
│   ├── services/       # API 调用封装
│   ├── styles/         # 样式
│   └── types/          # TypeScript 类型定义
└── public/             # 静态资源
```

**技术栈：** Next.js + TypeScript + Tailwind CSS

---

## 🔄 数据流

### 场景执行流程

```
用户请求场景
    │
    ▼
API 接收请求 (POST /api/scenes/{pack_id}/{scene_id}/play)
    │
    ▼
Loader 加载 Pack + Scene 定义
    │
    ▼
Runtime 初始化场景上下文
    │
    ▼
┌─────────────────────────────────┐
│  场景循环 (step by step)         │
│  ┌─────────────────────────┐    │
│  │ narration → 展示叙述      │    │
│  │ dialogue → Agent 生成对话 │◄── Retriever (RAG)
│  │ breakpoint → 等待用户输入  │    │
│  │ transition → 切换场景      │    │
│  └──────────┬──────────────┘    │
│             │                   │
│             ▼                   │
│      用户输入 (SSE/WS)           │
└─────────────────────────────────┘
    │
    ▼
返回场景结果 / 继续执行
```

### RAG 检索流程

```
用户问题
    │
    ▼
Query 预处理 → Embedding
    │
    ▼
Vector Store 检索 (Top-K)
    │
    ▼
Re-ranker 重排序
    │
    ▼
拼接上下文 → 注入 Agent Prompt
    │
    ▼
LLM 生成回答
```

---

## 🔌 扩展点

| 扩展点 | 说明 | 接口 |
|--------|------|------|
| **Embedding 后端** | 替换向量化引擎 | `EmbedderBase` |
| **Vector Store** | 替换向量存储 | `VectorStoreBase` |
| **LLM Provider** | 替换大语言模型 | `LLMProviderBase` |
| **Loader Plugin** | 支持新文件格式 | `LoaderPlugin` |
| **Scene Hook** | 场景生命周期钩子 | `SceneHook` |
| **API Middleware** | 自定义中间件 | FastAPI Middleware |

### 扩展示例：添加自定义 LLM Provider

```python
from entitylearn.runtime.llm import LLMProviderBase

class MyLLMProvider(LLMProviderBase):
    async def generate(self, prompt: str, **kwargs) -> str:
        # 你的实现
        ...
```

---

## 📊 技术选型总结

| 层级 | 技术 | 原因 |
|------|------|------|
| Python 框架 | FastAPI + Pydantic | 高性能、类型安全 |
| Schema 校验 | JSON Schema Draft-07 | 标准、可移植 |
| 配置格式 | YAML | 人类可读、注释友好 |
| 知识文档 | Markdown | 通用、格式化 |
| 前端 | Next.js | SSR/SSG、React 生态 |
| 容器化 | Docker + Compose | 一键部署 |
| 包管理 | uv | 快速、现代 |
| CI/CD | GitHub Actions | 免费、集成度高 |
