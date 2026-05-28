# 路线图 | Roadmap

> EntityLearn 版本规划与里程碑

---

## 📊 版本概览

| 版本 | 状态 | 预计时间 | 核心目标 |
|------|------|----------|---------|
| v0.1.0-alpha | 🟡 开发中 | 2026 Q2 | 示例包可加载可播放 |
| v0.2.0-beta | ⚪ 规划中 | 2026 Q3 | 多领域包 + CI 校验 + RAG 问答 |
| v1.0.0 | ⚪ 规划中 | 2026 Q4 | Schema 稳定 + 社区可持续 |

---

## 🎯 v0.1.0-alpha — 示例包可加载可播放

### 目标
验证核心抽象的正确性：Pack → Agent → Scene → Test 的闭环。

### 已完成 ✅
- [x] 项目仓库初始化
- [x] 目录结构搭建
- [x] JSON Schema 定义（pack, agent, scene, test）
- [x] 模板文件（agent-template, scene-template, test-template）
- [x] 文档体系搭建（README, 架构, 快速开始, 贡献指南）

### 进行中 🟡
- [ ] Pydantic 数据模型实现
- [ ] Pack Loader：YAML → Pydantic 模型
- [ ] Schema Validator：基于 JSON Schema 的校验
- [ ] CLI 基础命令：list, validate, entities list

### 待完成 ⚪
- [ ] Scene Runner 基础版（narration + dialogue + breakpoint）
- [ ] networking 示例包完整实现（3 agents, 1 scene, knowledge, tests）
- [ ] `entitylearn play` 交互式场景运行
- [ ] 核心测试覆盖率 > 80%
- [ ] 打包发布到 PyPI

---

## 🚀 v0.2.0-beta — 多领域包 + CI 校验 + RAG 问答

### 目标
从"能跑"到"能用"：多领域支持、自动化质量保障、RAG 增强问答。

### 计划功能

#### 多领域支持
- [ ] Pack 注册与发现机制
- [ ] 跨 Pack 的 Agent 引用
- [ ] Pack 版本管理与依赖
- [ ] Pack 市场（Community Pack Registry）

#### CI 校验增强
- [ ] GitHub Actions 自动校验所有 Pack
- [ ] Schema 兼容性检查
- [ ] 知识覆盖率报告
- [ ] 回归测试自动运行

#### RAG 问答
- [ ] 知识文档自动向量化
- [ ] 向量存储后端（ChromaDB / FAISS）
- [ ] 语义检索 + 关键词混合搜索
- [ ] Re-ranker 结果优化
- [ ] 上下文窗口管理

#### Agent 增强
- [ ] FAQ 匹配（精确匹配 → 语义匹配）
- [ ] 多轮对话状态管理
- [ ] 引用追踪（回答中标注知识来源）

#### API & Web UI
- [ ] RESTful API 完善
- [ ] SSE 流式输出
- [ ] Web UI 场景播放器
- [ ] Web UI Agent 聊天界面
- [ ] 知识包浏览器

---

## 🏆 v1.0.0 — Schema 稳定 + 社区可持续

### 目标
生产就绪、向后兼容、社区自治。

### 计划功能

#### Schema 稳定
- [ ] 1.0 Schema 冻结承诺（向后兼容至 2.0）
- [ ] 完整的迁移指南和工具
- [ ] Schema 版本协商

#### 性能与可靠性
- [ ] 大型知识包（100+ 文档）性能优化
- [ ] 并发场景执行
- [ ] 缓存层
- [ ] 错误恢复与重试

#### 社区治理
- [ ] 维护者团队（Maintainers）
- [ ] RFC 流程（Request for Comments）
- [ ] 社区 Pack 审核流程
- [ ] 贡献者激励计划

#### 生态建设
- [ ] VS Code 插件（YAML 自动补全 + Schema 验证）
- [ ] Pack Creator CLI 向导
- [ ] 官方示例包库（5+ 领域）
- [ ] 培训课程 / Workshop 材料

---

## 🔮 未来愿景（v1.x+）

| 方向 | 描述 |
|------|------|
| **多模态知识** | 支持图片、音频、视频作为知识来源 |
| **动态场景** | 根据用户水平动态调整场景难度和路径 |
| **Agent 训练** | 基于场景交互数据微调专用模型 |
| **联邦知识包** | 在不共享原始数据的前提下联合训练 |
| **企业版** | 私有部署、RBAC、审计日志 |

---

## 📅 发布节奏

- **Alpha 版本**: 每 2 周一个小版本
- **Beta 版本**: 每月一个里程碑
- **正式版本**: 按 RFC 流程

---

## 💬 参与讨论

对路线图有建议？欢迎：

- 提交 [Feature Request](https://github.com/entitylearn/entitylearn/issues/new?template=feature_request.md)
- 参与 [GitHub Discussions](https://github.com/entitylearn/entitylearn/discussions)
- 发送 Pack Proposal
