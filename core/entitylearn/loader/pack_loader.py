"""知识包加载器"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from ..models.pack import Pack
from ..models.agent import Agent
from ..models.scene import Scene
from ..models.test_case import TestSuite

logger = logging.getLogger(__name__)


class PackLoader:
    """知识包加载器。

    负责扫描 packs/ 目录，解析 pack.yaml 和 entrypoints 下的所有文件，
    返回完整的 Pack 对象。
    """

    def __init__(self, packs_dir: str | Path | None = None):
        if packs_dir is None:
            from ..config import PACKS_DIR
            packs_dir = PACKS_DIR
        self.packs_dir = Path(packs_dir)

    def load_all(self) -> list[Pack]:
        packs = []
        if not self.packs_dir.exists():
            logger.warning(f"Packs directory not found: {self.packs_dir}")
            return packs

        for item in sorted(self.packs_dir.iterdir()):
            if item.is_dir():
                pack_yaml = item / "pack.yaml"
                if pack_yaml.exists():
                    try:
                        pack = self.load(str(item))
                        packs.append(pack)
                    except Exception as e:
                        logger.error(f"Failed to load pack from {item}: {e}")
        return packs

    def load(self, pack_path: str | Path) -> Pack:
        pack_path = Path(pack_path)
        if not pack_path.exists():
            raise FileNotFoundError(f"Pack directory not found: {pack_path}")

        pack_yaml = pack_path / "pack.yaml"
        if not pack_yaml.exists():
            raise FileNotFoundError(f"pack.yaml not found in: {pack_path}")

        # 1. 解析 pack.yaml
        pack = Pack.from_yaml(str(pack_yaml))

        # 2. 扫描 entrypoints 加载 agents/scenes/tests
        ep = pack.meta.entrypoints
        ep_dirs = {
            "agents": ep.agents,
            "scenes": ep.scenes,
            "tests": ep.tests,
        }
        for _kind, ep_dir in ep_dirs.items():
            entrypoint_path = pack_path / ep_dir
            if entrypoint_path.is_dir():
                self._load_from_dir(entrypoint_path, pack)
            elif entrypoint_path.is_file():
                self._load_from_file(entrypoint_path, pack)

        return pack

    def _load_from_dir(self, dir_path: Path, pack: Pack) -> None:
        for yaml_file in sorted(dir_path.rglob("*.yaml")):
            self._load_yaml_file(yaml_file, pack)
        for yaml_file in sorted(dir_path.rglob("*.yml")):
            self._load_yaml_file(yaml_file, pack)

    def _load_from_file(self, file_path: Path, pack: Pack) -> None:
        self._load_yaml_file(file_path, pack)

    def _load_yaml_file(self, file_path: Path, pack: Pack) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)

            if raw is None or not isinstance(raw, dict):
                return

            kind = raw.get("kind", "").lower()

            if kind in ("agent",):
                agent = Agent.from_yaml(str(file_path))
                pack.agents.append(agent)
                logger.debug(f"Loaded agent: {agent.id} from {file_path}")
            elif kind in ("scene",):
                scene = Scene.from_yaml(str(file_path))
                pack.scenes.append(scene)
                logger.debug(f"Loaded scene: {scene.id} from {file_path}")
            elif kind in ("test", "test_suite", "testsuite"):
                test_suite = TestSuite.from_yaml(str(file_path))
                pack.tests.append(test_suite)
                logger.debug(f"Loaded test suite: {test_suite.id} from {file_path}")
            else:
                # 尝试根据内容特征自动判断
                if "persona" in raw or "voice" in raw or "faq" in raw:
                    agent = Agent.from_yaml(str(file_path))
                    pack.agents.append(agent)
                    logger.debug(f"Inferred agent: {agent.id} from {file_path}")
                elif "flow" in raw and isinstance(raw.get("flow"), list):
                    scene = Scene.from_yaml(str(file_path))
                    pack.scenes.append(scene)
                    logger.debug(f"Inferred scene: {scene.id} from {file_path}")
                elif "test_cases" in raw:
                    test_suite = TestSuite.from_yaml(str(file_path))
                    pack.tests.append(test_suite)
                    logger.debug(f"Inferred test suite: {test_suite.id} from {file_path}")
        except Exception as e:
            logger.error(f"Failed to parse YAML file {file_path}: {e}")


def load_pack(pack_path: str | Path) -> Pack:
    loader = PackLoader()
    pack_path = Path(pack_path)
    if pack_path.is_file():
        pack_path = pack_path.parent
    return loader.load(str(pack_path))


def load_all_packs(packs_dir: str | Path | None = None) -> list[Pack]:
    loader = PackLoader(packs_dir)
    return loader.load_all()
