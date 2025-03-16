# -*- coding: utf-8 -*-

import typer
import uvicorn
from typer.main import Typer
from alembic import command
from alembic.config import Config
from collections.abc import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import asynccontextmanager

from app.core.logger import logger
from app.core.database import create_db_and_tables
from app.core.exceptions import register_exception_handler
from app.core.middlewares import register_middleware_handler

app: Typer = typer.Typer()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    pass
    """
    自定义生命周期
    """
    logger.info(f'服务启动...{app.title}')
    await create_db_and_tables()
    yield
    logger.info(f'服务关闭...{app.title}')

# 初始化 Alembic 配置
alembic_cfg: Config = Config(file_="alembic.ini")

@app.command()
def revision(message: str = "生成新的 Alembic 迁移脚本") -> None:
    """
    生成新的 Alembic 迁移脚本。
    """
    command.revision(config=alembic_cfg, message=message, autogenerate=True)
    typer.echo(message=f"迁移脚本已生成: {message}")

@app.command()
def upgrade() -> None:
    """
    应用最新的 Alembic 迁移。
    """
    command.upgrade(config=alembic_cfg, revision="head")
    typer.echo(message="所有迁移已应用。")

def create_app() -> FastAPI:

    # 创建FastAPI应用
    app: FastAPI = FastAPI(lifespan=lifespan, debug=True)

    # 挂载静态文件
    app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

    # # 注册中间件
    register_middleware_handler(app)

    # # 注册异常
    register_exception_handler(app)

    # 注册路由
    from app.view.user import router as user_router
    Router = APIRouter()
    Router.include_router(router=user_router, tags=["用户模块"])
    app.include_router(router=Router)

    return app

@app.command()
def run() -> None:
    """
    启动应用。
    """
    uvicorn.run(app="main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)


if __name__ == "__main__":
    app()