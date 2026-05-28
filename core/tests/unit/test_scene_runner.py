"""EntityLearn 测试 - 单元测试：场景运行器"""

from pathlib import Path

import pytest

from entitylearn.models.agent import Agent, KnowledgeSource, Scope, StyleGuide
from entitylearn.models.scene import (
    Scene,
    FlowStep,
    Participant,
    Breakpoint,
    SceneMetadata,
)
from entitylearn.runtime.scene_runner import SceneRunner, SceneStep


@pytest.fixture
def sample_agent() -> Agent:
    """示例 Agent"""
    return Agent(
        id="teacher_zhang",
        name="张老师",
        description="数学老师",
        persona="我是一名经验丰富的数学老师，擅长用生活中的例子讲解数学概念。",
        voice="亲切",
        first_person=True,
        responsibilities=["讲解数学概念"],
        knowledge_sources=[
            KnowledgeSource(
                path="knowledge/math_basics.md",
                type="markdown",
                title="数学基础",
            )
        ],
        scope=Scope(allowed_topics=["数学", "教育"]),
        style_guide=StyleGuide(tone="educational"),
    )


@pytest.fixture
def sample_scene() -> Scene:
    """示例场景"""
    return Scene(
        id="math_lesson_1",
        name="认识分数",
        description="通过分披萨认识分数概念",
        objective="学生能理解分数的基本概念",
        participants=[
            Participant(agent_id="teacher_zhang", role_in_scene="主讲老师"),
        ],
        entry_agent_id="teacher_zhang",
        breakpoints=[
            Breakpoint(
                step_id="question_1",
                prompt="你觉得1/2和2/4一样大吗？",
                allowed_agents=["teacher_zhang"],
            ),
        ],
        flow=[
            FlowStep(
                step_id="intro",
                type="narration",
                speaker="teacher_zhang",
                content="同学们好！今天我们学习分数的基本概念。",
            ),
            FlowStep(
                step_id="example",
                type="narration",
                speaker="teacher_zhang",
                content="假设我们有一个披萨，把它切成4块...",
            ),
            FlowStep(
                step_id="question_1",
                type="question",
                speaker="teacher_zhang",
                content="你觉得1/2和2/4一样大吗？",
            ),
            FlowStep(
                step_id="summary",
                type="narration",
                speaker="teacher_zhang",
                content="今天我们学习了分数的基本概念！",
            ),
        ],
        metadata=SceneMetadata(difficulty="beginner", estimated_duration_min=15),
    )


class TestSceneRunner:
    """测试 SceneRunner"""

    def test_init(self):
        """测试初始化"""
        runner = SceneRunner()
        assert runner.current_scene is None
        assert runner.is_paused is False

    def test_load_scene(self, sample_scene):
        """测试加载场景"""
        runner = SceneRunner()
        runner.load_scene(sample_scene)
        assert runner.current_scene is not None
        assert runner.current_scene.id == "math_lesson_1"

    def test_run_scene_generator(self, sample_agent, sample_scene):
        """测试 Generator 模式播放场景"""
        agents = {sample_agent.id: sample_agent}
        runner = SceneRunner(agents=agents)

        gen = runner.run_scene(sample_scene, agents)

        # 第1步：intro
        step1 = next(gen)
        assert isinstance(step1, SceneStep)
        assert step1.step_id == "intro"
        assert step1.speaker == "teacher_zhang"
        assert "同学们好" in step1.content

        # 第2步：example
        step2 = next(gen)
        assert step2.step_id == "example"
        assert "披萨" in step2.content

        # 第3步：question_1 (breakpoint)
        step3 = next(gen)
        assert step3.is_breakpoint is True
        assert step3.step_id == "question_1"
        assert "1/2" in step3.content

    def test_next_method(self, sample_agent, sample_scene):
        """测试 next() 方法"""
        agents = {sample_agent.id: sample_agent}
        runner = SceneRunner(agents=agents)
        runner.load_scene(sample_scene)

        step1 = runner.next()
        assert step1 is not None
        assert step1.step_id == "intro"

        step2 = runner.next()
        assert step2 is not None
        assert step2.step_id == "example"

        # 第三个是断点，会暂停
        step3 = runner.next()
        assert step3 is not None
        assert step3.is_breakpoint is True
        assert runner.is_paused is True

    def test_empty_scene(self):
        """测试空场景"""
        empty_scene = Scene(
            id="empty",
            name="空场景",
            flow=[],
            participants=[],
        )
        runner = SceneRunner()
        gen = runner.run_scene(empty_scene)
        with pytest.raises(StopIteration):
            next(gen)

    def test_context_tracking(self, sample_agent, sample_scene):
        """测试上下文跟踪"""
        agents = {sample_agent.id: sample_agent}
        runner = SceneRunner(agents=agents)
        runner.load_scene(sample_scene)

        runner.next()  # intro
        ctx = runner.context.get_context()
        assert ctx["steps_played"] == 1
        assert ctx["current_step_id"] == "intro"

        runner.next()  # example
        ctx = runner.context.get_context()
        assert ctx["steps_played"] == 2
