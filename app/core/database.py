# -*- coding: utf-8 -*-

from collections.abc import Generator
from sqlmodel import create_engine, Session, select
from app.core.logger import logger

from app.core.config import settings

# 创建数据库引擎，增加连接池配置
engine = create_engine(url=settings.DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话连接"""
    with Session(bind=engine) as session:
        yield session

async def create_db_and_tables() -> None:
    from app.model.user import User
    with Session(bind=engine) as session:
        admin_user: User | None = session.exec(select(User).where(User.username == "admin")).first()
        if not admin_user:
            admin: User = User(name="管理员", username="admin", password="123456", description="管理员", is_superuser=True)
            session.add(instance=admin)
            session.commit()
            logger.info("管理员账号初始化成功")
        else:
            logger.info("管理员用户已存在, 无需创建")
