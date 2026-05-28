import { useState } from 'react';
import type { AskQuestionResponse, SourceRef } from '../types';
import SourcePanel from './SourcePanel';

interface BreakpointInputProps {
  question: string;
  hint?: string;
  targetAgentName?: string;
  placeholder?: string;
  onSubmit: (question: string) => Promise<AskQuestionResponse>;
  disabled?: boolean;
}

export default function BreakpointInput({
  question,
  hint,
  targetAgentName,
  placeholder = '输入你的回答...',
  onSubmit,
  disabled = false,
}: BreakpointInputProps) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AskQuestionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading || disabled) return;

    setLoading(true);
    setError(null);
    try {
      const res = await onSubmit(trimmed);
      setResponse(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : '请求失败');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-white rounded-xl border-2 border-primary-300 breakpoint-pulse overflow-hidden">
      {/* Question prompt */}
      <div className="bg-primary-50 px-4 py-3 border-b border-primary-100">
        <div className="flex items-start gap-2">
          <span className="text-lg flex-shrink-0">🤔</span>
          <div>
            <p className="text-sm font-medium text-primary-800">{question}</p>
            {hint && (
              <p className="text-xs text-primary-500 mt-0.5">💡 {hint}</p>
            )}
            {targetAgentName && (
              <p className="text-xs text-primary-400 mt-1">
                向 {targetAgentName} 提问
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Input area - only show if no response yet */}
      {!response && (
        <div className="p-3">
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={loading || disabled}
              rows={2}
              className="flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                         disabled:bg-slate-50 disabled:text-slate-400
                         placeholder:text-slate-400"
            />
            <button
              onClick={handleSubmit}
              disabled={loading || disabled || !input.trim()}
              className="flex-shrink-0 self-end btn-primary px-4 py-2"
            >
              {loading ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
              <span>发送</span>
            </button>
          </div>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}

      {/* Response display */}
      {response && (
        <div className="animate-slide-up">
          <div className="px-4 py-3 border-t border-slate-100">
            <p className="text-xs font-medium text-slate-500 mb-1">
              💬 回答
              {response.answered_by && (
                <span className="text-slate-400 ml-1">— {response.answered_by}</span>
              )}
            </p>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
              {response.answer}
            </p>
          </div>

          {/* Source refs */}
          {response.source_refs.length > 0 && (
            <div className="px-4 py-3 border-t border-slate-100 bg-slate-50">
              <SourcePanel sources={response.source_refs} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
