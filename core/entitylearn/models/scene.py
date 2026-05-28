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
    speaker: str | None = Field(default=None, description="说话人: null 或 agent_id")
    content: str = Field(default="", description="步骤内容")
    source_refs: list[SourceRef] = Field(
        default_factory=list, description="引用的来源"
    )
    visual_hint: str = Field(default="", description="可视化提示（图片/图表引用）")
    actions: list[dict] = Field(default_factory=list, description="可选动作")
    next_step_id: str | None = Field(default=None, description="下一步骤 ID")

    @property
    def is_breakpoint(self) -> bool:
        return self.type == "breakpoint"


class Participant(BaseModel):
    """场景参与者"""

    agent_id: str = Field(..., description="参与的 Agent ID")
    display_name: str = Field(default="", description="展示名称")
    role_in_scene: str = Field(default="speaker", description="在场景中的角色")
    speaking_style: str = Field(default="", description="说话风格提示")


class Breakpoint(BaseModel):
    """交互断点"""

    step_id: str = Field(..., description="断点所在的步骤 ID")
    label: str = Field(default="", description="断点标签")
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
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Scene YAML not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            raise ValueError(f"Empty scene YAML: {path}")

        # 归一化：participants 的 agent -> agent_id
        if "participants" in raw:
            for p in raw["participants"]:
                if isinstance(p, dict) and "agent" in p and "agent_id" not in p:
                    p["agent_id"] = p.pop("agent")

        # 归一化：flow 的 step -> step_id, speaker null -> None, source_refs 字符串 -> 对象
        if "flow" in raw:
            for step in raw["flow"]:
                if isinstance(step, dict):
                    if "step" in step and "step_id" not in step:
                        step["step_id"] = str(step.pop("step"))
                    if step.get("speaker") is None:
                        step["speaker"] = None
                    # 转换字符串 source_refs 为 SourceRef 对象
                    if "source_refs" in step:
                        step["source_refs"] = [
                            SourceRef(path=sr) if isinstance(sr, str) else SourceRef(**sr)
                            for sr in step["source_refs"]
                        ]
                    # 处理 actions
                    if "actions" in step and step["actions"] is None:
                        step["actions"] = []

        # 归一化：breakpoints 的 step -> step_id
        if "breakpoints" in raw:
            for bp in raw["breakpoints"]:
                if isinstance(bp, dict) and "step" in bp and "step_id" not in bp:
                    bp["step_id"] = str(bp.pop("step"))

        # 归一化：difficulty -> metadata.difficulty, estimated_duration -> metadata
        meta_fields = {}
        if "difficulty" in raw:
            meta_fields["difficulty"] = raw.pop("difficulty")
        if "estimated_duration" in raw:
            dur = raw.pop("estimated_duration")
            if isinstance(dur, str) and dur.endswith("m"):
                meta_fields["estimated_duration_min"] = int(dur[:-1])
            elif isinstance(dur, (int, float)):
                meta_fields["estimated_duration_min"] = int(dur)
        if "tags" in raw and isinstance(raw.get("tags"), list):
            meta_fields["tags"] = raw.pop("tags")
        if meta_fields and "metadata" not in raw:
            raw["metadata"] = meta_fields

        # 移除不需要的字段
        for key in ["pack_id", "domain"]:
            raw.pop(key, None)

        return cls(**raw)

    def get_step(self, step_id: str) -> FlowStep | None:
        for step in self.flow:
            if step.step_id == step_id:
                return step
        return None

    def get_first_step(self) -> FlowStep | None:
        return self.flow[0] if self.flow else None

    def get_step_ids(self) -> set[str]:
        return {step.step_id for step in self.flow}
