"""场景运行器"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, Optional

from pydantic import BaseModel, Field

from ..models.scene import Scene, FlowStep, Breakpoint, SourceRef
from ..models.agent import Agent
from .agent_runtime import AgentRuntime, Answer
from .context_manager import ContextManager

logger = logging.getLogger(__name__)


class SceneStep(BaseModel):
    """场景播放中的一步"""

    step_id: str = Field(..., description="步骤 ID")
    speaker: str = Field(default="system", description="说话人")
    content: str = Field(default="", description="内容")
    type: str = Field(default="narration", description="步骤类型")
    source_refs: list[dict] = Field(default_factory=list, description="来源引用")
    is_breakpoint: bool = Field(default=False, description="是否交互断点")
    breakpoint_prompt: str = Field(default="", description="断点提示")


class SceneRunner:
    """场景运行器。

    支持逐步播放场景、断点暂停、用户交互。
    """

    def __init__(
        self,
        agents: dict[str, Agent] | None = None,
        pack_path: str | Path | None = None,
    ):
        """初始化场景运行器。

        Args:
            agents: Agent ID → Agent 映射
            pack_path: 知识包根目录
        """
        self._agents = agents or {}
        self.pack_path = Path(pack_path) if pack_path else None
        self._agent_runtime = AgentRuntime(pack_path)
        self._context = ContextManager()

        # 当前场景状态
        self._scene: Scene | None = None
        self._step_index: int = 0
        self._breakpoints: dict[str, Breakpoint] = {}
        self._paused: bool = False
        self._user_input_queue: list[str] = []

    @property
    def context(self) -> ContextManager:
        """获取上下文管理器"""
        return self._context

    @property
    def current_scene(self) -> Scene | None:
        """当前场景"""
        return self._scene

    @property
    def is_paused(self) -> bool:
        """是否暂停（等待用户输入）"""
        return self._paused

    def load_scene(self, scene: Scene) -> None:
        """加载一个场景。

        Args:
            scene: 要播放的场景
        """
        self._scene = scene
        self._step_index = 0
        self._paused = False
        self._user_input_queue.clear()

        # 建立断点索引
        self._breakpoints = {}
        for bp in scene.breakpoints:
            self._breakpoints[bp.step_id] = bp

        # 初始化上下文
        self._context.start_scene(scene.id, scene.name)

    def run_scene(
        self,
        scene: Scene,
        agents: dict[str, Agent] | None = None,
    ) -> Generator[SceneStep, Optional[str], None]:
        """逐步播放场景（Generator 模式）。

        每次 yield 一个 SceneStep。遇到断点时暂停，等待通过 send()
        传入用户输入后继续。

        Args:
            scene: 要播放的场景
            agents: Agent 映射（可选，用于覆盖初始化时的 agents）

        Yields:
            SceneStep: 每一步的内容
        """
        if agents:
            self._agents = agents
        self.load_scene(scene)

        if not scene.flow:
            logger.warning(f"Scene '{scene.id}' has no flow steps")
            return

        # 确定第一个 speaker
        first_speaker = scene.flow[0].speaker
        if first_speaker == "system" and scene.entry_agent_id:
            first_speaker = scene.entry_agent_id

        while self._step_index < len(scene.flow):
            step = scene.flow[self._step_index]

            # 检查是否是断点
            bp = self._breakpoints.get(step.step_id)
            if bp and self._step_index > 0:
                breakpoint_step = SceneStep(
                    step_id=step.step_id,
                    speaker=step.speaker,
                    content=bp.prompt or step.content,
                    type="breakpoint",
                    source_refs=[],
                    is_breakpoint=True,
                    breakpoint_prompt=bp.prompt,
                )
                self._context.add_step(step)
                self._paused = True

                # 等待用户输入
                user_input = yield breakpoint_step
                if user_input:
                    self._paused = False
                    # 处理用户输入——用相关 Agent 回答
                    answer_step = self._handle_user_input(
                        scene, bp, user_input
                    )
                    if answer_step:
                        yield answer_step
                self._step_index += 1
                continue

            # 普通步骤
            scene_step = SceneStep(
                step_id=step.step_id,
                speaker=step.speaker,
                content=step.content,
                type=step.type,
                source_refs=[
                    ref.model_dump() for ref in step.source_refs
                ],
            )
            self._context.add_step(step)
            self._step_index += 1
            yield scene_step

            # 如果设定了 next_step_id，跳转
            if step.next_step_id:
                target_idx = self._find_step_index(scene, step.next_step_id)
                if target_idx is not None:
                    self._step_index = target_idx

    def _handle_user_input(
        self,
        scene: Scene,
        bp: Breakpoint,
        user_input: str,
    ) -> SceneStep | None:
        """处理用户在断点处的输入"""
        # 确定由哪些 agent 回答
        allowed = bp.allowed_agents or [
            p.agent_id for p in scene.participants
        ]

        for agent_id in allowed:
            agent = self._agents.get(agent_id)
            if agent:
                answer: Answer = self._agent_runtime.answer(
                    agent=agent,
                    question=user_input,
                    context=self._context.get_context(),
                )
                if answer.confidence > 0:
                    return SceneStep(
                        step_id=f"{bp.step_id}_response_{agent_id}",
                        speaker=agent_id,
                        content=answer.content,
                        type="dialogue",
                        source_refs=[
                            {"path": s, "quote": "", "section": ""}
                            for s in answer.sources
                        ],
                    )

        # 无 agent 匹配或无内容
        return SceneStep(
            step_id=f"{bp.step_id}_response",
            speaker="system",
            content="感谢你的提问，但目前没有足够的信息来回答。",
            type="narration",
        )

    def next(self) -> SceneStep | None:
        """获取下一个步骤（非 Generator 模式）。

        Returns:
            下一步的 SceneStep，或 None 表示结束
        """
        if not self._scene:
            return None

        if self._step_index >= len(self._scene.flow):
            return None

        # 检查是否在断点处暂停
        if self._paused:
            return None

        step = self._scene.flow[self._step_index]
        bp = self._breakpoints.get(step.step_id)

        if bp and self._step_index > 0:
            self._paused = True
            scene_step = SceneStep(
                step_id=step.step_id,
                speaker=step.speaker,
                content=bp.prompt or step.content,
                type="breakpoint",
                is_breakpoint=True,
                breakpoint_prompt=bp.prompt,
            )
            self._context.add_step(step)
            return scene_step

        scene_step = SceneStep(
            step_id=step.step_id,
            speaker=step.speaker,
            content=step.content,
            type=step.type,
            source_refs=[ref.model_dump() for ref in step.source_refs],
        )
        self._context.add_step(step)

        # 处理 next_step_id
        if step.next_step_id:
            target_idx = self._find_step_index(self._scene, step.next_step_id)
            if target_idx is not None:
                self._step_index = target_idx
            else:
                self._step_index += 1
        else:
            self._step_index += 1

        return scene_step

    def ask(self, question: str) -> SceneStep | None:
        """在断点处提问。

        Args:
            question: 用户问题

        Returns:
            回答的 SceneStep
        """
        if not self._paused or not self._scene:
            logger.warning("Not at a breakpoint")
            return None

        current_step_id = self._context.current_step_id
        if not current_step_id:
            return None

        bp = self._breakpoints.get(current_step_id)
        if not bp:
            return None

        self._paused = False
        result = self._handle_user_input(self._scene, bp, question)
        return result

    def _find_step_index(self, scene: Scene, step_id: str) -> int | None:
        """查找步骤索引"""
        for i, step in enumerate(scene.flow):
            if step.step_id == step_id:
                return i
        return None
