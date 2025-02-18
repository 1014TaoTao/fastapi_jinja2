# -*- coding: utf-8 -*-

import uuid
from typing import Optional
from fastapi import Query
from sqlmodel import Field, SQLModel

# 创建模型
class UserCreateSchema(SQLModel):
    name: str = Field(min_length=1, max_length=255, description="用户名")
    password: str = Field(min_length=6, max_length=40, description="密码")
    description: Optional[str] = Field(default=None, max_length=255, description="描述")

# 更新模型
class UserUpdateSchema(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="用户名")
    password: Optional[str] = Field(default=None, min_length=8, max_length=40, description="密码")
    description: Optional[str] = Field(default=None, max_length=255, description="描述")
    is_active: Optional[bool] = Field(default=None, description="是否激活")
    is_superuser: Optional[bool] = Field(default=None, description="是否超级用户")

# 响应模型
class UserOutSchema(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="用户ID", index=True)
    name: str = Field(description="用户名")
    is_active: bool = Field(description="是否激活")
    is_superuser: bool = Field(description="是否超级用户")
    description: Optional[str] = Field(description="描述")

# ORM 模型
class User(UserCreateSchema, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="用户ID", index=True)
    name: str = Field(min_length=1, max_length=255, description="用户名", index=True)
    password: str = Field(min_length=6, max_length=40, description="密码")
    is_active: bool = Field(default=True, description="是否激活")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    description: Optional[str] = Field(default=None, max_length=255, description="描述")


class UserFilterParams:
    def __init__(
            self,
            name: Optional[str] = Query(None, description="名称", min_length=1, max_length=255, title="名称"),
    ) -> None:
        self.name = ("like", name)
