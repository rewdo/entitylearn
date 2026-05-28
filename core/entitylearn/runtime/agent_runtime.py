"""Agent 运行时"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from ..models.agent import Agent, FAQ, KnowledgeSource

logger = logging.getLogger(__name__)


class Answer(BaseModel):
    """Agent 回答"""

    content: str = Field(..., description="回答内容")
    sources: list[str] = Field(default_factory=list, description="引用的来源路径")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="置信度 0-1",
    )


class AgentRuntime:
    """Agent 运行时。

    负责让 Agent 回答问题：优先 FAQ 匹配，其次搜索知识文档，
    保持第一人称、保守策略。
    """

    def __init__(self, pack_path: str | Path | None = None):
        """初始化 Agent 运行时。

        Args:
            pack_path: 知识包根目录（用于读取知识文档）
        """
        self.pack_path = Path(pack_path) if pack_path else None

    def answer(
        self,
        agent: Agent,
        question: str,
        context: dict | None = None,
    ) -> Answer:
        """让 Agent 回答问题。

        策略：
        1. 先检查 FAQ
        2. 再搜索知识文档
        3. 都不命中 → 返回不确定

        Args:
            agent: 回答问题的 Agent
            question: 用户问题
            context: 当前上下文（可选）

        Returns:
            Answer 对象
        """
        question_lower = question.strip().lower()

        # 1. 检查禁止话题
        forbidden_hit = self._check_forbidden(agent, question)
        if forbidden_hit:
            person_prefix = "我" if agent.first_person else agent.name
            return Answer(
                content=f"抱歉，{person_prefix}不方便讨论这个话题。",
                sources=[],
                confidence=0.0,
            )

        # 2. 匹配 FAQ
        faq_answer = self._match_faq(agent, question_lower)
        if faq_answer:
            return faq_answer

        # 3. 搜索知识文档
        knowledge_answer = self._search_knowledge(agent, question_lower)
        if knowledge_answer.confidence > 0.3:
            return knowledge_answer

        # 4. 不确定
        person_prefix = "我" if agent.first_person else agent.name
        return Answer(
            content=f"抱歉，{person_prefix}目前没有足够的信息来回答这个问题。",
            sources=[],
            confidence=0.0,
        )

    def _check_forbidden(self, agent: Agent, question: str) -> bool:
        """检查问题是否涉及禁止话题"""
        q_lower = question.lower()
        for topic in agent.forbidden_topics:
            if topic.lower() in q_lower:
                return True

        for topic in agent.scope.disallowed_topics:
            if topic.lower() in q_lower:
                return True

        return False

    def _match_faq(self, agent: Agent, question_lower: str) -> Answer | None:
        """尝试匹配 FAQ。

        使用简单关键词匹配：问题中的重要词都在 FAQ 问题中出现则匹配。
        """
        # 提取问题中的关键词（长度≥2的词）
        q_words = set(
            w for w in re.findall(r"[\u4e00-\u9fff\w]+", question_lower)
            if len(w) >= 2
        )

        if not q_words:
            return None

        best_match: FAQ | None = None
        best_score = 0.0

        for faq in agent.faq:
            faq_words = set(
                w for w in re.findall(r"[\u4e00-\u9fff\w]+", faq.question.lower())
                if len(w) >= 2
            )
            if not faq_words:
                continue

            # Jaccard 相似度
            intersection = q_words & faq_words
            union = q_words | faq_words
            score = len(intersection) / len(union) if union else 0.0

            if score > best_score:
                best_score = score
                best_match = faq

        if best_match and best_score >= 0.3:
            person_prefix = "我" if agent.first_person else agent.name
            answer_text = best_match.answer.replace("{{name}}", agent.name)
            answer_text = answer_text.replace("{{person}}", person_prefix)
            return Answer(
                content=answer_text,
                sources=best_match.sources,
                confidence=min(best_score + 0.2, 1.0),
            )

        return None

    def _search_knowledge(self, agent: Agent, question_lower: str) -> Answer:
        """搜索知识文档。

        MVP 实现：读取知识文档，按关键词匹配段落。
        """
        if not self.pack_path or not agent.knowledge_sources:
            return Answer(content="", sources=[], confidence=0.0)

        q_words = set(
            w for w in re.findall(r"[\u4e00-\u9fff\w]+", question_lower)
            if len(w) >= 2
        )

        if not q_words:
            return Answer(content="", sources=[], confidence=0.0)

        all_paragraphs: list[dict] = []

        for ks in agent.knowledge_sources:
            source_path = self.pack_path / ks.path
            if not source_path.exists():
                logger.warning(f"Knowledge source not found: {source_path}")
                continue

            try:
                with open(source_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # 按段落分割
                paragraphs = content.split("\n\n")
                for para in paragraphs:
                    para = para.strip()
                    if para and len(para) > 10:
                        all_paragraphs.append({
                            "text": para,
                            "source": ks.path,
                            "title": ks.title or ks.path,
                        })
            except Exception as e:
                logger.error(f"Failed to read {source_path}: {e}")

        if not all_paragraphs:
            return Answer(content="", sources=[], confidence=0.0)

        # 评分
        scored = []
        for para_info in all_paragraphs:
            para_lower = para_info["text"].lower()
            score = sum(1 for w in q_words if w in para_lower)
            scored.append((score, para_info))

        scored.sort(key=lambda x: x[0], reverse=True)

        # 取 top 3
        top_paras = scored[:3]
        if not top_paras or top_paras[0][0] == 0:
            return Answer(content="", sources=[], confidence=0.0)

        # 构建回答
        relevant_texts = [p[1]["text"] for p in top_paras if p[0] > 0]
        sources = list(set(p[1]["source"] for p in top_paras if p[0] > 0))

        if not relevant_texts:
            return Answer(content="", sources=[], confidence=0.0)

        person_prefix = "我" if agent.first_person else agent.name
        # 简单拼接（MVP，不做 LLM 总结）
        combined = f"根据{person_prefix}的了解：\n\n" + "\n\n".join(
            relevant_texts[:2]
        )

        max_score_possible = len(q_words)
        confidence = min(top_paras[0][0] / max(max_score_possible, 1), 0.8)

        return Answer(
            content=combined,
            sources=sources,
            confidence=confidence,
        )
