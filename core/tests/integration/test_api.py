"""EntityLearn 测试 - 集成测试：API 端点"""

import pytest
from fastapi.testclient import TestClient

from entitylearn.api.app import app

client = TestClient(app)


class TestAPI:
    """测试 API 端点"""

    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "EntityLearn API"
        assert "version" in data

    def test_health(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_list_packs_empty(self):
        """测试列出知识包（空）"""
        response = client.get("/api/packs")
        # 可能返回空列表或404，取决于 packs 目录是否存在
        if response.status_code == 200:
            assert isinstance(response.json(), list)
        else:
            assert response.status_code == 404

    def test_list_packs_structure(self):
        """测试知识包列表结构"""
        response = client.get("/api/packs")
        if response.status_code == 200:
            packs = response.json()
            for pack in packs:
                assert "id" in pack
                assert "name" in pack
                assert "agent_count" in pack
                assert "scene_count" in pack

    def test_get_nonexistent_pack(self):
        """测试获取不存在的知识包"""
        response = client.get("/api/packs/nonexistent")
        assert response.status_code == 404

    def test_list_agents_nonexistent_pack(self):
        """测试列出不存在的知识包的 Agent"""
        response = client.get("/api/packs/nonexistent/agents")
        assert response.status_code == 404

    def test_get_agent_nonexistent(self):
        """测试获取不存在的 Agent"""
        response = client.get("/api/packs/nonexistent/agents/nonexistent")
        assert response.status_code == 404

    def test_list_scenes_nonexistent_pack(self):
        """测试列出不存在的知识包的 Scene"""
        response = client.get("/api/packs/nonexistent/scenes")
        assert response.status_code == 404

    def test_play_scene_nonexistent(self):
        """测试播放不存在的场景"""
        response = client.get("/api/packs/nonexistent/scenes/nonexistent/play")
        assert response.status_code == 404

    def test_ask_not_at_breakpoint(self):
        """测试在非断点时提问"""
        response = client.post(
            "/api/packs/nonexistent/scenes/nonexistent/ask",
            json={"question": "test"},
        )
        assert response.status_code == 404

    def test_docs_available(self):
        """测试文档页面可访问"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self):
        """测试 ReDoc 页面可访问"""
        response = client.get("/redoc")
        assert response.status_code == 200
