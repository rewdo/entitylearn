"""EntityLearn API 路由"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..loader.pack_loader import PackLoader, load_pack, load_all_packs
from ..runtime.scene_runner import SceneRunner, SceneStep

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局状态
_pack_loader = PackLoader()
_packs_cache: dict[str, "Pack"] = {}  # noqa: F821
_scene_runners: dict[str, SceneRunner] = {}


class AskRequest(BaseModel):
    """提问请求"""

    question: str = Field(..., description="用户问题", min_length=1)
    agent_id: str | None = Field(default=None, description="指定回答的 Agent ID")


class AskResponse(BaseModel):
    """提问响应"""

    step_id: str = Field(..., description="步骤 ID")
    speaker: str = Field(..., description="回答者")
    content: str = Field(..., description="回答内容")
    type: str = Field(default="dialogue", description="类型")
    sources: list[str] = Field(default_factory=list, description="引用来源")


def _ensure_packs_loaded():
    """确保已加载知识包"""
    if not _packs_cache:
        all_packs = _pack_loader.load_all()
        for pack in all_packs:
            _packs_cache[pack.id] = pack


@router.get("/packs")
async def list_packs():
    """列出所有知识包"""
    _ensure_packs_loaded()
    return [
        {
            "id": pack.id,
            "name": pack.name,
            "version": pack.meta.version,
            "description": pack.meta.description,
            "domain": pack.meta.domain,
            "agent_count": len(pack.agents),
            "scene_count": len(pack.scenes),
            "test_count": len(pack.tests),
        }
        for pack in _packs_cache.values()
    ]


@router.get("/packs/{pack_id}")
async def get_pack(pack_id: str):
    """获取知识包详情"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    return {
        "id": pack.id,
        "name": pack.name,
        "meta": pack.meta.model_dump(),
        "agent_count": len(pack.agents),
        "scene_count": len(pack.scenes),
        "test_count": len(pack.tests),
    }


@router.get("/packs/{pack_id}/agents")
async def list_agents(pack_id: str):
    """列出知识包的所有 Agent"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    return [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "role": agent.role,
            "voice": agent.voice,
            "first_person": agent.first_person,
            "knowledge_source_count": len(agent.knowledge_sources),
            "faq_count": len(agent.faq),
        }
        for agent in pack.agents
    ]


@router.get("/packs/{pack_id}/agents/{agent_id}")
async def get_agent(pack_id: str, agent_id: str):
    """获取 Agent 详情"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    agent = pack.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found in pack '{pack_id}'",
        )

    return agent.model_dump()


@router.get("/packs/{pack_id}/scenes")
async def list_scenes(pack_id: str):
    """列出知识包的所有场景"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    return [
        {
            "id": scene.id,
            "name": scene.name,
            "description": scene.description,
            "objective": scene.objective,
            "participant_count": len(scene.participants),
            "step_count": len(scene.flow),
            "difficulty": scene.metadata.difficulty,
            "estimated_duration_min": scene.metadata.estimated_duration_min,
        }
        for scene in pack.scenes
    ]


@router.get("/packs/{pack_id}/scenes/{scene_id}")
async def get_scene(pack_id: str, scene_id: str):
    """获取场景详情"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    scene = pack.get_scene(scene_id)
    if not scene:
        raise HTTPException(
            status_code=404,
            detail=f"Scene '{scene_id}' not found in pack '{pack_id}'",
        )

    return scene.model_dump()


@router.get("/packs/{pack_id}/scenes/{scene_id}/play")
async def play_scene(pack_id: str, scene_id: str):
    """播放场景（返回所有步骤）"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    scene = pack.get_scene(scene_id)
    if not scene:
        raise HTTPException(
            status_code=404,
            detail=f"Scene '{scene_id}' not found in pack '{pack_id}'",
        )

    # 建立 agents 映射
    agents = {a.id: a for a in pack.agents}

    runner = SceneRunner(agents=agents, pack_path=_pack_loader.packs_dir / pack_id)

    steps = []
    for step in runner.run_scene(scene, agents):
        steps.append(step.model_dump())

    return {
        "scene_id": scene_id,
        "scene_name": scene.name,
        "step_count": len(steps),
        "steps": steps,
    }


@router.post("/packs/{pack_id}/scenes/{scene_id}/ask")
async def ask_question(pack_id: str, scene_id: str, request: AskRequest):
    """在场景断点处提问"""
    _ensure_packs_loaded()
    pack = _packs_cache.get(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_id}' not found")

    scene = pack.get_scene(scene_id)
    if not scene:
        raise HTTPException(
            status_code=404,
            detail=f"Scene '{scene_id}' not found in pack '{pack_id}'",
        )

    agents = {a.id: a for a in pack.agents}
    runner_key = f"{pack_id}:{scene_id}"

    if runner_key not in _scene_runners:
        _scene_runners[runner_key] = SceneRunner(
            agents=agents,
            pack_path=_pack_loader.packs_dir / pack_id,
        )

    runner = _scene_runners[runner_key]

    # 如果 runner 没有加载场景，先加载
    if runner.current_scene is None or runner.current_scene.id != scene_id:
        # 先播放到第一个断点
        gen = runner.run_scene(scene, agents)
        try:
            next(gen)
        except StopIteration:
            pass

    if not runner.is_paused:
        raise HTTPException(
            status_code=400,
            detail="Not at a breakpoint. Play the scene first to reach a breakpoint.",
        )

    result = runner.ask(request.question)
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to process question",
        )

    return AskResponse(
        step_id=result.step_id,
        speaker=result.speaker,
        content=result.content,
        type=result.type,
        sources=[
            ref.get("path", "") for ref in result.source_refs
        ],
    )
