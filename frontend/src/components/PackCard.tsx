import { Link } from 'react-router-dom';
import type { Pack } from '../types';

interface PackCardProps {
  pack: Pack;
}

export default function PackCard({ pack }: PackCardProps) {
  return (
    <Link
      to={`/packs/${pack.id}`}
      className="card p-6 group cursor-pointer block"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📦</span>
          <div>
            <h3 className="font-semibold text-slate-900 group-hover:text-primary-600 transition-colors">
              {pack.name}
            </h3>
            <p className="text-xs text-slate-400">v{pack.version}</p>
          </div>
        </div>
        <span className="tag bg-primary-50 text-primary-700">
          {pack.domain}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-slate-600 line-clamp-2 mb-4">
        {pack.description}
      </p>

      {/* Stats */}
      <div className="flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          {pack.agent_count ?? '?'} Agent{(pack.agent_count ?? 0) !== 1 ? 's' : ''}
        </span>
        <span className="flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {pack.scene_count ?? '?'} Scene{(pack.scene_count ?? 0) !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Tags */}
      {pack.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-slate-100">
          {pack.tags.map((tag) => (
            <span key={tag} className="tag bg-slate-100 text-slate-600">
              {tag}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}
