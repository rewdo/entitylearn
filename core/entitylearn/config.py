"""配置管理模块"""

import os
from pathlib import Path


# 默认路径：基于项目根目录
_DEFAULT_ROOT = Path(__file__).resolve().parent.parent.parent  # core/ -> entitylearn root


def get_default_packs_dir() -> Path:
    """获取默认知识包目录"""
    env_packs = os.environ.get("ENTITYLEARN_PACKS_DIR")
    if env_packs:
        return Path(env_packs)
    return _DEFAULT_ROOT / "packs"


def get_default_schema_dir() -> Path:
    """获取默认 Schema 目录"""
    env_schema = os.environ.get("ENTITYLEARN_SCHEMA_DIR")
    if env_schema:
        return Path(env_schema)
    return _DEFAULT_ROOT / "schemas"


def get_default_data_dir() -> Path:
    """获取默认数据目录"""
    env_data = os.environ.get("ENTITYLEARN_DATA_DIR")
    if env_data:
        return Path(env_data)
    return _DEFAULT_ROOT / "data"


# 模块级配置实例
PACKS_DIR: Path = get_default_packs_dir()
SCHEMA_DIR: Path = get_default_schema_dir()
DATA_DIR: Path = get_default_data_dir()


__all__ = [
    "PACKS_DIR",
    "SCHEMA_DIR",
    "DATA_DIR",
    "get_default_packs_dir",
    "get_default_schema_dir",
    "get_default_data_dir",
]
