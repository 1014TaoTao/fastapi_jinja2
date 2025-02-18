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

    # deepseek api 文档地址： https://api-docs.deepseek.com/zh-cn/
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_API_KEY: str
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # qwen api 文档地址： https://help.aliyun.com/zh/model-studio/getting-started/
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_KEY: str
    QWEN_MODEL: str = "qwen-plus"

    @property
    def DATABASE_URL(self) -> str:
        """数据库连接地址"""
        return f"sqlite:///{self.BASE_DIR.joinpath(self.SQLITE_DB_NAME)}?characterEncoding=UTF-8"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


settings = get_settings()
