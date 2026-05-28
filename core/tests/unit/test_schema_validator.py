"""EntityLearn 测试 - 单元测试：Schema 校验器"""

import pytest

from entitylearn.loader.schema_validator import SchemaValidator, validate_pack
from entitylearn.models.pack import Pack, PackMeta
from entitylearn.models.agent import Agent, KnowledgeSource
from entitylearn.models.scene import (
    Scene,
    FlowStep,
    Participant,
    Breakpoint,
    SourceRef,
)


@pytest.fixture
def validator():
    """创建校验器"""
    return SchemaValidator()


@pytest.fixture
def valid_pack():
    """有效知识包"""
    agent = Agent(
        id="agent_1",
        name="测试Agent",
        persona="我是一个测试角色，用于回答测试问题。",
        voice="中性",
        first_person=True,
        knowledge_sources=[
            KnowledgeSource(path="knowledge/test.md", type="markdown")
        ],
    )

    scene = Scene(
        id="scene_1",
        name="测试场景",
        objective="测试目标",
        participants=[
            Participant(agent_id="agent_1", role_in_scene="speaker"),
        ],
        entry_agent_id="agent_1",
        flow=[
            FlowStep(
                step_id="step_1",
                type="narration",
                speaker="agent_1",
                content="第一步",
            ),
            FlowStep(
                step_id="step_2",
                type="narration",
                speaker="agent_1",
                content="第二步",
                next_step_id="step_1",  # 循环引用，但 step_id 存在
            ),
        ],
        breakpoints=[
            Breakpoint(step_id="step_1", prompt="请回答"),
        ],
    )

    return Pack(
        meta=PackMeta(
            id="test_pack",
            name="测试包",
            version="0.1.0",
            description="测试用",
        ),
        agents=[agent],
        scenes=[scene],
    )


class TestSchemaValidator:
    """测试 SchemaValidator"""

    def test_valid_pack_passes(self, validator, valid_pack):
        """测试有效知识包通过校验"""
        errors = validator.validate(valid_pack)
        assert len(errors) == 0

    def test_missing_id(self, validator):
        """测试缺少 ID"""
        pack = Pack(
            meta=PackMeta(id="", name="Test"),
        )
        errors = validator.validate(pack)
        assert any("id" in e.lower() for e in errors)

    def test_missing_name(self, validator):
        """测试缺少名称"""
        pack = Pack(
            meta=PackMeta(id="test", name=""),
        )
        errors = validator.validate(pack)
        assert any("name" in e.lower() for e in errors)

    def test_duplicate_agent_ids(self, validator):
        """测试重复 Agent ID"""
        agent1 = Agent(
            id="dup_agent",
            name="A1",
            persona="test persona here for validation.",
        )
        agent2 = Agent(
            id="dup_agent",
            name="A2",
            persona="another test persona here for validation.",
        )
        pack = Pack(
            meta=PackMeta(id="test", name="Test"),
            agents=[agent1, agent2],
        )
        errors = validator.validate(pack)
        assert any("duplicate" in e.lower() for e in errors)

    def test_unknown_agent_reference(self, validator):
        """测试引用不存在的 Agent"""
        scene = Scene(
            id="scene_1",
            name="场景",
            participants=[
                Participant(agent_id="nonexistent_agent", role_in_scene="speaker"),
            ],
            flow=[
                FlowStep(step_id="s1", speaker="system", content="hello"),
            ],
        )
        pack = Pack(
            meta=PackMeta(id="test", name="Test"),
            scenes=[scene],
        )
        errors = validator.validate(pack)
        assert any("nonexistent_agent" in e for e in errors)

    def test_breakpoint_step_not_found(self, validator):
        """测试断点步骤不存在"""
        scene = Scene(
            id="scene_1",
            name="场景",
            flow=[
                FlowStep(step_id="s1", speaker="system", content="hello"),
            ],
            breakpoints=[
                Breakpoint(step_id="nonexistent_step", prompt="?"),
            ],
        )
        pack = Pack(
            meta=PackMeta(id="test", name="Test"),
            scenes=[scene],
        )
        errors = validator.validate(pack)
        assert any("breakpoint" in e.lower() and "nonexistent_step" in e for e in errors)

    def test_unknown_speaker(self, validator):
        """测试未知 speaker"""
        scene = Scene(
            id="scene_1",
            name="场景",
            flow=[
                FlowStep(step_id="s1", speaker="unknown_speaker", content="hello"),
            ],
        )
        pack = Pack(
            meta=PackMeta(id="test", name="Test"),
            scenes=[scene],
        )
        errors = validator.validate(pack)
        assert any("unknown_speaker" in e for e in errors)

    def test_empty_scene_flow(self, validator):
        """测试空流程"""
        scene = Scene(
            id="scene_1",
            name="空场景",
            flow=[],
        )
        pack = Pack(
            meta=PackMeta(id="test", name="Test"),
            scenes=[scene],
        )
        errors = validator.validate(pack)
        assert any("no flow steps" in e.lower() for e in errors)

    def test_unknown_next_step_id(self, validator):
        """测试 next_step_id 不存在"""
        scene = Scene(
            id="scene_1",
            name="场景",
            flow=[
                FlowStep(
                    step_id="s1",
                    speaker="system",
                    content="hello",
                    next_step_id="nonexistent",
                ),
            ],
        )
        pack = Pack(
            meta=PackMeta(id="test", name="Test"),
            scenes=[scene],
        )
        errors = validator.validate(pack)
        assert any("next_step_id" in e.lower() for e in errors)
