# -*- coding: utf-8 -*-

from typing import Generator
from sqlmodel import create_engine, Session
from sqlalchemy.pool import QueuePool

from app.core.logger import logger
from app.core.setting import settings

# 创建数据库引擎，增加连接池配置
engine = create_engine(url=settings.DATABASE_URL, echo=True)

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话连接"""
    with Session(engine) as session:
        try:
            logger.debug("Database session started")
            yield session
        except Exception as e:
            logger.error(f"Database error: {e}")
            session.rollback()
            raise e
        finally:
            logger.debug("Database session closed")
            session.close()
