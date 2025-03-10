# -*- coding: utf-8 -*-

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # 项目根目录
    BASE_DIR: Path = Path(__file__).parent.parent.parent

    # sqlite 数据库名称
    SQLITE_DB_NAME: str

    # 千问大模型配置
    QWEN_BASE_URL: str
    QWEN_API_KEY: str
    QWEN_MODEL: str

    # deepseek 大模型配置
    DEEPSEEK_BASE_URL: str
    DEEPSEEK_API_KEY: str
    DEEPSEEK_MODEL: str


    @property
    def DATABASE_URL(self) -> str:
        """数据库连接地址"""
        return f"sqlite:///{self.BASE_DIR.joinpath(self.SQLITE_DB_NAME)}?characterEncoding=UTF-8"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


settings = get_settings()
