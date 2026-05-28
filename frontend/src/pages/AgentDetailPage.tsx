import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { Agent } from '../types';
import { fetchAgent } from '../services/api';
import { getAgentColor } from '../types';

export default function AgentDetailPage() {
  const { packId, agentId } = useParams<{ packId: string; agentId: string }>();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFaqs, setExpandedFaqs] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!packId || !agentId) return;
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchAgent(packId!, agentId!);
        if (!cancelled) {
          setAgent(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : '加载失败');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [packId, agentId]);

  const toggleFaq = (index: number) => {
    setExpandedFaqs((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  // ── Loading ──
  if (loading) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="skeleton h-4 w-32 mb-4" />
        <div className="card p-6 mb-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="skeleton w-14 h-14 rounded-full" />
            <div>
              <div className="skeleton h-6 w-32 mb-2" />
              <div className="skeleton h-4 w-24" />
            </div>
          </div>
          <div className="skeleton h-4 w-full mb-2" />
          <div className="skeleton h-4 w-full mb-2" />
          <div className="skeleton h-4 w-3/4" />
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="card p-4 mb-3">
            <div className="skeleton h-5 w-64 mb-2" />
            <div className="skeleton h-4 w-full" />
          </div>
        ))}
      </div>
    );
  }

  // ── Error ──
  if (error || !agent) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <span className="text-5xl mb-4">⚠️</span>
        <h2 className="text-lg font-semibold text-slate-800 mb-2">加载失败</h2>
        <p className="text-sm text-slate-500 mb-4">{error || 'Agent 不存在'}</p>
        <Link to={packId ? `/packs/${packId}` : '/'} className="btn-secondary">
          {packId ? '返回场景列表' : '返回首页'}
        </Link>
      </div>
    );
  }

  const color = getAgentColor(agent.id);
  const initial = agent.name.charAt(0);

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm mb-4">
        <Link to="/" className="breadcrumb-link">知识包</Link>
        <span className="text-slate-300">/</span>
        <Link to={`/packs/${packId}`} className="breadcrumb-link">{packId}</Link>
        <span className="text-slate-300">/</span>
        <span className="text-slate-600 font-medium">{agent.name}</span>
      </nav>

      {/* Agent header */}
      <div className="card p-6 mb-6">
        <div className="flex items-start gap-4 mb-4">
          <div
            className="flex-shrink-0 w-14 h-14 rounded-full flex items-center justify-center text-white text-xl font-bold shadow-lg"
            style={{ backgroundColor: color }}
          >
            {initial}
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 mb-1">{agent.name}</h1>
            <p className="text-sm font-medium" style={{ color }}>{agent.role}</p>
            <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
              <span>Model: {agent.model}</span>
              <span>Temperature: {agent.temperature}</span>
              <span>Max Tokens: {agent.max_tokens}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Persona */}
      <div className="card p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
          🎭 人格设定
        </h2>
        <div
          className="prose prose-sm max-w-none text-slate-600 leading-relaxed whitespace-pre-wrap"
          style={{ borderLeft: `3px solid ${color}`, paddingLeft: '12px' }}
        >
          {agent.persona}
        </div>
      </div>

      {/* Knowledge Sources */}
      <div className="card p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
          📚 知识来源 ({agent.knowledge_sources.length})
        </h2>
        {agent.knowledge_sources.length === 0 ? (
          <p className="text-sm text-slate-400">暂无知识来源</p>
        ) : (
          <div className="space-y-2">
            {agent.knowledge_sources.map((source, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg"
              >
                <svg className="w-5 h-5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-slate-700">{source.doc}</p>
                  {source.description && (
                    <p className="text-xs text-slate-500">{source.description}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* FAQ */}
      <div className="card p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
          ❓ 常见问题 ({agent.faq.length})
        </h2>
        {agent.faq.length === 0 ? (
          <p className="text-sm text-slate-400">暂无常见问题</p>
        ) : (
          <div className="space-y-3">
            {agent.faq.map((faq, idx) => (
              <div
                key={idx}
                className="border border-slate-200 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => toggleFaq(idx)}
                  className="w-full flex items-center justify-between p-3 text-left hover:bg-slate-50 transition-colors"
                >
                  <span className="text-sm font-medium text-slate-700 pr-4">
                    {faq.question}
                  </span>
                  <svg
                    className={`w-4 h-4 text-slate-400 flex-shrink-0 transition-transform ${
                      expandedFaqs.has(idx) ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {expandedFaqs.has(idx) && (
                  <div className="px-3 pb-3 animate-fade-in">
                    <div
                      className="bg-slate-50 rounded-lg p-3 text-sm text-slate-600 leading-relaxed"
                      style={{ borderLeft: `3px solid ${color}` }}
                    >
                      {faq.answer}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Back */}
      <div className="flex items-center gap-3">
        <Link to={`/packs/${packId}`} className="btn-secondary">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          返回场景列表
        </Link>
      </div>
    </div>
  );
}
