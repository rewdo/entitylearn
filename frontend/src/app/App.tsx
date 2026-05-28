import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from '../components/Layout';
import PackListPage from '../pages/PackListPage';
import SceneListPage from '../pages/SceneListPage';
import ScenePlayPage from '../pages/ScenePlayPage';
import AgentDetailPage from '../pages/AgentDetailPage';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {/* 首页 — 知识包列表 */}
          <Route path="/" element={<PackListPage />} />

          {/* 场景列表 */}
          <Route path="/packs/:packId" element={<SceneListPage />} />

          {/* Agent 详情 */}
          <Route path="/packs/:packId/agents/:agentId" element={<AgentDetailPage />} />

          {/* 场景播放（核心） */}
          <Route path="/packs/:packId/scenes/:sceneId" element={<ScenePlayPage />} />

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="flex flex-col items-center justify-center py-20">
                <span className="text-5xl mb-4">🔍</span>
                <h1 className="text-xl font-bold text-slate-800 mb-2">404</h1>
                <p className="text-sm text-slate-500 mb-4">页面不存在</p>
                <a href="/" className="btn-primary">返回首页</a>
              </div>
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
