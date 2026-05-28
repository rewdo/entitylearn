import { Link } from 'react-router-dom';
import type { Agent } from '../types';
import { getAgentColor, getAgentColorClasses } from '../types';

interface AgentInfoProps {
  agent: Agent;
  packId: string;
  /** Show compact version for sidebar */
  compact?: boolean;
}

export default function AgentInfo({ agent, packId, compact = false }: AgentInfoProps) {
  const color = getAgentColor(agent.id);
  const colorClasses = getAgentColorClasses(agent.id);
  const initial = agent.name.charAt(0);

  if (compact) {
    return (
      <Link
        to={`/packs/${packId}/agents/${agent.id}`}
        className={`flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-50 transition-colors group`}
      >
        <div
          className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
          style={{ backgroundColor: color }}
        >
          {initial}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-700 group-hover:text-primary-600 transition-colors truncate">
            {agent.name}
          </p>
          <p className="text-xs text-slate-400 truncate">{agent.role}</p>
        </div>
      </Link>
    );
  }

  return (
    <div className={`rounded-xl border ${colorClasses.border} border-opacity-40 overflow-hidden`}>
      {/* Header */}
      <div className="p-4" style={{ backgroundColor: `${color}10` }}>
        <div className="flex items-center gap-3 mb-2">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
            style={{ backgroundColor: color }}
          >
            {initial}
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">{agent.name}</h3>
            <p className="text-xs" style={{ color }}>{agent.role}</p>
          </div>
        </div>
        <Link
          to={`/packs/${packId}/agents/${agent.id}`}
          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
        >
          查看详情 →
        </Link>
      </div>

      {/* Knowledge sources count */}
      {agent.knowledge_sources.length > 0 && (
        <div className="px-4 py-2 border-t border-slate-100">
          <p className="text-xs text-slate-500">
            📚 {agent.knowledge_sources.length} 个知识来源
          </p>
        </div>
      )}

      {/* FAQ count */}
      {agent.faq.length > 0 && (
        <div className="px-4 py-2 border-t border-slate-100">
          <p className="text-xs text-slate-500">
            ❓ {agent.faq.length} 个常见问题
          </p>
        </div>
      )}
    </div>
  );
}
