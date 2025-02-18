# -*- coding: utf-8 -*-

import uuid
from typing import Any, Optional, List, Dict
from fastapi import APIRouter, Depends, Query, status, HTTPException, Path
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.crud import BaseCRUD
from app.model.demo import UserFilterParams, User, UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.core.database import get_db 
from pydantic import ValidationError

router = APIRouter()

@router.get("/detail/{user_id}", summary="获取单个用户数据", response_model=UserOutSchema)
def detail(
    user_id: str = Path(..., title="The ID of the user to get", example="8a05fbb1-71ce-4e7e-8e4c-01664bfbabe1"),
    db: Session = Depends(get_db)
) -> UserOutSchema:
    """获取单个用户数据"""
    try:
        parsed_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 UUID 格式")
    user = BaseCRUD(db).get(User, UserOutSchema, filters={"id": ("eq", str(parsed_uuid))})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return JSONResponse(content=user.model_dump(), status_code=status.HTTP_200_OK)

@router.get("/list", summary="获取所有用户数据", response_model=List[UserOutSchema])
def list(
    order_by: Optional[List[Dict]] = Query(None, title="排序字段", example=[{'field': 'id', 'direction': 'desc'}]),
    db: Session = Depends(get_db)
) -> List[UserOutSchema]:
    """获取所有用户数据（支持排序）"""
    users = BaseCRUD(db).list(User, UserOutSchema, order_by=order_by)
    users_list_dict = [u.model_dump() for u in users]
    return JSONResponse(content=users_list_dict, status_code=status.HTTP_200_OK)

@router.get("/page", summary="分页获取用户数据", response_model=Dict[str, Any])
def page(
    offset: int = Query(0, title="偏移量", example=0),
    limit: int = Query(10, title="每页数量", example=10),
    order_by: Optional[List[Dict]] = Query(None, title="排序字段", example=[{'field': 'id', 'direction': 'desc'}]),
    filters: UserFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """分页获取用户数据（支持排序和过滤）"""
    result = BaseCRUD(db).page(User, UserOutSchema, offset=offset, limit=limit, order_by=order_by, filters=filters.__dict__)
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)

@router.post("/create", summary="创建用户", response_model=UserOutSchema)
def create(
    user: UserCreateSchema,
    db: Session = Depends(get_db)
) -> UserOutSchema:
    """创建用户"""
    try:
        db_user = BaseCRUD(db).create(User, user)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
    return JSONResponse(content=db_user.model_dump(), status_code=status.HTTP_200_OK)

@router.put("/update/{user_id}", summary="更新用户", response_model=UserOutSchema)
def update(
    user: UserUpdateSchema,
    user_id: str = Path(..., title="The ID of the user to update", example="8a05fbb1-71ce-4e7e-8e4c-01664bfbabe1"),
    db: Session = Depends(get_db)
) -> UserOutSchema:
    """更新用户"""
    try:
        parsed_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 UUID 格式")
    try:
        user_dict = user.model_dump(exclude_unset=True)
        db_user = BaseCRUD(db).update(User, str(parsed_uuid), user_dict)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return JSONResponse(content=db_user.model_dump(), status_code=status.HTTP_200_OK)

@router.delete("/delete/{user_id}", summary="删除用户")
def delete(
    user_id: str = Path(..., title="The ID of the user to delete", example="8a05fbb1-71ce-4e7e-8e4c-01664bfbabe1"),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """删除用户"""
    try:
        parsed_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的 UUID 格式")
    result = BaseCRUD(db).delete(User, parsed_uuid)
    return JSONResponse(
        content=result,
        status_code=status.HTTP_200_OK
    )
