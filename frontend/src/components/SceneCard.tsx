import { Link } from 'react-router-dom';
import type { SceneListItem } from '../types';
import { DIFFICULTY_CONFIG } from '../types';

interface SceneCardProps {
  scene: SceneListItem;
  packId: string;
}

export default function SceneCard({ scene, packId }: SceneCardProps) {
  const diff = DIFFICULTY_CONFIG[scene.difficulty] || DIFFICULTY_CONFIG.beginner;

  return (
    <Link
      to={`/packs/${packId}/scenes/${scene.id}`}
      className="card p-5 group cursor-pointer block"
    >
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center text-primary-600">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 group-hover:text-primary-600 transition-colors mb-1">
            {scene.name}
          </h3>
          <p className="text-sm text-slate-500 line-clamp-2 mb-2">
            {scene.description}
          </p>

          {/* Meta */}
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className={`tag ${diff.className}`}>
              {diff.label}
            </span>
            <span>{scene.participant_count} 实体</span>
            <span>{scene.step_count} 步骤</span>
            <span>⏱ {scene.duration_minutes} 分钟</span>
          </div>
        </div>

        {/* Arrow */}
        <div className="flex-shrink-0 self-center text-slate-300 group-hover:text-primary-500 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </Link>
  );
}
