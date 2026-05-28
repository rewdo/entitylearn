"""检索器

封装 KnowledgeIndexer 提供便捷检索接口。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from ..models.agent import Agent
from .indexer import KnowledgeIndexer, SearchResult

logger = logging.getLogger(__name__)


class Retriever:
    """知识检索器。

    封装索引和检索逻辑，提供面向 Agent 的便捷接口。
    """

    def __init__(self, pack_path: str | Path | None = None):
        """初始化检索器。

        Args:
            pack_path: 知识包根目录
        """
        self.pack_path = Path(pack_path) if pack_path else None
        self._indexer = KnowledgeIndexer()
        self._indexed = False

    def ensure_indexed(self) -> None:
        """确保已建立索引"""
        if not self._indexed and self.pack_path:
            count = self._indexer.index_knowledge(self.pack_path)
            self._indexed = True
            logger.info(f"Indexed {count} documents from {self.pack_path}")

    def retrieve(
        self,
        query: str,
        agent: Agent | None = None,
        top_k: int = 3,
    ) -> list[SearchResult]:
        """检索最相关的知识片段。

        Args:
            query: 搜索查询
            agent: 可选，关联的 Agent（用于过滤和增强）
            top_k: 返回结果数

        Returns:
            搜索结果列表
        """
        self.ensure_indexed()

        agent_id = agent.id if agent else None
        results = self._indexer.search(query, agent_id=agent_id, top_k=top_k)

        # 如果提供了 agent，优先返回 agent.knowledge_sources 中的文档
        if agent and agent.knowledge_sources:
            source_paths = {ks.path for ks in agent.knowledge_sources}
            prioritized = [r for r in results if r.path in source_paths]
            other = [r for r in results if r.path not in source_paths]
            results = prioritized + other

        return results[:top_k]

    def get_indexer(self) -> KnowledgeIndexer:
        """获取底层索引器"""
        self.ensure_indexed()
        return self._indexer
