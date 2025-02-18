# -*- coding: utf-8 -*-

from typing import Any, AsyncGenerator
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.core.exceptions import register_exception_handler
from app.core.middlewares import register_middleware_handler
from app.core.router import register_router_handler
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """
    自定义生命周期
    """
    logger.info(f'服务启动...')

    # from sqlmodel import SQLModel, Session
    # from app.core.database import engine
    # from app.model.demo import User
    # SQLModel.metadata.drop_all(engine)
    # SQLModel.metadata.create_all(engine)
    # # 使用 get_db() 来获取会话管理器
    # with Session(engine) as session:
    #     admin = User(name="admin", password="123456", description="管理员", is_active=True, is_superuser=True)
    #     session.add(admin)
    #     session.commit()
    # logger.info(f'数据库初始化...')
    yield
    logger.info(f'服务关闭...')

def create_app() -> FastAPI:

    # 创建FastAPI应用
    app = FastAPI(lifespan=lifespan)

    # 挂载静态文件
    app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

    # 注册路由
    register_router_handler(app)

    # 注册中间件
    register_middleware_handler(app)

    # 注册异常
    register_exception_handler(app)

    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)