"""Agent 数据模型（Pydantic v2）"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class KnowledgeSource(BaseModel):
    """知识来源"""

    path: str = Field(..., description="知识文档相对路径")
    type: str = Field(default="markdown", description="文档类型: markdown/txt/yaml")
    title: str = Field(default="", description="文档标题")
    note: str = Field(default="", description="备注")


class FAQ(BaseModel):
    """常见问题"""

    question: str = Field(..., description="问题")
    answer: str = Field(..., description="回答")
    sources: list[str] = Field(default_factory=list, description="来源引用路径")


class Scope(BaseModel):
    """回答范围"""

    allowed_topics: list[str] = Field(
        default_factory=list, description="允许回答的话题列表"
    )
    disallowed_topics: list[str] = Field(
        default_factory=list, description="禁止回答的话题列表"
    )


class StyleGuide(BaseModel):
    """风格指南"""

    tone: str = Field(default="formal", description="语气: formal/casual/educational")
    length: str = Field(default="medium", description="回答长度: short/medium/long")
    mention_limits: dict[str, int] = Field(
        default_factory=dict,
        description="提及次数限制，如 {'name': 3}",
    )


class Agent(BaseModel):
    """角色 Agent"""

    id: str = Field(..., description="唯一标识符")
    name: str = Field(..., description="角色名称")
    description: str = Field(default="", description="角色描述")
    role: str = Field(default="角色", description="角色类型")
    persona: str = Field(default="", description="人设完整描述")
    voice: str = Field(default="中性", description="说话风格")
    first_person: bool = Field(default=True, description="是否使用第一人称")

    responsibilities: list[str] = Field(
        default_factory=list, description="职责列表"
    )
    knowledge_sources: list[KnowledgeSource] = Field(
        default_factory=list, description="知识来源列表"
    )
    forbidden_topics: list[str] = Field(
        default_factory=list, description="禁止讨论的话题"
    )
    scope: Scope = Field(default_factory=Scope, description="回答范围")
    faq: list[FAQ] = Field(default_factory=list, description="常见问题列表")

    style_guide: StyleGuide = Field(
        default_factory=StyleGuide, description="风格指南"
    )
    metadata: dict = Field(default_factory=dict, description="自定义元数据")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Agent":
        """从 YAML 文件加载 Agent 定义。

        Args:
            path: agent YAML 文件路径

        Returns:
            解析后的 Agent 对象
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Agent YAML not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            raise ValueError(f"Empty agent YAML: {path}")

        # 处理嵌套对象
        if "knowledge_sources" in raw:
            raw["knowledge_sources"] = [
                KnowledgeSource(**ks) if isinstance(ks, dict) else KnowledgeSource(path=ks)
                for ks in raw["knowledge_sources"]
            ]

        if "faq" in raw:
            raw["faq"] = [
                FAQ(**faq) if isinstance(faq, dict) else faq
                for faq in raw["faq"]
            ]

        if "scope" in raw and isinstance(raw["scope"], dict):
            raw["scope"] = Scope(**raw["scope"])

        if "style_guide" in raw and isinstance(raw["style_guide"], dict):
            raw["style_guide"] = StyleGuide(**raw["style_guide"])

        return cls(**raw)
