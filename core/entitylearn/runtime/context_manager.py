"""上下文管理器"""

from __future__ import annotations

from typing import Optional

from ..models.scene import FlowStep


class ContextManager:
    """场景上下文管理器。

    管理当前场景的播放状态、已执行步骤和上下文摘要。
    """

    def __init__(self):
        self._steps: list[FlowStep] = []
        self._current_step_id: str | None = None
        self._scene_id: str | None = None
        self._scene_name: str = ""

    @property
    def current_step_id(self) -> str | None:
        """当前步骤 ID"""
        return self._current_step_id

    @property
    def step_count(self) -> int:
        """已播放步骤数"""
        return len(self._steps)

    def add_step(self, step: FlowStep) -> None:
        """记录一个已播放步骤。

        Args:
            step: 已执行的流程步骤
        """
        self._steps.append(step)
        self._current_step_id = step.step_id

    def get_context(self) -> dict:
        """获取当前上下文摘要。

        Returns:
            包含场景信息、已播放步骤摘要等
        """
        return {
            "scene_id": self._scene_id,
            "scene_name": self._scene_name,
            "current_step_id": self._current_step_id,
            "steps_played": self.step_count,
            "recent_steps": [
                {
                    "step_id": s.step_id,
                    "speaker": s.speaker,
                    "content_preview": s.content[:200] if s.content else "",
                    "type": s.type,
                }
                for s in self._steps[-5:]  # 最近 5 步
            ],
        }

    def get_history(self) -> list[dict]:
        """获取完整播放历史。

        Returns:
            所有已播放步骤的列表
        """
        return [
            {
                "step_id": s.step_id,
                "speaker": s.speaker,
                "content": s.content,
                "type": s.type,
                "source_refs": [ref.model_dump() for ref in s.source_refs],
            }
            for s in self._steps
        ]

    def reset(self) -> None:
        """重置上下文管理器"""
        self._steps.clear()
        self._current_step_id = None
        self._scene_id = None
        self._scene_name = ""

    def start_scene(self, scene_id: str, scene_name: str = "") -> None:
        """开始一个新场景。

        Args:
            scene_id: 场景 ID
            scene_name: 场景名称
        """
        self.reset()
        self._scene_id = scene_id
        self._scene_name = scene_name
