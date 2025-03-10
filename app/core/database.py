# -*- coding: utf-8 -*-

from typing import Generator
from sqlmodel import create_engine, Session, SQLModel, select

from app.core.config import settings
from app.core.logger import logger

# 创建数据库引擎，增加连接池配置
connect_args = {"check_same_thread": False}
engine = create_engine(url=settings.DATABASE_URL, echo=True, connect_args=connect_args)

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话连接"""
    with Session(engine) as session:
        yield session

async def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)
    # SQLModel.metadata.create_all(engine)
    from app.model.demo import User
    with Session(engine) as session:
        admin_user = session.exec(select(User).where(User.username == "admin")).first()
        if not admin_user:
            admin = User(name="管理员", username="admin", password="123456", description="管理员", is_superuser=True)
            session.add(admin)
            session.commit()
            logger.info("管理员用户已创建")
        else:
            logger.info("管理员用户已存在")
