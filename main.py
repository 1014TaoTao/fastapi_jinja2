# -*- coding: utf-8 -*-

from typing import Any, AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.core.database import create_db_and_tables
from app.core.exceptions import register_exception_handler
from app.core.middlewares import register_middleware_handler
from app.core.logger import logger

import typer
from alembic import command
from alembic.config import Config
from app.core.database import engine

app = typer.Typer()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    自定义生命周期
    """
    logger.info(f'服务启动...')
    await create_db_and_tables()
    yield
    logger.info(f'服务关闭...')

# 初始化 Alembic 配置
alembic_cfg = Config("alembic.ini")

@app.command()
def init():
    """
    初始化 Alembic 迁移环境。
    """
    command.init(alembic_cfg, "app/alembic", template="generic")
    typer.echo("Alembic 迁移环境已初始化。")

@app.command()
def revision(message: str):
    """
    生成新的 Alembic 迁移脚本。
    """
    command.revision(alembic_cfg, message=message, autogenerate=True)
    typer.echo(f"迁移脚本已生成: {message}")

@app.command()
def upgrade():
    """
    应用最新的 Alembic 迁移。
    """
    command.upgrade(alembic_cfg, "head")
    typer.echo("所有迁移已应用。")

def create_app() -> FastAPI:

    # 创建FastAPI应用
    app = FastAPI(lifespan=lifespan, debug=True)

    # 挂载静态文件
    app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

    # # 注册中间件
    register_middleware_handler(app)

    # # 注册异常
    register_exception_handler(app)

    # 注册路由
    from app.view.demo import router as demo_router
    Router = APIRouter(prefix="")
    Router.include_router(router=demo_router, tags=["案例接口"])
    app.include_router(Router)

    return app

@app.command()
def run():
    """
    启动应用。
    """
    import uvicorn
    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, factory=True)
    typer.echo("应用已启动。")


if __name__ == "__main__":
    app()