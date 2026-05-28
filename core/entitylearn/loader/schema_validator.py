"""Schema 校验器"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..models.pack import Pack

logger = logging.getLogger(__name__)


class SchemaValidator:
    """知识包 Schema 校验器。

    负责校验知识包的完整性、交叉引用和文件可用性。
    """

    def __init__(self, pack_path: str | Path | None = None):
        """初始化校验器。

        Args:
            pack_path: 知识包根目录（用于校验文件引用）
        """
        self.pack_path = Path(pack_path) if pack_path else None

    def validate(self, pack: Pack) -> list[str]:
        """校验知识包的完整性。

        Args:
            pack: 待校验的知识包

        Returns:
            错误信息列表，空列表表示通过校验
        """
        errors: list[str] = []

        # 1. 基础校验
        errors.extend(self._validate_meta(pack))

        # 2. 交叉引用校验
        errors.extend(self._validate_cross_references(pack))

        # 3. 文件引用校验
        if self.pack_path:
            errors.extend(self._validate_file_references(pack))

        # 4. Scene 逻辑校验
        errors.extend(self._validate_scenes(pack))

        return errors

    def _validate_meta(self, pack: Pack) -> list[str]:
        """校验 Pack 元数据"""
        errors = []
        meta = pack.meta

        if not meta.id or not meta.id.strip():
            errors.append("Pack meta.id is required and must not be empty")

        if not meta.name or not meta.name.strip():
            errors.append("Pack meta.name is required and must not be empty")

        # 检查重复 ID
        agent_ids = [a.id for a in pack.agents]
        scene_ids = [s.id for s in pack.scenes]
        test_ids = [t.id for t in pack.tests]

        seen_agent = set()
        for aid in agent_ids:
            if aid in seen_agent:
                errors.append(f"Duplicate agent ID: {aid}")
            seen_agent.add(aid)

        seen_scene = set()
        for sid in scene_ids:
            if sid in seen_scene:
                errors.append(f"Duplicate scene ID: {sid}")
            seen_scene.add(sid)

        seen_test = set()
        for tid in test_ids:
            if tid in seen_test:
                errors.append(f"Duplicate test suite ID: {tid}")
            seen_test.add(tid)

        return errors

    def _validate_cross_references(self, pack: Pack) -> list[str]:
        """校验交叉引用完整性"""
        errors = []
        agent_ids = {a.id for a in pack.agents}
        scene_ids = {s.id for s in pack.scenes}
        all_step_ids: set[str] = set()

        # 收集所有 step_id
        for scene in pack.scenes:
            all_step_ids.update(scene.get_step_ids())

        # 校验 Scene.participants 引用的 agent 是否存在
        for scene in pack.scenes:
            for participant in scene.participants:
                if participant.agent_id not in agent_ids:
                    errors.append(
                        f"Scene '{scene.id}' references unknown agent "
                        f"'{participant.agent_id}' in participants"
                    )

        # 校验 Scene.entry_agent_id
        for scene in pack.scenes:
            if scene.entry_agent_id and scene.entry_agent_id not in agent_ids:
                errors.append(
                    f"Scene '{scene.id}' entry_agent_id '{scene.entry_agent_id}' "
                    f"not found in agents"
                )

        # 校验 Breakpoint step_id 存在于 flow 中
        for scene in pack.scenes:
            for bp in scene.breakpoints:
                if bp.step_id not in all_step_ids:
                    errors.append(
                        f"Scene '{scene.id}' breakpoint step_id "
                        f"'{bp.step_id}' not found in flow steps"
                    )

        # 校验 FlowStep.next_step_id 能找到
        for scene in pack.scenes:
            for step in scene.flow:
                if step.next_step_id and step.next_step_id not in all_step_ids:
                    errors.append(
                        f"Scene '{scene.id}' flow step '{step.step_id}' "
                        f"next_step_id '{step.next_step_id}' not found"
                    )

        # 校验 FlowStep.speaker 引用的 agent
        for scene in pack.scenes:
            for step in scene.flow:
                if step.speaker is None:
                    continue
                if step.speaker not in ("system", "") and step.speaker not in agent_ids:
                    errors.append(
                        f"Scene '{scene.id}' step '{step.step_id}' "
                        f"speaker '{step.speaker}' not found in agents"
                    )

        # 校验 TestSuite.target_id 存在
        for test in pack.tests:
            if test.target_type == "agent" and test.target_id not in agent_ids:
                errors.append(
                    f"TestSuite '{test.id}' target agent "
                    f"'{test.target_id}' not found"
                )
            elif test.target_type == "scene" and test.target_id not in scene_ids:
                errors.append(
                    f"TestSuite '{test.id}' target scene "
                    f"'{test.target_id}' not found"
                )

        return errors

    def _validate_file_references(self, pack: Pack) -> list[str]:
        """校验知识来源文件是否存在"""
        errors = []

        if not self.pack_path:
            return errors

        # 校验 Agent.knowledge_sources 文件
        for agent in pack.agents:
            for ks in agent.knowledge_sources:
                src_path = (self.pack_path / ks.path).resolve()
                if not src_path.exists():
                    errors.append(
                        f"Agent '{agent.id}' knowledge source "
                        f"'{ks.path}' not found at {src_path}"
                    )

        # 校验 Scene source_refs
        for scene in pack.scenes:
            for step in scene.flow:
                for ref in step.source_refs:
                    ref_path = (self.pack_path / ref.path).resolve()
                    if not ref_path.exists():
                        errors.append(
                            f"Scene '{scene.id}' step '{step.step_id}' "
                            f"source ref '{ref.path}' not found at {ref_path}"
                        )

        return errors

    def _validate_scenes(self, pack: Pack) -> list[str]:
        """校验场景逻辑"""
        errors = []

        for scene in pack.scenes:
            # 至少有一个步骤
            if not scene.flow:
                errors.append(f"Scene '{scene.id}' has no flow steps")
                continue

            # 检查第一个步骤的 speaker
            first_step = scene.flow[0]
            if scene.entry_agent_id and pack.agents:
                # exit_agent_id 如果设置，建议第一步骤由 entry_agent 发言
                pass

        return errors


def validate_pack(pack: Pack, pack_path: str | Path | None = None) -> list[str]:
    """校验知识包（便捷函数）。

    Args:
        pack: 待校验的知识包
        pack_path: 知识包根目录

    Returns:
        错误信息列表
    """
    validator = SchemaValidator(pack_path)
    return validator.validate(pack)
