"""测试用例数据模型（Pydantic v2）"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """单个测试用例"""

    input: str = Field(..., description="输入问题")
    expected_keywords: list[str] = Field(
        default_factory=list, description="期望回答中包含的关键词"
    )
    forbidden_keywords: list[str] = Field(
        default_factory=list, description="禁止出现的关键词"
    )
    expected_sources: list[str] = Field(
        default_factory=list, description="期望引用的来源文件"
    )
    max_answer_length: int | None = Field(
        default=None, description="最大回答长度（字符）"
    )
    must_be_first_person: bool = Field(
        default=False, description="必须使用第一人称"
    )
    must_include_uncertainty_if_no_source: bool = Field(
        default=False, description="无来源时须表达不确定"
    )


class TestSuite(BaseModel):
    """测试套件"""

    id: str = Field(..., description="测试套件唯一标识")
    name: str = Field(default="", description="测试套件名称")
    target_type: str = Field(
        default="agent", description="测试目标类型: agent/scene"
    )
    target_id: str = Field(..., description="测试目标 ID（Agent 或 Scene ID）")
    test_cases: list[TestCase] = Field(
        default_factory=list, description="测试用例列表"
    )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "TestSuite":
        """从 YAML 文件加载 TestSuite。

        Args:
            path: test YAML 文件路径

        Returns:
            解析后的 TestSuite 对象
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Test YAML not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if raw is None:
            raise ValueError(f"Empty test YAML: {path}")

        if "test_cases" in raw:
            raw["test_cases"] = [
                TestCase(**tc) if isinstance(tc, dict) else tc
                for tc in raw["test_cases"]
            ]

        return cls(**raw)
