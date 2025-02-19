# -*- coding: utf-8 -*-

from typing import Optional
from fastapi import Query
from sqlmodel import Field, SQLModel

# 创建模型
class UserCreateSchema(SQLModel):
    name: str = Field(description="用户名", index=True)
    password: str = Field(description="密码")
    description: Optional[str] = Field(default=None, description="描述")

# 更新模型
class UserUpdateSchema(SQLModel):
    name: Optional[str] = Field(default=None, description="用户名")
    password: Optional[str] = Field(default=None, description="密码")
    description: Optional[str] = Field(default=None, description="描述")

# 响应模型
class UserOutSchema(SQLModel):
    id: int
    name: str
    password: str
    description: str
    is_superuser: bool

# ORM 模型
class User(UserCreateSchema, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="用户ID")
    name: str = Field(description="用户名")
    password: str = Field(description="密码")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    description: Optional[str] = Field(default=None, max_length=255, description="描述")


class UserFilterParams:
    def __init__(
        self,
        name: Optional[str] = Query(None, description="名称", example="demo"),
    ) -> None:
        self.name = ("like", name)
