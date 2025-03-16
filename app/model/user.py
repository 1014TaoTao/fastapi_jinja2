# -*- coding: utf-8 -*-

from sqlmodel import Field, SQLModel
from typing import TypeVar, Generic

T = TypeVar("T")

class Response(SQLModel, Generic[T]):
    code: int = 200
    message: str = ""
    data: T | None = None


# 分页模型
class Page(SQLModel):
    items: list = Field(default=[], description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page_no: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=10, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")
    has_next: bool = Field(default=False, description="是否有下一页")


# 创建模型
class UserCreateSchema(SQLModel):
    name: str = Field(min_length=2, max_length=50, description="用户名")
    username: str = Field(min_length=4, max_length=20, description="账号")
    password: str = Field(min_length=6, max_length=20, description="密码")
    description: str | None = Field(default=None, max_length=255, description="描述")


# 更新模型
class UserUpdateSchema(SQLModel):
    name: str | None = Field(default=None, description="用户名")
    username: str | None = Field(default=None, description="用户名")
    password: str | None = Field(default=None, description="密码")
    description: str | None = Field(default=None, description="描述")


# ORM 模型
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, description="用户ID")
    name: str = Field(index=True, nullable=False, description="用户名")
    username: str = Field(unique=True, description="账号")
    password: str = Field(description="密码")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    description: str | None = Field(default=None, description="描述")

