"""EntityLearn FastAPI 应用"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import __version__
from .routes import router


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。

    Returns:
        配置好的 FastAPI 应用
    """
    app = FastAPI(
        title="EntityLearn API",
        description="实体化知识讲解引擎 API",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router, prefix="/api")

    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": "EntityLearn API",
            "version": __version__,
            "docs": "/docs",
            "redoc": "/redoc",
        }

    @app.get("/health")
    async def health():
        """健康检查"""
        return {"status": "ok", "version": __version__}

    return app


# 默认应用实例
app = create_app()
