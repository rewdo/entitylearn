// ============================================================
// EntityLearn API Service Layer
// ============================================================

import type {
  Pack,
  Agent,
  AgentListItem,
  Scene,
  SceneListItem,
  AskQuestionRequest,
  AskQuestionResponse,
} from '../types';

const BASE_URL = '/api';

/** 统一 fetch 封装 */
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => '');
    let message: string;
    try {
      const parsed = JSON.parse(errorBody);
      message = parsed.detail || parsed.message || res.statusText;
    } catch {
      message = errorBody || `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(message);
  }

  return res.json();
}

// ── 知识包 ──

/** 获取所有知识包 */
export function fetchPacks(): Promise<Pack[]> {
  return request<Pack[]>('/packs');
}

/** 获取单个知识包详情 */
export function fetchPack(packId: string): Promise<Pack> {
  return request<Pack>(`/packs/${packId}`);
}

// ── Agent ──

/** 获取知识包下所有 Agent（列表） */
export function fetchAgents(packId: string): Promise<AgentListItem[]> {
  return request<AgentListItem[]>(`/packs/${packId}/agents`);
}

/** 获取单个 Agent 详情 */
export function fetchAgent(packId: string, agentId: string): Promise<Agent> {
  return request<Agent>(`/packs/${packId}/agents/${agentId}`);
}

// ── 场景 ──

/** 获取知识包下所有场景（列表） */
export function fetchScenes(packId: string): Promise<SceneListItem[]> {
  return request<SceneListItem[]>(`/packs/${packId}/scenes`);
}

/** 获取单个场景详情 */
export function fetchScene(packId: string, sceneId: string): Promise<Scene> {
  return request<Scene>(`/packs/${packId}/scenes/${sceneId}`);
}

// ── 交互 ──

/** 在场景断点处向 Agent 提问 */
export function askQuestion(
  packId: string,
  sceneId: string,
  body: AskQuestionRequest,
): Promise<AskQuestionResponse> {
  return request<AskQuestionResponse>(`/packs/${packId}/scenes/${sceneId}/ask`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
