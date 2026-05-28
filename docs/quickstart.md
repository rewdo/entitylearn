# 快速开始 | Quick Start

> 5 分钟上手 EntityLearn

---

## 📋 环境要求

| 项目 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.10+ | 推荐 3.11 |
| uv | 最新版 | 推荐包管理器 |
| Git | 最新版 | 克隆仓库 |
| Docker | 可选 | 容器化部署 |

---

## 🚀 安装

### 方式一：源码安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/entitylearn/entitylearn.git
cd entitylearn

# 安装（含开发依赖）
uv sync --dev

# 或使用 pip
pip install -e ".[dev]"

# 验证安装
entitylearn --version
```

### 方式二：Docker

```bash
docker-compose -f docker/docker-compose.yml up -d
# 访问 http://localhost:8000
```

---

## 🎯 运行第一个场景

### 1. 查看可用知识包

```bash
entitylearn list
```

输出示例：
```
Available packs:
  networking (v0.1.0) - 网络故障排查知识包
```

### 2. 查看包内实体

```bash
entitylearn entities list networking
```

输出示例：
```
Agents in networking:
  - net-engineer    网络工程师
  - noc-operator    NOC值班员
  - field-tech      现场技术员

Scenes in networking:
  - bgp-peering-troubleshoot  BGP邻居断开故障排查
  - ospf-neighbor-down        OSPF邻居Down排查
```

### 3. 运行场景

```bash
entitylearn play networking --scene bgp-peering-troubleshoot
```

你将看到场景逐步展开，在断点处可以输入你的回应。

### 4. 交互示例

```
[场景开始] BGP邻居断开故障排查
─────────────────────────────────

【旁白】周一上午 9:30，NOC 监控系统发出告警...

【NOC值班员】工程师你好，监控显示 AS65001 的 BGP 邻居 Down 了，
              你能帮忙分析一下原因吗？

💬 你的回应 > 先确认一下物理链路状态
                                    # ← 你在这里输入

【网络工程师】好的，我先检查物理层。
              请 NOC 确认对端设备是否可达？
...
```

---

## 🌐 Web UI 启动

```bash
entitylearn serve

# 或指定端口
entitylearn serve --port 8080 --host 0.0.0.0
```

访问 `http://localhost:8000` 即可看到 Web UI：

- **知识包浏览器** — 查看已安装的知识包
- **场景播放器** — 交互式运行场景
- **Agent 聊天** — 与单个 Agent 对话
- **知识检索** — 直接搜索知识库

---

## 📦 创建你的第一个知识包

### 1. 复制模板

```bash
cp -r packs/templates/pack-template packs/my-domain
```

### 2. 编辑 pack.yaml

```yaml
id: my-domain
name: 我的领域知识包
version: 0.1.0
description: 我的第一个知识包
domain: my-domain
# ... 其余配置
```

### 3. 创建 Agent

在 `packs/my-domain/agents/` 下创建 `expert.yaml`：

```yaml
id: expert
name: 领域专家
description: 我的领域专家 Agent
role: Domain Expert
persona: 你是一位领域专家...
responsibilities:
  - 回答领域相关问题
knowledge_sources:
  - path: knowledge/guide.md
    type: document
```

### 4. 添加知识文档

在 `packs/my-domain/knowledge/` 下创建 `guide.md`：

```markdown
# 领域知识指南

## 核心概念

...你的知识内容...
```

### 5. 创建场景和测试

参考模板创建 `scenes/` 和 `tests/` 文件。

### 6. 校验和运行

```bash
entitylearn validate my-domain
entitylearn test my-domain
entitylearn play my-domain
```

---

## 🧪 运行测试

```bash
# 核心引擎测试
pytest

# 知识包测试
entitylearn test networking

# 特定 Agent 测试
entitylearn test networking --target net-engineer
```

---

## 📚 下一步

- 📖 [架构文档](architecture.md) — 了解系统架构
- 🧩 [贡献指南](contribution-guide.md) — 深度技术贡献教程
- 🗺️ [路线图](roadmap.md) — 查看未来规划

---

## ❓ 常见问题

**Q: 支持哪些 LLM？**
A: 通过 LLMProviderBase 扩展点，理论上支持任何 LLM。当前内置支持 OpenAI 兼容 API。

**Q: 知识包可以私有吗？**
A: 可以。知识包是本地文件，你可以选择不公开发布。

**Q: 支持多语言吗？**
A: 引擎层完全支持多语言。在 `pack.yaml` 中设置 `language` 字段即可。
