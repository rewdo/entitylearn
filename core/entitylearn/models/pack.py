"""Pack 数据模型（Pydantic v2）"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from .agent import Agent
from .scene import Scene
from .test_case import TestSuite


class Author(BaseModel):
    """作者信息"""
    name: str = Field(..., description="作者名称")
    email: Optional[str] = Field(default=None, description="邮箱")
    url: Optional[str] = Field(default=None, description="个人主页")


class Entrypoints(BaseModel):
    """知识包入口路径配置"""
    agents: str = Field(default="agents", description="Agent 文件目录")
    scenes: str = Field(default="scenes", description="场景文件目录")
    knowledge: str = Field(default="knowledge", description="知识文档目录")
    tests: str = Field(default="tests", description="测试文件目录")


class PackMeta(BaseModel):
    """知识包的元数据"""

    id: str = Field(..., description="唯一标识符")
    name: str = Field(..., description="包名称")
    version: str = Field(default="0.1.0", description="语义版本号")
    description: str = Field(default="", description="包描述")
    domain: str = Field(default="general", description="领域: education/legal/medical/tech 等")
    language: str = Field(default="zh-CN", description="主要语言")
    authors: list[Author] = Field(default_factory=list, description="作者列表")
    license: str = Field(default="MIT", description="许可证")
    schema_version: str = Field(default="1.0", description="Schema 版本")

    entrypoints: Entrypoints = Field(
        default_factory=Entrypoints,
        description="包内资源入口路径",
    )
    tags: list[str] = Field(default_factory=list, description="标签")
    compatibility: dict[str, str] = Field(
        default_factory=dict, description="兼容性声明"
    )


class Pack(BaseModel):
    """完整的知识包"""

    meta: PackMeta = Field(..., description="包元数据")
    agents: list[Agent] = Field(default_factory=list, description="Agent 列表")
    scenes: list[Scene] = Field(default_factory=list, description="场景列表")
    tests: list[TestSuite] = Field(default_factory=list, description="测试套件")

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Pack":
        """从 YAML 文件加载 Pack 元数据。

        Args:
            path: pack.yaml 文件路径

        Returns:
            解析后的 Pack 对象（agents/scenes/tests 由 loader 填充）
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Pack YAML not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            raise ValueError(f"Empty pack YAML: {path}")

        # 解析 meta
        meta = PackMeta(**raw)

        # agents/scenes/tests 由 loader 从 entrypoints 加载
        return cls(meta=meta, agents=[], scenes=[], tests=[])

    @property
    def id(self) -> str:
        """快捷访问 pack id"""
        return self.meta.id

    @property
    def name(self) -> str:
        """快捷访问 pack name"""
        return self.meta.name

    def get_agent(self, agent_id: str) -> Agent | None:
        """按 ID 查找 Agent"""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None

    def get_scene(self, scene_id: str) -> Scene | None:
        """按 ID 查找 Scene"""
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None

    def get_agent_ids(self) -> set[str]:
        """获取所有 Agent ID 集合"""
        return {agent.id for agent in self.agents}

    def get_scene_ids(self) -> set[str]:
        """获取所有 Scene ID 集合"""
        return {scene.id for scene in self.scenes}
