# 贡献指南 | Contributing Guide

感谢你对 EntityLearn 的关注！🎉

## 📋 行为准则 | Code of Conduct

本项目遵循 [贡献者公约 2.1](CODE_OF_CONDUCT.md)。参与贡献即表示你同意遵守其条款。

---

## 📦 如何贡献知识包 | How to Contribute a Pack

知识包（Pack）是 EntityLearn 最核心的贡献形式。一个高质量的 Pack 可以让整个社区受益。

### 步骤

1. **选题** — 确认你的领域尚未被覆盖（查看 [packs/](packs/) 目录或搜索已有 Issues）
2. **提案** — 提交 [Pack Proposal](.github/ISSUE_TEMPLATE/pack_proposal.md) Issue，说明领域、实体设计、场景设计方案
3. **开发** — 按照规范创建知识包文件：
   - `pack.yaml` — 包元信息
   - `agents/*.yaml` — 实体 Agent 定义
   - `scenes/*.yaml` — 场景定义
   - `knowledge/*.md` — 知识文档
   - `tests/*.yaml` — 测试用例
4. **校验** — 运行 `entitylearn validate packs/<your-pack>` 确保通过
5. **提 PR** — 按 PR 模板提交，确保 CI 通过

### 知识包规范要求

- ✅ 所有 Agent 必须有明确的 `role` 和 `responsibilities`
- ✅ 每个 Agent 至少关联一个 `knowledge_source`
- ✅ 每个场景至少包含 2 个实体之间的互动
- ✅ 测试覆盖率至少包含 3 个测试用例
- ✅ 禁止包含个人隐私、敏感商业数据
- ✅ 知识文档使用 Markdown 格式
- ✅ 所有 YAML 文件通过 `entitylearn validate` 校验

---

## 💻 如何贡献代码 | How to Contribute Code

### 开发环境搭建

```bash
# 克隆并安装
git clone https://github.com/entitylearn/entitylearn.git
cd entitylearn

# 使用 uv 安装（推荐）
uv sync --dev

# 或使用 pip
pip install -e ".[dev]"

# 运行测试确认环境正常
pytest
```

### 代码规范

- **格式化**: 使用 [Black](https://github.com/psf/black) (line-length=100)
- **Lint**: 使用 [Ruff](https://github.com/astral-sh/ruff)
- **类型标注**: 所有公开函数必须有类型标注
- **文档字符串**: 使用 Google docstring 风格

```bash
# 格式化代码
black core/ --line-length 100
ruff check core/

# 运行测试
pytest --cov=entitylearn
```

### 提交 PR 流程

1. **Fork** 本仓库
2. **创建分支**: `git checkout -b feat/your-feature` 或 `fix/your-fix`
3. **开发并测试**: 确保 `pytest` 全部通过
4. **提交**: 使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式
   ```
   feat: add auto-pack discovery
   fix: resolve schema validation for nested agents
   docs: update quickstart guide
   ```
5. **推送**: `git push origin feat/your-feature`
6. **创建 PR**: 填写 PR 模板，关联相关 Issue
7. **等待 Review**: 至少需要 1 位维护者的 Approve

### PR Checklist

请确保 PR 满足以下条件：

- [ ] 测试通过 (`pytest`)
- [ ] 代码格式化通过 (`black` + `ruff`)
- [ ] 知识包 schema 校验通过 (`entitylearn validate`)
- [ ] 文档已更新（如需）
- [ ] 相关 Issue 已关联
- [ ] 无品牌合规敏感内容（见下方说明）

---

## 🔒 合规要求 | Compliance

本项目禁止包含特定品牌标识。详情请咨询项目维护者。

---

## 🧪 测试要求 | Testing Requirements

```bash
# 运行所有测试
pytest

# 运行带覆盖率
pytest --cov=entitylearn --cov-report=term-missing

# 运行特定测试
pytest core/tests/unit/test_loader.py

# 运行知识包测试
entitylearn test packs/networking
```
