"""Scene 数据模型（Pydantic v2）"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    """知识来源引用"""

    path: str = Field(..., description="引用的文件路径")
    quote: str = Field(default="", description="引用内容摘录")
    section: str = Field(default="", description="引用章节")


class FlowStep(BaseModel):
    """场景中的一个播放步骤"""

    step_id: str = Field(..., description="步骤唯一标识")
    type: str = Field(default="narration", description="步骤类型: narration/dialogue/question/breakpoint/visual")
    speaker: str = Field(default="system", description="说话人: system 或 agent_id")
    content: str = Field(default="", description="步骤内容")
    source_refs: list[SourceRef] = Field(
        default_factory=list, description="引用的来源"
    )
    visual_hint: str = Field(default="", description="可视化提示（图片/图表引用）")
    actions: list[str] = Field(default_factory=list, description="可选动作")
    next_step_id: str | None = Field(default=None, description="下一步骤 ID")


class Participant(BaseModel):
    """场景参与者"""

    agent_id: str = Field(..., description="参与的 Agent ID")
    role_in_scene: str = Field(default="speaker", description="在场景中的角色")
    speaking_style: str = Field(default="", description="说话风格提示")


class Breakpoint(BaseModel):
    """交互断点"""

    step_id: str = Field(..., description="断点所在的步骤 ID")
    prompt: str = Field(default="", description="提示用户输入的文字")
    allowed_agents: list[str] = Field(
        default_factory=list, description="允许此断点触发哪些 Agent 回答"
    )
    user_input_mode: str = Field(
        default="free_text",
        description="用户输入模式: free_text/multiple_choice",
    )


class SceneMetadata(BaseModel):
    """场景元数据"""

    difficulty: str = Field(default="beginner", description="难度: beginner/intermediate/advanced")
    estimated_duration_min: int = Field(default=10, description="预计时长（分钟）")
    tags: list[str] = Field(default_factory=list, description="标签")


class Scene(BaseModel):
    """教学场景"""

    id: str = Field(..., description="场景唯一标识")
    name: str = Field(..., description="场景名称")
    description: str = Field(default="", description="场景描述")
    objective: str = Field(default="", description="教学目标")
    participants: list[Participant] = Field(
        default_factory=list, description="参与者列表"
    )
    entry_agent_id: str | None = Field(
        default=None, description="入场角色 ID（第一个说话的）"
    )
    breakpoints: list[Breakpoint] = Field(
        default_factory=list, description="交互断点列表"
    )
    flow: list[FlowStep] = Field(
        default_factory=list, description="场景流程步骤列表"
    )
    metadata: SceneMetadata = Field(
        default_factory=SceneMetadata, description="场景元数据"
    )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Scene":
        """从 YAML 文件加载 Scene 定义。

        Args:
            path: scene YAML 文件路径

        Returns:
            解析后的 Scene 对象
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Scene YAML not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            raise ValueError(f"Empty scene YAML: {path}")

        # 处理嵌套对象
        if "participants" in raw:
            raw["participants"] = [
                Participant(**p) if isinstance(p, dict) else p
                for p in raw["participants"]
            ]

        if "breakpoints" in raw:
            raw["breakpoints"] = [
                Breakpoint(**bp) if isinstance(bp, dict) else bp
                for bp in raw["breakpoints"]
            ]

        if "flow" in raw:
            raw["flow"] = [
                FlowStep(**step) if isinstance(step, dict) else step
                for step in raw["flow"]
            ]
            # 处理嵌套 source_refs
            for i, step in enumerate(raw["flow"]):
                if isinstance(step, FlowStep) and step.source_refs:
                    step.source_refs = [
                        SourceRef(**sr) if isinstance(sr, dict) else sr
                        for sr in step.source_refs
                    ]

        if "metadata" in raw and isinstance(raw["metadata"], dict):
            raw["metadata"] = SceneMetadata(**raw["metadata"])

        return cls(**raw)

    def get_step(self, step_id: str) -> FlowStep | None:
        """按 step_id 查找步骤"""
        for step in self.flow:
            if step.step_id == step_id:
                return step
        return None

    def get_first_step(self) -> FlowStep | None:
        """获取第一个步骤"""
        return self.flow[0] if self.flow else None

    def get_step_ids(self) -> set[str]:
        """获取所有步骤 ID"""
        return {step.step_id for step in self.flow}
