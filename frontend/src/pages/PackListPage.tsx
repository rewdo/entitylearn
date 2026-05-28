import { useEffect, useState } from 'react';
import type { Pack } from '../types';
import { fetchPacks } from '../services/api';
import PackCard from '../components/PackCard';

export default function PackListPage() {
  const [packs, setPacks] = useState<Pack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await fetchPacks();
        if (!cancelled) {
          setPacks(data);
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
  }, []);

  // ── Loading ──
  if (loading) {
    return (
      <div>
        <div className="mb-6">
          <div className="skeleton h-7 w-48 mb-2" />
          <div className="skeleton h-4 w-72" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6">
              <div className="skeleton h-6 w-32 mb-3" />
              <div className="skeleton h-4 w-full mb-2" />
              <div className="skeleton h-4 w-3/4 mb-4" />
              <div className="skeleton h-3 w-48" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── Error ──
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <span className="text-5xl mb-4">⚠️</span>
        <h2 className="text-lg font-semibold text-slate-800 mb-2">加载失败</h2>
        <p className="text-sm text-slate-500 mb-4">{error}</p>
        <button onClick={() => window.location.reload()} className="btn-primary">
          重新加载
        </button>
      </div>
    );
  }

  // ── Empty ──
  if (packs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <span className="text-5xl mb-4">📦</span>
        <h2 className="text-lg font-semibold text-slate-800 mb-2">暂无知识包</h2>
        <p className="text-sm text-slate-500 mb-4">还没有任何知识包，请先创建一个</p>
        <a
          href="https://github.com/entitylearn/entitylearn"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary"
        >
          查看文档
        </a>
      </div>
    );
  }

  // ── Content ──
  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          知识包
        </h1>
        <p className="text-slate-500">
          浏览所有可用的知识包，选择你感兴趣的领域开始探索
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {packs.map((pack) => (
          <PackCard key={pack.id} pack={pack} />
        ))}
      </div>
    </div>
  );
}
