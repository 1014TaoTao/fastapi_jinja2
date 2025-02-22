# -*- coding: utf-8 -*-

from typing import Generator
from sqlmodel import create_engine, Session

from app.core.setting import settings

# 创建数据库引擎，增加连接池配置
engine = create_engine(url=settings.DATABASE_URL)  # 调整连接池大小

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话连接"""
    with Session(engine) as session:
        yield session

