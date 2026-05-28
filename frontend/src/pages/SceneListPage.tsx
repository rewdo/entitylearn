import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { Pack, SceneListItem } from '../types';
import { fetchPack, fetchScenes } from '../services/api';
import SceneCard from '../components/SceneCard';

export default function SceneListPage() {
  const { packId } = useParams<{ packId: string }>();
  const [pack, setPack] = useState<Pack | null>(null);
  const [scenes, setScenes] = useState<SceneListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!packId) return;
    let cancelled = false;

    async function load() {
      try {
        const [packData, scenesData] = await Promise.all([
          fetchPack(packId!),
          fetchScenes(packId!),
        ]);
        if (!cancelled) {
          setPack(packData);
          setScenes(scenesData);
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
  }, [packId]);

  // ── Loading ──
  if (loading) {
    return (
      <div>
        <div className="skeleton h-4 w-48 mb-2" />
        <div className="skeleton h-7 w-64 mb-2" />
        <div className="skeleton h-4 w-96 mb-8" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="card p-5 mb-4">
            <div className="flex gap-4">
              <div className="skeleton w-10 h-10 rounded-lg" />
              <div className="flex-1">
                <div className="skeleton h-5 w-48 mb-2" />
                <div className="skeleton h-4 w-full mb-2" />
                <div className="skeleton h-3 w-64" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // ── Error ──
  if (error || !pack) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <span className="text-5xl mb-4">⚠️</span>
        <h2 className="text-lg font-semibold text-slate-800 mb-2">加载失败</h2>
        <p className="text-sm text-slate-500 mb-4">{error || '知识包不存在'}</p>
        <Link to="/" className="btn-secondary">返回首页</Link>
      </div>
    );
  }

  // ── Content ──
  return (
    <div className="animate-fade-in">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm mb-4">
        <Link to="/" className="breadcrumb-link">知识包</Link>
        <span className="text-slate-300">/</span>
        <span className="text-slate-600 font-medium">{pack.name}</span>
      </nav>

      {/* Pack header */}
      <div className="card p-6 mb-6">
        <div className="flex items-start gap-4">
          <span className="text-3xl">📦</span>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-xl font-bold text-slate-900">{pack.name}</h1>
              <span className="tag bg-primary-50 text-primary-700">{pack.domain}</span>
            </div>
            <p className="text-sm text-slate-500 mb-2">{pack.description}</p>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span>v{pack.version}</span>
              <span>·</span>
              <span>{pack.language === 'zh-CN' ? '中文' : pack.language}</span>
              <span>·</span>
              <span>License: {pack.license}</span>
            </div>

            {/* Tags */}
            {pack.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {pack.tags.map((tag) => (
                  <span key={tag} className="tag bg-slate-100 text-slate-600">{tag}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scenes section */}
      <h2 className="text-lg font-semibold text-slate-900 mb-4">
        学习场景 ({scenes.length})
      </h2>

      {scenes.length === 0 ? (
        <div className="card p-8 text-center">
          <span className="text-4xl block mb-3">🎬</span>
          <p className="text-slate-500 text-sm">该知识包暂无场景</p>
        </div>
      ) : (
        <div className="space-y-3">
          {scenes.map((scene) => (
            <SceneCard key={scene.id} scene={scene} packId={packId!} />
          ))}
        </div>
      )}
    </div>
  );
}
