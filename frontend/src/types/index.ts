// ============================================================
// EntityLearn TypeScript Type Definitions
// ============================================================

/** 知识包 */
export interface Pack {
  id: string;
  name: string;
  version: string;
  description: string;
  domain: string;
  language: string;
  schema_version: string;
  license: string;
  authors: Author[];
  tags: string[];
  /** 运行时计算的统计 */
  agent_count?: number;
  scene_count?: number;
}

export interface Author {
  name: string;
  email?: string;
}

/** FAQ 条目 */
export interface FAQ {
  question: string;
  answer: string;
}

/** 知识来源引用 */
export interface KnowledgeSource {
  doc: string;
  description?: string;
}

/** Entity Agent — 领域实体角色 */
export interface Agent {
  id: string;
  name: string;
  role: string;
  persona: string;
  model: string;
  temperature: number;
  max_tokens: number;
  knowledge_sources: KnowledgeSource[];
  faq: FAQ[];
  /** 角色颜色标识 */
  color?: string;
}

/** 场景参与者 */
export interface Participant {
  agent_id: string;
  /** 在场景中的显示名 */
  display_name?: string;
}

/** 引用来源 */
export interface SourceRef {
  /** 知识文档名称 */
  doc: string;
  /** 引用片段 */
  excerpt: string;
  /** 相关度 */
  relevance?: number;
  /** 文档完整片段（展开后显示） */
  full_content?: string;
}

/** 场景流步骤 */
export interface FlowStep {
  id: string;
  /** 发言者 agent id */
  speaker_id: string;
  /** 第一人称发言内容 */
  content: string;
  /** 引用来源 */
  source_refs: SourceRef[];
  /** 步骤类型 */
  type: 'message' | 'system' | 'narration';
  /** 步骤顺序 */
  order: number;
}

/** 断点 — 需要用户参与的交互点 */
export interface Breakpoint {
  id: string;
  /** 触发断点的步骤 id */
  step_id: string;
  /** 断点问题 */
  question: string;
  /** 期望回答的目标 agent */
  target_agent_id?: string;
  /** 提示文本 */
  hint?: string;
}

/** 场景 */
export interface Scene {
  id: string;
  name: string;
  description: string;
  goal: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes: number;
  /** 参与实体 */
  participants: Participant[];
  /** 流程步骤 */
  flow_steps: FlowStep[];
  /** 断点列表 */
  breakpoints: Breakpoint[];
  /** 标签 */
  tags?: string[];
}

/** 场景列表项（精简版） */
export interface SceneListItem {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes: number;
  participant_count: number;
  step_count: number;
  tags?: string[];
}

/** Agent 列表项（精简版） */
export interface AgentListItem {
  id: string;
  name: string;
  role: string;
  model: string;
  color?: string;
}

/** 断点提问请求 */
export interface AskQuestionRequest {
  question: string;
  agent_id?: string;
}

/** 断点提问响应 */
export interface AskQuestionResponse {
  answer: string;
  source_refs: SourceRef[];
  /** 回答者的 agent id */
  answered_by: string;
}

/** API 通用响应包装 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/** Agent 颜色映射 */
export const AGENT_COLORS: Record<string, string> = {
  router: '#F59E0B',
  switch: '#10B981',
  dns_server: '#8B5CF6',
  dns: '#8B5CF6',
  client: '#3B82F6',
  web_server: '#EF4444',
  web: '#EF4444',
};

export const AGENT_COLOR_CLASSES: Record<string, { bg: string; border: string; text: string; bgLight: string }> = {
  router: { bg: 'bg-amber-500', border: 'border-amber-500', text: 'text-amber-700', bgLight: 'bg-amber-50' },
  switch: { bg: 'bg-emerald-500', border: 'border-emerald-500', text: 'text-emerald-700', bgLight: 'bg-emerald-50' },
  dns_server: { bg: 'bg-violet-500', border: 'border-violet-500', text: 'text-violet-700', bgLight: 'bg-violet-50' },
  dns: { bg: 'bg-violet-500', border: 'border-violet-500', text: 'text-violet-700', bgLight: 'bg-violet-50' },
  client: { bg: 'bg-blue-500', border: 'border-blue-500', text: 'text-blue-700', bgLight: 'bg-blue-50' },
  web_server: { bg: 'bg-red-500', border: 'border-red-500', text: 'text-red-700', bgLight: 'bg-red-50' },
  web: { bg: 'bg-red-500', border: 'border-red-500', text: 'text-red-700', bgLight: 'bg-red-50' },
};

/** 获取 Agent 颜色（支持多种 id 格式） */
export function getAgentColor(agentId: string): string {
  return AGENT_COLORS[agentId] || AGENT_COLORS[agentId.replace('_server', '')] || '#6B7280';
}

export function getAgentColorClasses(agentId: string) {
  return AGENT_COLOR_CLASSES[agentId] ||
    AGENT_COLOR_CLASSES[agentId.replace('_server', '')] || {
      bg: 'bg-gray-500',
      border: 'border-gray-500',
      text: 'text-gray-700',
      bgLight: 'bg-gray-50',
    };
}

/** 难度标签配置 */
export const DIFFICULTY_CONFIG: Record<string, { label: string; className: string }> = {
  beginner: { label: '入门', className: 'bg-green-100 text-green-700' },
  intermediate: { label: '进阶', className: 'bg-amber-100 text-amber-700' },
  advanced: { label: '高级', className: 'bg-red-100 text-red-700' },
};
