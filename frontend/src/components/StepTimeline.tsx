import type { FlowStep } from '../types';

interface StepTimelineProps {
  steps: FlowStep[];
  currentStepIndex: number;
  onStepClick?: (index: number) => void;
  agentNames: Record<string, string>;
}

export default function StepTimeline({
  steps,
  currentStepIndex,
  onStepClick,
  agentNames,
}: StepTimelineProps) {
  return (
    <div className="space-y-1">
      {steps.map((step, idx) => {
        const isActive = idx === currentStepIndex;
        const isPast = idx < currentStepIndex;
        const isFuture = idx > currentStepIndex;
        const speakerName = agentNames[step.speaker_id] || step.speaker_id;

        return (
          <button
            key={step.id}
            onClick={() => onStepClick?.(idx)}
            disabled={isFuture}
            className={`w-full text-left flex items-center gap-3 px-3 py-2 rounded-lg text-xs transition-all ${
              isActive
                ? 'bg-primary-50 text-primary-700 font-medium'
                : isPast
                ? 'text-slate-400 hover:bg-slate-50 cursor-pointer'
                : 'text-slate-300 cursor-not-allowed'
            }`}
          >
            {/* Dot indicator */}
            <span
              className={`flex-shrink-0 w-2 h-2 rounded-full ${
                isActive ? 'bg-primary-500' : isPast ? 'bg-slate-300' : 'bg-slate-200'
              }`}
            />

            {/* Step info */}
            <span className="truncate">
              <span className="text-slate-400 mr-1">#{idx + 1}</span>
              {step.type === 'system' ? '📢 系统' : `💬 ${speakerName}`}
            </span>

            {/* Active indicator */}
            {isActive && (
              <span className="ml-auto flex-shrink-0 w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse-dot" />
            )}
          </button>
        );
      })}

      {steps.length === 0 && (
        <p className="text-xs text-slate-400 text-center py-4">暂无步骤</p>
      )}
    </div>
  );
}
