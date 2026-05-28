import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { Scene, Agent, Breakpoint } from '../types';
import { fetchScene, fetchAgents, fetchAgent, askQuestion } from '../services/api';
import AgentBubble from '../components/AgentBubble';
import StepTimeline from '../components/StepTimeline';
import AgentInfo from '../components/AgentInfo';
import BreakpointInput from '../components/BreakpointInput';
import SourcePanel from '../components/SourcePanel';
import { DIFFICULTY_CONFIG } from '../types';

export default function ScenePlayPage() {
  const { packId, sceneId } = useParams<{ packId: string; sceneId: string }>();
  const [scene, setScene] = useState<Scene | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Playback state
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [autoPlay, setAutoPlay] = useState(false);
  const [revealedSteps, setRevealedSteps] = useState<number>(0);

  // Active breakpoint
  const [activeBreakpoint, setActiveBreakpoint] = useState<Breakpoint | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const autoPlayRef = useRef(autoPlay);

  // Load data
  useEffect(() => {
    if (!packId || !sceneId) return;
    let cancelled = false;

    async function load() {
      try {
        const [sceneData, agentList] = await Promise.all([
          fetchScene(packId!, sceneId!),
          fetchAgents(packId!),
        ]);

        if (cancelled) return;

        // Load full agent details
        const fullAgents = await Promise.all(
          sceneData.participants.map((p) => fetchAgent(packId!, p.agent_id))
        );

        if (!cancelled) {
          setScene(sceneData);
          setAgents(fullAgents);
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
  }, [packId, sceneId]);

  // Auto-scroll to latest message
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    if (revealedSteps > 0) {
      scrollToBottom();
    }
  }, [revealedSteps, scrollToBottom]);

  // Auto-play logic
  useEffect(() => {
    autoPlayRef.current = autoPlay;
  }, [autoPlay]);

  useEffect(() => {
    if (!autoPlay) return;
    const interval = setInterval(() => {
      if (!autoPlayRef.current) {
        clearInterval(interval);
        return;
      }
      setCurrentStepIndex((prev) => {
        const steps = scene?.flow_steps || [];
        const next = prev + 1;
        if (next >= steps.length) {
          setAutoPlay(false);
          return prev;
        }
        return next;
      });
      setRevealedSteps((prev) => Math.min(prev + 1, scene?.flow_steps?.length || 0));

      // Check breakpoints after advancing
      setActiveBreakpoint((prev) => {
        // If we have an active breakpoint already (not handled), keep it
        if (prev) return prev;
        return null;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [autoPlay, scene]);

  // Check for breakpoint at current step
  useEffect(() => {
    if (!scene) return;
    const currentStep = scene.flow_steps[currentStepIndex];
    if (!currentStep) {
      setActiveBreakpoint(null);
      return;
    }
    const bp = scene.breakpoints.find((b) => b.step_id === currentStep.id);
    if (bp) {
      setAutoPlay(false);
      setActiveBreakpoint(bp);
    } else {
      setActiveBreakpoint(null);
    }
  }, [currentStepIndex, scene]);

  // Advance to next step
  const handleNext = useCallback(() => {
    if (!scene) return;
    const next = currentStepIndex + 1;
    if (next >= scene.flow_steps.length) return;

    // Check if current step has unresolved breakpoint
    const currentStep = scene.flow_steps[currentStepIndex];
    const bp = scene.breakpoints.find((b) => b.step_id === currentStep?.id);
    if (bp && activeBreakpoint) {
      // Don't advance - breakpoint needs to be resolved
      return;
    }

    setCurrentStepIndex(next);
    setRevealedSteps((prev) => Math.min(prev + 1, scene.flow_steps.length));
    setActiveBreakpoint(null);
  }, [currentStepIndex, scene, activeBreakpoint]);

  // Handle breakpoint question submission
  const handleBreakpointSubmit = async (question: string): Promise<any> => {
    if (!packId || !sceneId || !activeBreakpoint) {
      throw new Error('Missing context');
    }
    return askQuestion(packId, sceneId, {
      question,
      agent_id: activeBreakpoint.target_agent_id,
    });
  };

  // Agent name/id lookup
  const agentMap = new Map(agents.map((a) => [a.id, a]));
  const agentNames: Record<string, string> = {};
  agents.forEach((a) => { agentNames[a.id] = a.name; });

  // ── Loading ──
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <svg className="w-8 h-8 animate-spin mx-auto mb-3 text-primary-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm text-slate-500">加载场景中...</p>
        </div>
      </div>
    );
  }

  // ── Error ──
  if (error || !scene) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <span className="text-5xl mb-4">⚠️</span>
        <h2 className="text-lg font-semibold text-slate-800 mb-2">加载失败</h2>
        <p className="text-sm text-slate-500 mb-4">{error || '场景不存在'}</p>
        <Link to={packId ? `/packs/${packId}` : '/'} className="btn-secondary">
          {packId ? '返回场景列表' : '返回首页'}
        </Link>
      </div>
    );
  }

  const allDoneSteps = revealedSteps >= scene.flow_steps.length && !activeBreakpoint;
  const currentStep = scene.flow_steps[currentStepIndex];
  const diff = DIFFICULTY_CONFIG[scene.difficulty] || DIFFICULTY_CONFIG.beginner;

  return (
    <div className="animate-fade-in -mx-4 sm:-mx-6 lg:-mx-8 -my-6 flex flex-col" style={{ height: 'calc(100vh - 64px)' }}>
      {/* ── Top bar ── */}
      <div className="flex-shrink-0 bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            to={`/packs/${packId}`}
            className="btn-ghost p-1.5 flex-shrink-0"
            title="返回场景列表"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div className="min-w-0">
            <h1 className="text-sm font-semibold text-slate-900 truncate">{scene.name}</h1>
            <p className="text-xs text-slate-400 truncate">{scene.goal}</p>
          </div>
          <span className={`tag flex-shrink-0 ${diff.className}`}>{diff.label}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-slate-400">
            {revealedSteps} / {scene.flow_steps.length}
          </span>
          <div className="w-24 h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all duration-500"
              style={{ width: `${scene.flow_steps.length > 0 ? (revealedSteps / scene.flow_steps.length) * 100 : 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* ── Main content: two columns ── */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Playback area (60%) */}
        <div className="flex-1 lg:flex-[3] flex flex-col min-w-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4">
            {scene.flow_steps.slice(0, revealedSteps).map((step, idx) => {
              const agent = agentMap.get(step.speaker_id);
              return (
                <AgentBubble
                  key={step.id}
                  step={step}
                  agentName={agent?.name || step.speaker_id}
                  agentRole={agent?.role || ''}
                  isLatest={idx === revealedSteps - 1}
                  stepNumber={idx + 1}
                />
              );
            })}

            {/* Active breakpoint */}
            {activeBreakpoint && revealedSteps > 0 && (
              <div className="py-3">
                <BreakpointInput
                  question={activeBreakpoint.question}
                  hint={activeBreakpoint.hint}
                  targetAgentName={
                    activeBreakpoint.target_agent_id
                      ? agentMap.get(activeBreakpoint.target_agent_id)?.name
                      : undefined
                  }
                  onSubmit={handleBreakpointSubmit}
                />
              </div>
            )}

            {/* All done */}
            {allDoneSteps && scene.flow_steps.length > 0 && (
              <div className="flex justify-center py-6">
                <div className="text-center bg-green-50 rounded-xl px-6 py-4 border border-green-200">
                  <p className="text-green-700 font-medium">🎉 场景播放完毕</p>
                  <p className="text-green-600 text-xs mt-1">{scene.goal}</p>
                </div>
              </div>
            )}

            {/* All done + all breakpoints resolved */}
            {allDoneSteps && !activeBreakpoint && (
              <div className="flex justify-center py-4">
                <Link
                  to={`/packs/${packId}`}
                  className="btn-secondary text-sm"
                >
                  返回场景列表
                </Link>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Controls */}
          <div className="flex-shrink-0 bg-white border-t border-slate-200 px-4 py-3">
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setAutoPlay(!autoPlay)}
                className={`btn-secondary text-xs ${autoPlay ? 'bg-primary-50 text-primary-700 border-primary-300' : ''}`}
              >
                {autoPlay ? (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    暂停
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    自动播放
                  </>
                )}
              </button>

              <button
                onClick={handleNext}
                disabled={allDoneSteps || (!!activeBreakpoint)}
                className="btn-primary text-sm"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
                下一步
              </button>

              {activeBreakpoint && (
                <span className="text-xs text-amber-600">请先回答断点问题</span>
              )}
            </div>
          </div>
        </div>

        {/* Right: Info panel (40%) */}
        <div className="hidden lg:flex lg:flex-col lg:w-80 xl:w-96 border-l border-slate-200 bg-white overflow-y-auto">
          {/* Scene info */}
          <div className="p-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900 mb-1">📋 场景信息</h2>
            <p className="text-xs text-slate-500 mb-2">{scene.name}</p>
            <p className="text-xs text-slate-600 leading-relaxed mb-2">{scene.description}</p>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>{scene.flow_steps.length} 个步骤</span>
              <span>·</span>
              <span>⏱ {scene.duration_minutes} 分钟</span>
            </div>
          </div>

          {/* Timeline */}
          <div className="p-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900 mb-3">🕐 步骤时间线</h2>
            <StepTimeline
              steps={scene.flow_steps}
              currentStepIndex={currentStepIndex}
              onStepClick={(idx) => {
                if (idx < revealedSteps) {
                  setCurrentStepIndex(idx);
                }
              }}
              agentNames={agentNames}
            />
          </div>

          {/* Participants */}
          <div className="p-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-900 mb-3">
              👥 参与实体 ({agents.length})
            </h2>
            <div className="space-y-1">
              {agents.map((agent) => (
                <AgentInfo key={agent.id} agent={agent} packId={packId!} compact />
              ))}
            </div>
          </div>

          {/* Current step sources */}
          {currentStep && currentStep.source_refs.length > 0 && (
            <div className="p-4">
              <h2 className="text-sm font-semibold text-slate-900 mb-3">
                📚 当前步骤引用
              </h2>
              <SourcePanel sources={currentStep.source_refs} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
