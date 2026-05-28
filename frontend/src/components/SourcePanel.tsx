import { useState } from 'react';
import type { SourceRef } from '../types';

interface SourcePanelProps {
  sources: SourceRef[];
}

export default function SourcePanel({ sources }: SourcePanelProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
        📚 引用来源
      </p>
      {sources.map((source, idx) => (
        <SourceItem key={idx} source={source} />
      ))}
    </div>
  );
}

function SourceItem({ source }: { source: SourceRef }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-3">
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-slate-700 flex items-center gap-1">
          <svg className="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {source.doc}
        </span>
        {source.relevance !== undefined && (
          <span className="text-xs text-slate-400">
            相关度 {(source.relevance * 100).toFixed(0)}%
          </span>
        )}
      </div>

      {/* Excerpt */}
      <p className="text-xs text-slate-600 leading-relaxed italic">
        &ldquo;{source.excerpt}&rdquo;
      </p>

      {/* Expand button for full content */}
      {source.full_content && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-1.5 text-xs text-primary-600 hover:text-primary-700 font-medium inline-flex items-center gap-1"
          >
            {expanded ? '收起' : '展开完整片段'}
            <svg
              className={`w-3 h-3 transition-transform ${expanded ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {expanded && (
            <div className="mt-2 p-3 bg-slate-50 rounded-lg animate-fade-in">
              <pre className="text-xs text-slate-600 whitespace-pre-wrap font-sans leading-relaxed">
                {source.full_content}
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}
