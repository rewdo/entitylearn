# 贡献指南（技术深度版）| Contribution Guide (Technical)

> 本文档是 [CONTRIBUTING.md](../CONTRIBUTING.md) 的补充，面向开发者提供更深入的技术细节。

---

## 📦 知识包开发详解

### Pack 文件结构

```
packs/<pack-id>/
├── pack.yaml              # 包元信息（必需）
├── agents/                # Agent 定义（必需）
│   ├── agent-a.yaml
│   └── agent-b.yaml
├── scenes/                # 场景定义（必需）
│   └── scene-1.yaml
├── knowledge/             # 知识文档（必需）
│   ├── overview.md
│   ├── procedures.md
│   └── glossary.md
└── tests/                 # 测试用例（必需）
    ├── agent-a-test.yaml
    └── scene-1-test.yaml
```

### pack.yaml 规范

```yaml
id: my-pack                 # 全局唯一，小写字母+数字+连字符
name: My Pack               # 显示名称
version: 0.1.0              # SemVer
description: >              # 10-1024 字符
  描述这个知识包的领域和价值。
domain: my-domain           # 所属领域
language: zh-CN             # 主要语言
authors:                    # 至少 1 位作者
  - name: Author Name
    email: author@example.com
license: MIT                # SPDX 标识符
schema_version: "1.0"       # 使用的 schema 版本
entrypoints:                # 子资源路径
  agents: agents/
  scenes: scenes/
  knowledge: knowledge/
  tests: tests/
tags:                       # 最多 10 个标签
  - networking
  - bgp
compatibility:              # 引擎版本兼容
  min_engine_version: 0.1.0
```

### Agent 编写最佳实践

1. **persona 要具体** — 抽象的人格设定效果很差
   ```yaml
   # ❌ 不好
   persona: 你是一个专家
   # ✅ 好
   persona: >
     你是李明，XX通信公司资深网络工程师，从业15年。
     持有CCIE认证，精通BGP/OSPF/IS-IS路由协议。
     你的工作风格是严谨细致，排查问题遵循OSI七层模型从底层开始。
   ```

2. **knowledge_sources 要精确** — 每个知识源注明类型和用途
   ```yaml
   # ✅ 好
   knowledge_sources:
     - path: knowledge/bgp-troubleshooting.md
       type: procedure
       title: BGP故障排查流程
       note: 当用户提到BGP相关问题时优先引用
   ```

3. **responsibilities 要可测试** — 每条职责应该能对应一个测试用例

4. **forbidden_topics 要明确** — 保护用户和系统安全

### Scene 编写最佳实践

1. **flow 步骤命名规范** — 使用有意义的 step_id
   ```yaml
   # ❌ 不好
   - step_id: s1
   # ✅ 好
   - step_id: discovery-phase-query
   ```

2. **场景复杂度控制** — 推荐参数：
   - 初学者场景：3-8 步
   - 中级场景：8-15 步
   - 高级场景：15-30 步

3. **breakpoint 设计原则**：
   - 每个关键决策点设置断点
   - 断点 prompt 要清晰指明期望的输入类型
   - 用户输入后应有明确的反馈

4. **visual_hint 使用** — 为 Web UI 提供渲染提示
   ```yaml
   visual_hint: >
     拓扑图：Router-A <--BGP--> Router-B <--BGP--> Router-C
     Router-B 和 Router-C 之间链路断开（红色虚线）
   ```

### Test 编写最佳实践

一个完整的测试套件应覆盖：

| 测试维度 | 说明 | 示例 |
|---------|------|------|
| 基础问答 | Agent 能否正确介绍自己 | `expected_keywords: ["专家", "帮助"]` |
| 知识引用 | 回答是否基于正确的知识源 | `expected_sources: ["knowledge/guide.md"]` |
| 边界处理 | 超出领域时如何表现 | `must_include_uncertainty_if_no_source: true` |
| 风格检查 | 是否符合人格设定 | `must_be_first_person: true` |
| 安全过滤 | 是否拒绝不当请求 | `forbidden_keywords: ["可以帮你违法"]` |
| 长度控制 | 回答是否过长/过短 | `max_answer_length: 500` |

---

## 💻 核心引擎开发

### 开发环境

```bash
uv sync --dev
```

### 目录说明

```
core/
├── entitylearn/           # 主包
│   ├── __init__.py
│   ├── main.py            # CLI 入口
│   ├── config.py          # 全局配置
│   ├── api/               # FastAPI 应用
│   │   ├── __init__.py
│   │   ├── server.py      # uvicorn 启动
│   │   ├── middleware.py  # 中间件
│   │   └── routes/        # 路由
│   ├── loader/            # 加载器
│   │   ├── __init__.py
│   │   ├── pack_loader.py
│   │   ├── agent_loader.py
│   │   ├── scene_loader.py
│   │   └── knowledge_loader.py
│   ├── models/            # Pydantic 模型（与 Schema 对应）
│   │   ├── __init__.py
│   │   ├── pack.py
│   │   ├── agent.py
│   │   ├── scene.py
│   │   └── test.py
│   ├── retrieval/         # RAG 检索
│   │   ├── __init__.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   ├── runtime/           # 运行时
│   │   ├── __init__.py
│   │   ├── scene_runner.py
│   │   └── dialogue_manager.py
│   └── validation/        # 校验
│       ├── __init__.py
│       └── validator.py
└── tests/                 # 核心测试
    ├── unit/
    │   ├── test_loader.py
    │   ├── test_models.py
    │   └── test_retrieval.py
    └── integration/
        └── test_api.py
```

### 添加新功能的标准流程

1. **定义模型** — 在 `models/` 中创建 Pydantic 类
2. **实现逻辑** — 在对应模块中实现功能
3. **添加路由** — 如需 API 暴露，在 `api/routes/` 添加
4. **编写测试** — 覆盖正常和异常路径
5. **更新 Schema** — 如需新的配置格式，更新 JSON Schema
6. **更新文档** — 更新架构文档和快速开始

---

## 🎨 UI 开发

前端使用 Next.js + TypeScript。详见 `frontend/` 目录。

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

---

## 📋 提交前检查清单

在提交 PR 前，确认：

```bash
# 1. 代码格式化
black core/ --line-length 100
ruff check core/

# 2. 类型检查
mypy core/entitylearn/

# 3. 单元测试
pytest --cov=entitylearn --cov-report=term-missing

# 4. 知识包校验
entitylearn validate networking

# 5. 知识包测试
entitylearn test networking

# 6. 合规检查（确保无品牌泄露）
# 参考项目合规要求
```
