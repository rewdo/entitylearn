"""EntityLearn 测试 - 单元测试：知识包加载器"""

import tempfile
from pathlib import Path

import pytest

from entitylearn.loader.pack_loader import PackLoader, load_pack, load_all_packs
from entitylearn.models.pack import Pack


@pytest.fixture
def sample_pack_dir():
    """创建示例知识包临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir) / "sample_pack"
        base.mkdir()

        # pack.yaml
        pack_yaml = base / "pack.yaml"
        pack_yaml.write_text("""
id: sample_pack
name: 示例知识包
version: "0.1.0"
description: 用于测试的示例知识包
domain: education
language: zh-CN
schema_version: "1.0"
license: MIT
entrypoints:
  agents: agents
  scenes: scenes
""", encoding="utf-8")

        # agents 目录
        agents_dir = base / "agents"
        agents_dir.mkdir()

        (agents_dir / "teacher.yaml").write_text("""
id: teacher_zhang
name: 张老师
kind: agent
description: 数学老师
persona: 我是一名数学老师
voice: 亲切
first_person: true
""", encoding="utf-8")

        # scenes 目录
        scenes_dir = base / "scenes"
        scenes_dir.mkdir()

        (scenes_dir / "math_lesson.yaml").write_text("""
id: math_lesson_1
name: 认识分数
kind: scene
description: 基础分数课程
objective: 理解分数
participants:
  - agent_id: teacher_zhang
    role_in_scene: 主讲
flow:
  - step_id: intro
    type: narration
    speaker: teacher_zhang
    content: 大家好
""", encoding="utf-8")

        yield base


class TestPackLoader:
    """测试 PackLoader"""

    def test_load_pack(self, sample_pack_dir):
        """测试加载单个知识包"""
        pack = load_pack(str(sample_pack_dir))
        assert isinstance(pack, Pack)
        assert pack.id == "sample_pack"
        assert pack.name == "示例知识包"

    def test_load_pack_agents(self, sample_pack_dir):
        """测试加载 Agent"""
        pack = load_pack(str(sample_pack_dir))
        assert len(pack.agents) == 1
        assert pack.agents[0].id == "teacher_zhang"
        assert pack.agents[0].name == "张老师"

    def test_load_pack_scenes(self, sample_pack_dir):
        """测试加载 Scene"""
        pack = load_pack(str(sample_pack_dir))
        assert len(pack.scenes) == 1
        assert pack.scenes[0].id == "math_lesson_1"

    def test_load_pack_from_yaml_path(self, sample_pack_dir):
        """测试从 pack.yaml 路径加载"""
        pack = load_pack(str(sample_pack_dir / "pack.yaml"))
        assert pack.id == "sample_pack"

    def test_load_all_packs(self, sample_pack_dir):
        """测试加载所有知识包"""
        packs = load_all_packs(str(sample_pack_dir.parent))
        assert len(packs) == 1
        assert packs[0].id == "sample_pack"

    def test_nonexistent_pack(self):
        """测试加载不存在的知识包"""
        with pytest.raises(FileNotFoundError):
            load_pack("/nonexistent/pack")

    def test_get_agent(self, sample_pack_dir):
        """测试 get_agent"""
        pack = load_pack(str(sample_pack_dir))
        agent = pack.get_agent("teacher_zhang")
        assert agent is not None
        assert agent.name == "张老师"

        assert pack.get_agent("nonexistent") is None

    def test_get_scene(self, sample_pack_dir):
        """测试 get_scene"""
        pack = load_pack(str(sample_pack_dir))
        scene = pack.get_scene("math_lesson_1")
        assert scene is not None
        assert scene.name == "认识分数"

        assert pack.get_scene("nonexistent") is None
