"""知识索引器

基于 frontmatter 和标题建立倒排索引（MVP，不依赖向量数据库）。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HitFragment(BaseModel):
    """匹配的知识片段"""

    text: str = Field(..., description="片段文本")
    section: str = Field(default="", description="所属章节/标题")
    start_line: int = Field(default=0, description="起始行号")


class SearchResult(BaseModel):
    """搜索结果"""

    path: str = Field(..., description="文件路径")
    title: str = Field(default="", description="文档标题")
    snippet: str = Field(default="", description="内容片段")
    relevance_score: float = Field(default=0.0, description="相关度分数 0-1")
    fragments: list[HitFragment] = Field(
        default_factory=list, description="匹配的片段列表"
    )


class KnowledgeIndexer:
    """知识索引器。

    为知识包建立关键词倒排索引，支持快速搜索。
    """

    def __init__(self):
        # word → list of (doc_path, title)
        self._index: dict[str, list[tuple[str, str]]] = {}
        # doc_path → full content
        self._documents: dict[str, str] = {}
        # doc_path → list of (heading, content) sections
        self._sections: dict[str, list[tuple[str, str]]] = {}
        # doc_path → title
        self._titles: dict[str, str] = {}

    def index_knowledge(self, pack_path: str | Path) -> int:
        """为知识包建立索引。

        Args:
            pack_path: 知识包根目录

        Returns:
            索引的文档数
        """
        pack_path = Path(pack_path)
        if not pack_path.exists():
            logger.warning(f"Pack path not found: {pack_path}")
            return 0

        count = 0
        # 扫描 knowledge/ 目录或直接扫描 markdown 文件
        for pattern in ["**/*.md", "**/*.txt", "**/*.yaml", "**/*.yml"]:
            for doc_path in pack_path.glob(pattern):
                # 跳过 pack.yaml 自身
                if doc_path.name == "pack.yaml":
                    continue
                try:
                    self._index_document(doc_path, pack_path)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to index {doc_path}: {e}")

        return count

    def _index_document(self, doc_path: Path, base_path: Path) -> None:
        """索引单个文档"""
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        rel_path = str(doc_path.relative_to(base_path))
        self._documents[rel_path] = content

        # 解析 frontmatter + 标题
        title = self._extract_title(content, doc_path)
        self._titles[rel_path] = title

        # 按标题分节
        sections = self._split_by_headings(content)
        self._sections[rel_path] = sections

        # 建立倒排索引
        words = self._tokenize(content)
        for word in words:
            if word not in self._index:
                self._index[word] = []
            entry = (rel_path, title)
            if entry not in self._index[word]:
                self._index[word].append(entry)

        logger.debug(f"Indexed: {rel_path} ({len(words)} unique tokens)")

    def search(
        self,
        query: str,
        agent_id: str | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """搜索知识内容。

        Args:
            query: 搜索查询
            agent_id: 可选，过滤特定 agent 的知识
            top_k: 返回结果数

        Returns:
            搜索结果列表（按相关度降序）
        """
        query_words = self._tokenize(query)
        if not query_words:
            return []

        # 打分
        doc_scores: dict[str, float] = {}
        for word in query_words:
            if word in self._index:
                for doc_path, title in self._index[word]:
                    if doc_path not in doc_scores:
                        doc_scores[doc_path] = 0.0
                    doc_scores[doc_path] += 1.0

        if not doc_scores:
            return []

        # 归一化
        max_score = max(doc_scores.values())
        results = []
        for doc_path, score in doc_scores.items():
            rel_score = score / max_score if max_score > 0 else 0.0

            # 提取片段
            snippet = self._extract_snippet(doc_path, query_words)

            # 提取匹配的片段
            fragments = self._find_fragments(doc_path, query_words)

            results.append(SearchResult(
                path=doc_path,
                title=self._titles.get(doc_path, ""),
                snippet=snippet,
                relevance_score=rel_score,
                fragments=fragments,
            ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]

    def _extract_title(self, content: str, doc_path: Path) -> str:
        """从文档中提取标题"""
        # frontmatter title
        fm_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        if fm_match:
            return fm_match.group(1).strip().strip("\"'")

        # 第一个 # 标题
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        return doc_path.stem

    def _tokenize(self, text: str) -> set[str]:
        """分词：优先使用 jieba 中文分词，回退到正则"""
        # 移除 markdown 标记
        text = re.sub(r"[#*_`~\[\]()]", " ", text)
        try:
            import jieba
            words = jieba.cut(text.lower())
            return {w.strip() for w in words if len(w.strip()) >= 2}
        except ImportError:
            words = re.findall(r"[\u4e00-\u9fff\w]+", text.lower())
            return {w for w in words if len(w) >= 2}

    def _split_by_headings(self, content: str) -> list[tuple[str, str]]:
        """按标题分节"""
        sections = []
        # 简单按 ## 分割
        parts = re.split(r"\n(?=#{1,3}\s)", content)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            heading_match = re.match(r"^#{1,3}\s+(.+)$", part, re.MULTILINE)
            heading = heading_match.group(1).strip() if heading_match else ""
            sections.append((heading, part))
        return sections

    def _extract_snippet(self, doc_path: str, query_words: set[str]) -> str:
        """提取相关片段作为 snippet"""
        content = self._documents.get(doc_path, "")
        if not content:
            return ""

        lines = content.split("\n")
        best_line = ""
        best_score = 0

        for line in lines:
            line_lower = line.lower()
            score = sum(1 for w in query_words if w in line_lower)
            if score > best_score:
                best_score = score
                best_line = line

        return best_line[:300] if best_line else content[:300]

    def _find_fragments(
        self, doc_path: str, query_words: set[str]
    ) -> list[HitFragment]:
        """查找匹配的片段"""
        content = self._documents.get(doc_path, "")
        if not content:
            return []

        fragments = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            line_lower = line.lower()
            matches = sum(1 for w in query_words if w in line_lower)
            if matches >= 2 and len(line.strip()) > 10:
                fragments.append(HitFragment(
                    text=line.strip()[:500],
                    section="",
                    start_line=i + 1,
                ))

        return fragments[:5]

    def get_document(self, doc_path: str) -> str | None:
        """获取文档全文"""
        return self._documents.get(doc_path)

    @property
    def index_size(self) -> int:
        """索引中的词数"""
        return len(self._index)

    @property
    def document_count(self) -> int:
        """已索引文档数"""
        return len(self._documents)
