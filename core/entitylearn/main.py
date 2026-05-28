"""EntityLearn CLI 入口"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer

from . import __version__
from .config import PACKS_DIR

# Windows GBK 编码兼容：强制 stdout 使用 utf-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

app = typer.Typer(
    name="entitylearn",
    help="EntityLearn - 实体化知识讲解引擎",
    add_completion=False,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@app.command()
def version():
    """显示版本号"""
    typer.echo(f"EntityLearn v{__version__}")


@app.command()
def list_packs():
    """列出所有可用的知识包"""
    from .loader.pack_loader import load_all_packs

    packs = load_all_packs()
    if not packs:
        typer.echo("未找到任何知识包。请在 packs/ 目录下创建知识包。")
        typer.echo(f"默认 packs 目录: {PACKS_DIR}")
        return

    typer.echo(f"\n找到 {len(packs)} 个知识包:\n")
    for pack in packs:
        typer.echo(f"  📦 {pack.id}")
        typer.echo(f"     名称: {pack.name}")
        typer.echo(f"     版本: {pack.meta.version}")
        typer.echo(f"     描述: {pack.meta.description}")
        typer.echo(f"     Agent: {len(pack.agents)} | Scene: {len(pack.scenes)} | Test: {len(pack.tests)}")
        typer.echo()


@app.command()
def validate(
    pack: str = typer.Argument(..., help="知识包 ID 或路径"),
):
    """校验知识包"""
    from .loader.pack_loader import load_pack
    from .loader.schema_validator import validate_pack as do_validate

    pack_path = Path(pack)
    if not pack_path.exists():
        # 尝试从 packs/ 目录查找
        pack_path = PACKS_DIR / pack

    if not pack_path.exists():
        typer.echo(f"❌ 知识包不存在: {pack}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"📋 正在校验: {pack_path}")

    try:
        loaded = load_pack(pack_path)
    except Exception as e:
        typer.echo(f"❌ 加载失败: {e}", err=True)
        raise typer.Exit(code=1)

    errors = do_validate(loaded, pack_path if pack_path.is_dir() else pack_path.parent)

    if errors:
        typer.echo(f"\n❌ 校验失败，发现 {len(errors)} 个问题:\n")
        for i, err in enumerate(errors, 1):
            typer.echo(f"  {i}. {err}")
        raise typer.Exit(code=1)
    else:
        typer.echo(f"\n✅ 校验通过!")
        typer.echo(f"   知识包: {loaded.name} ({loaded.id})")
        typer.echo(f"   Agent: {len(loaded.agents)} | Scene: {len(loaded.scenes)} | Test: {len(loaded.tests)}")


@app.command()
def run(
    pack: str = typer.Argument(..., help="知识包 ID 或路径"),
):
    """运行指定知识包的场景"""
    from .loader.pack_loader import load_pack
    from .runtime.scene_runner import SceneRunner

    pack_path = Path(pack)
    if not pack_path.exists():
        pack_path = PACKS_DIR / pack

    if not pack_path.exists():
        typer.echo(f"❌ 知识包不存在: {pack}", err=True)
        raise typer.Exit(code=1)

    try:
        loaded = load_pack(pack_path)
    except Exception as e:
        typer.echo(f"❌ 加载失败: {e}", err=True)
        raise typer.Exit(code=1)

    if not loaded.scenes:
        typer.echo("❌ 该知识包没有定义场景。")
        raise typer.Exit(code=1)

    # 列出场景供选择
    typer.echo(f"\n📦 {loaded.name}")
    typer.echo(f"\n可用场景:\n")
    for i, scene in enumerate(loaded.scenes, 1):
        typer.echo(f"  {i}. {scene.id} - {scene.name}")
        typer.echo(f"     {scene.description[:80]}")
        typer.echo(f"     难度: {scene.metadata.difficulty} | "
                   f"预计 {scene.metadata.estimated_duration_min} 分钟")
        typer.echo()

    # 选择场景
    if len(loaded.scenes) == 1:
        choice = "1"
    else:
        choice = typer.prompt("请选择场景 (输入编号)", default="1")

    try:
        idx = int(choice) - 1
        scene = loaded.scenes[idx]
    except (ValueError, IndexError):
        typer.echo("❌ 无效的选择", err=True)
        raise typer.Exit(code=1)

    # 建立 agents 映射
    agents = {a.id: a for a in loaded.agents}
    runner = SceneRunner(
        agents=agents,
        pack_path=pack_path if pack_path.is_dir() else pack_path.parent,
    )

    typer.echo(f"\n🎬 开始播放: {scene.name}")
    typer.echo(f"   目标: {scene.objective}")
    typer.echo(f"{'─' * 60}\n")

    # 播放场景
    gen = runner.run_scene(scene, agents)
    user_input = None

    while True:
        try:
            step = gen.send(user_input)
        except StopIteration:
            break

        # 显示步骤
        speaker_label = _speaker_label(step.speaker, agents)
        if step.is_breakpoint:
            typer.echo(f"\n💬 [{speaker_label}]: {step.content}")
            user_input = typer.prompt("   你的回答", default="")
        else:
            typer.echo(f"[{speaker_label}]: {step.content}")
            if step.source_refs:
                for ref in step.source_refs:
                    path = ref.get("path", "") if isinstance(ref, dict) else ref.path
                    typer.echo(f"    📎 来源: {path}")
            typer.echo()
            user_input = None

    typer.echo(f"{'─' * 60}")
    typer.echo("✅ 场景播放结束")


def _speaker_label(speaker: str, agents: dict) -> str:
    """获取说话人标签"""
    if speaker == "system":
        return "系统"
    agent = agents.get(speaker)
    if agent:
        return agent.name
    return speaker


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="绑定地址"),
    port: int = typer.Option(8000, "--port", "-p", help="端口号"),
    reload: bool = typer.Option(False, "--reload", help="热重载（开发模式）"),
):
    """启动 Web API 服务"""
    import uvicorn

    typer.echo(f"🚀 EntityLearn API v{__version__}")
    typer.echo(f"   地址: http://{host}:{port}")
    typer.echo(f"   文档: http://{host}:{port}/docs")
    typer.echo()

    uvicorn.run(
        "entitylearn.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@app.command()
def index(
    pack: str = typer.Argument(..., help="知识包 ID 或路径"),
):
    """为知识包建立搜索索引"""
    from .retrieval.indexer import KnowledgeIndexer

    pack_path = Path(pack)
    if not pack_path.exists():
        pack_path = PACKS_DIR / pack

    if not pack_path.exists():
        typer.echo(f"❌ 知识包不存在: {pack}", err=True)
        raise typer.Exit(code=1)

    indexer = KnowledgeIndexer()
    count = indexer.index_knowledge(pack_path)

    typer.echo(f"✅ 索引完成")
    typer.echo(f"   文档数: {count}")
    typer.echo(f"   词条数: {indexer.index_size}")


def main():
    """CLI 入口"""
    app()


if __name__ == "__main__":
    main()
