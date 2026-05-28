"""引用校验器"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..models.pack import Pack
from ..models.scene import Scene

logger = logging.getLogger(__name__)


class ReferenceChecker:
    """引用校验器。

    校验知识包中所有文件引用和来源引用的完整性。
    """

    def __init__(self, pack_path: str | Path | None = None):
        """初始化引用校验器。

        Args:
            pack_path: 知识包根目录
        """
        self.pack_path = Path(pack_path) if pack_path else None

    def check_source_exists(self, path: str) -> bool:
        """检查引用文件是否存在。

        Args:
            path: 相对于 pack_path 的文件路径

        Returns:
            文件是否存在
        """
        if not self.pack_path:
            return True  # 无 pack_path 时不阻塞

        full_path = self.pack_path / path
        return full_path.exists()

    def check_all_sources(self, pack: Pack) -> list[str]:
        """检查知识包中所有引用。

        Args:
            pack: 待检查的知识包

        Returns:
            缺失引用的错误列表
        """
        errors = []

        if not self.pack_path:
            return errors

        # 检查 Agent.knowledge_sources
        for agent in pack.agents:
            for ks in agent.knowledge_sources:
                if not self.check_source_exists(ks.path):
                    errors.append(
                        f"Agent '{agent.id}': knowledge source "
                        f"'{ks.path}' not found"
                    )

        # 检查 Scene.source_refs
        for scene in pack.scenes:
            scene_errors = self.validate_sources(scene)
            errors.extend(scene_errors)

        return errors

    def validate_sources(self, scene: Scene) -> list[str]:
        """校验单个场景的所有 source_refs。

        Args:
            scene: 待校验的场景

        Returns:
            缺失引用的错误列表
        """
        errors = []

        if not self.pack_path:
            return errors

        for step in scene.flow:
            for ref in step.source_refs:
                if not self.check_source_exists(ref.path):
                    errors.append(
                        f"Scene '{scene.id}' step '{step.step_id}': "
                        f"source ref '{ref.path}' not found"
                    )

        return errors
