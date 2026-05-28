import { useState } from 'react';
import type { FlowStep } from '../types';
import { getAgentColor, getAgentColorClasses } from '../types';
import SourcePanel from './SourcePanel';

interface AgentBubbleProps {
  step: FlowStep;
  agentName: string;
  agentRole: string;
  /** Whether this is the latest message (for animation) */
  isLatest?: boolean;
  /** Step number */
  stepNumber: number;
}

export default function AgentBubble({
  step,
  agentName,
  agentRole,
  isLatest = false,
  stepNumber,
}: AgentBubbleProps) {
  const [showSources, setShowSources] = useState(false);
  const color = getAgentColor(step.speaker_id);
  const colorClasses = getAgentColorClasses(step.speaker_id);

  // Get initial from agent name
  const initial = agentName.charAt(0);

  const isSystem = step.type === 'system' || step.type === 'narration';

  if (isSystem) {
    return (
      <div className={`flex justify-center py-3 ${isLatest ? 'message-enter' : ''}`}>
        <div className="bg-slate-100 text-slate-600 rounded-lg px-4 py-2 max-w-lg text-sm text-center">
          <span className="text-slate-400 text-xs mr-2">#{stepNumber}</span>
          {step.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`py-3 ${isLatest ? 'message-enter' : ''}`}>
      <div className="flex gap-3">
        {/* Avatar */}
        <div
          className="flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold"
          style={{ backgroundColor: color }}
          title={agentRole}
        >
          {initial}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-slate-400">#{stepNumber}</span>
            <span className="font-medium text-sm" style={{ color }}>
              {agentName}
            </span>
            <span className="text-xs text-slate-400">{agentRole}</span>
          </div>

          {/* Message body */}
          <div
            className={`rounded-xl rounded-tl-sm px-4 py-3 ${colorClasses.bgLight} border ${colorClasses.border} border-opacity-30`}
          >
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
              {step.content}
            </p>

            {/* Source refs toggle */}
            {step.source_refs.length > 0 && (
              <button
                onClick={(e) => {
                  e.preventDefault();
                  setShowSources(!showSources);
                }}
                className="mt-2 inline-flex items-center gap-1 text-xs font-medium opacity-60 hover:opacity-100 transition-opacity"
                style={{ color }}
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {step.source_refs.length} 条引用来源
                <svg
                  className={`w-3 h-3 transition-transform ${showSources ? 'rotate-180' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            )}

            {/* Expanded sources */}
            {showSources && step.source_refs.length > 0 && (
              <div className="mt-3 animate-fade-in">
                <SourcePanel sources={step.source_refs} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
