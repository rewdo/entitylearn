"""EntityLearn 测试 - 单元测试：Agent 运行时"""

import tempfile
from pathlib import Path

import pytest

from entitylearn.models.agent import Agent, KnowledgeSource, FAQ, Scope, StyleGuide
from entitylearn.runtime.agent_runtime import AgentRuntime, Answer


@pytest.fixture
def sample_agent() -> Agent:
    """示例 Agent"""
    return Agent(
        id="doctor_li",
        name="李医生",
        description="内科医生",
        persona="我是一名经验丰富的内科医生，擅长用通俗易懂的方式解释医学概念。",
        voice="专业温和",
        first_person=True,
        responsibilities=["回答内科医学问题"],
        knowledge_sources=[
            KnowledgeSource(
                path="knowledge/common_cold.md",
                type="markdown",
                title="感冒知识",
            ),
        ],
        faq=[
            FAQ(
                question="感冒了怎么办",
                answer="感冒通常是由病毒引起的，{{person}}建议多休息、多喝水、饮食清淡。大多数感冒在7-10天内会自行好转。",
                sources=["knowledge/common_cold.md"],
            ),
            FAQ(
                question="什么是感冒",
                answer="感冒是一种常见的上呼吸道病毒感染。{{person}}常见的症状包括流鼻涕、咳嗽、喉咙痛。",
                sources=["knowledge/common_cold.md"],
            ),
        ],
        scope=Scope(
            allowed_topics=["感冒", "内科", "健康"],
            disallowed_topics=["手术", "外科"],
        ),
        forbidden_topics=["政治"],
        style_guide=StyleGuide(tone="professional", length="medium"),
    )


class TestAgentRuntime:
    """测试 AgentRuntime"""

    def test_init(self):
        """测试初始化"""
        runtime = AgentRuntime()
        assert runtime.pack_path is None

    def test_init_with_path(self, tmp_path):
        """测试带路径初始化"""
        runtime = AgentRuntime(pack_path=tmp_path)
        assert runtime.pack_path == tmp_path

    def test_faq_match_exact(self, sample_agent):
        """测试 FAQ 精确匹配"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "感冒了怎么办")
        assert isinstance(answer, Answer)
        assert answer.confidence > 0.5
        assert "休息" in answer.content or "多喝水" in answer.content
        assert "knowledge/common_cold.md" in answer.sources

    def test_faq_match_partial(self, sample_agent):
        """测试 FAQ 部分匹配"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "什么是感冒呢？")
        assert isinstance(answer, Answer)
        assert answer.confidence > 0.3
        assert "病毒" in answer.content or "呼吸道" in answer.content

    def test_forbidden_topic(self, sample_agent):
        """测试禁止话题"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "聊一下政治话题")
        assert answer.confidence == 0.0
        assert "不方便" in answer.content

    def test_disallowed_topic(self, sample_agent):
        """测试不在范围内的话题"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "怎么做外科手术")
        assert answer.confidence == 0.0

    def test_no_knowledge_match(self, sample_agent):
        """测试无知识匹配"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "今天天气怎么样")
        assert answer.confidence == 0.0
        assert "不确定" in answer.content or "没有足够的信息" in answer.content

    def test_knowledge_search_with_file(self, sample_agent, tmp_path):
        """测试知识文档搜索"""
        # 创建知识文档
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir()
        (knowledge_dir / "common_cold.md").write_text(
            """# 感冒知识

## 什么是感冒

感冒是由病毒引起的上呼吸道感染。

## 感冒症状

常见症状包括流鼻涕、咳嗽、打喷嚏、喉咙痛等。

## 感冒治疗

多休息、多喝水是基本原则。症状严重时可使用对症药物。
""",
            encoding="utf-8",
        )

        runtime = AgentRuntime(pack_path=tmp_path)
        answer = runtime.answer(sample_agent, "感冒有哪些症状")
        assert isinstance(answer, Answer)
        assert answer.confidence > 0.2
        assert "流鼻涕" in answer.content or "咳嗽" in answer.content

    def test_answer_sources(self, sample_agent):
        """测试回答来源"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "感冒了怎么办")
        assert len(answer.sources) > 0

    def test_first_person_output(self, sample_agent):
        """测试第一人称输出"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "感冒了怎么办")
        assert "我" in answer.content

    def test_non_first_person_agent(self, sample_agent):
        """测试非第一人称 Agent"""
        sample_agent.first_person = False
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "感冒了怎么办")
        # 应该使用 agent name 而不是 "我"
        assert "李医生" in answer.content

    def test_empty_question(self, sample_agent):
        """测试空问题"""
        runtime = AgentRuntime()
        answer = runtime.answer(sample_agent, "")
        assert answer.confidence == 0.0
