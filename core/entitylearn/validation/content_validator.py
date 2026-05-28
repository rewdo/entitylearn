"""内容校验器"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from ..models.agent import Agent
from ..models.scene import Scene

logger = logging.getLogger(__name__)


class ContentValidator:
    """内容校验器。

    校验 Agent 和 Scene 的内容完整性、合规性。
    """

    def validate_agent(self, agent: Agent) -> list[str]:
        """校验 Agent 内容完整性。

        Args:
            agent: 待校验的 Agent

        Returns:
            问题列表
        """
        issues = []

        # 必要字段
        if not agent.id or not agent.id.strip():
            issues.append("Agent id is required")

        if not agent.name or not agent.name.strip():
            issues.append(f"Agent '{agent.id}': name is required")

        if not agent.persona or len(agent.persona) < 10:
            issues.append(
                f"Agent '{agent.id}': persona is too short "
                f"(min 10 chars recommended)"
            )

        # 知识来源
        if not agent.knowledge_sources and not agent.faq:
            issues.append(
                f"Agent '{agent.id}': no knowledge_sources or faq defined"
            )

        # 禁止话题不应为空字符串
        agent.forbidden_topics[:] = [
            t for t in agent.forbidden_topics if t.strip()
        ]

        return issues

    def validate_scene(
        self, scene: Scene, agents: dict[str, Agent] | None = None
    ) -> list[str]:
        """校验场景逻辑完整性。

        Args:
            scene: 待校验的场景
            agents: 可用的 Agent 映射

        Returns:
            问题列表
        """
        issues = []

        if not scene.id:
            issues.append("Scene id is required")
            return issues

        if not scene.name:
            issues.append(f"Scene '{scene.id}': name is required")

        if not scene.objective:
            issues.append(
                f"Scene '{scene.id}': objective is recommended"
            )

        # 流程步骤
        if not scene.flow:
            issues.append(f"Scene '{scene.id}': no flow steps defined")
            return issues

        # 步骤 ID 唯一性
        step_ids = [s.step_id for s in scene.flow]
        if len(step_ids) != len(set(step_ids)):
            issues.append(f"Scene '{scene.id}': duplicate step_ids found")

        # 参与者在 agents 中
        if agents:
            for p in scene.participants:
                if p.agent_id not in agents:
                    issues.append(
                        f"Scene '{scene.id}': participant agent "
                        f"'{p.agent_id}' not found in provided agents"
                    )

        # entry_agent_id 在 participants 中
        if scene.entry_agent_id:
            participant_ids = {p.agent_id for p in scene.participants}
            if scene.entry_agent_id not in participant_ids:
                issues.append(
                    f"Scene '{scene.id}': entry_agent_id "
                    f"'{scene.entry_agent_id}' not in participants"
                )

        return issues

    def check_forbidden_topics(
        self,
        answer: str,
        forbidden_topics: list[str],
    ) -> list[str]:
        """检查回答是否包含禁止词。

        Args:
            answer: Agent 的回答
            forbidden_topics: 禁止话题列表

        Returns:
            命中的禁止词列表
        """
        hits = []
        answer_lower = answer.lower()
        for topic in forbidden_topics:
            if topic.lower() in answer_lower:
                hits.append(topic)
        return hits

    def check_first_person(self, answer: str) -> bool:
        """检查是否使用第一人称。

        检查中文"我"、英文"I"等。

        Args:
            answer: Agent 的回答

        Returns:
            是否使用了第一人称
        """
        patterns = [
            r"我(?!们)",        # "我" 但不是 "我们"
            r"\bI\b",
            r"\bme\b",
            r"\bmy\b",
            r"本人",
        ]
        for pat in patterns:
            if re.search(pat, answer):
                return True
        return False


def validate_agent(agent: Agent) -> list[str]:
    """校验 Agent（便捷函数）"""
    validator = ContentValidator()
    return validator.validate_agent(agent)


def validate_scene(
    scene: Scene,
    agents: dict[str, Agent] | None = None,
) -> list[str]:
    """校验 Scene（便捷函数）"""
    validator = ContentValidator()
    return validator.validate_scene(scene, agents)
