# -*- coding: utf-8 -*-

import json
from typing import Any, Optional, Dict, List
from fastapi import Request, APIRouter, Depends, Query, status, HTTPException, Path, BackgroundTasks, Form, templating, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlmodel import Session

from app.core.crud import BaseCRUD
from app.model.demo import UserFilterParams, User, UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.core.database import get_db 
from app.utils.tasks import task

templates = templating.Jinja2Templates(directory="templates")

router = APIRouter()

nav_links = [
    {"name": "首页", "url": "/home"},
    {"name": "用户管理", "url": "/user"},
    {"name": "关于我们", "url": "/about"},
]

@router.get("/detail/{user_id}", summary="获取单个用户数据", response_model=UserOutSchema)
def detail(user_id: int = Path(..., example=1),db: Session = Depends(get_db)) -> UserOutSchema:
    """获取单个用户数据"""
    user = BaseCRUD(db).get(User, filters={"id": ("eq", user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return JSONResponse(content=user.model_dump(), status_code=status.HTTP_200_OK)

@router.get("/user", summary="获取用户列表", response_model=None)
def list(request: Request, db: Session = Depends(get_db)):
    """获取所有用户数据"""
    users = BaseCRUD(db).list(User, UserOutSchema)
    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "nav_links": nav_links,
            "users": users
        }
    )

@router.get("/page", summary="分页获取用户数据", response_model=Dict[str, Any])
def page(
    offset: int = Query(description="偏移量", example=0),
    limit: int = Query(description="每页数量", example=10),
    order_by: Optional[str] = Query(None, description="排序字段", example='[{"field": "id", "direction": "desc"}]'),
    filters: UserFilterParams = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """分页获取用户数据（支持排序和过滤）"""
    # 解析排序参数
    order_by_list = []
    if order_by:
        try:
            order_by_list = json.loads(order_by)  # 将字符串解析为列表
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="排序参数格式错误")

    # 将过滤条件转换为字典
    filter_dict = {}
    if filters:
        filter_dict = filters.__dict__

    # 调用 BaseCRUD 的分页方法
    result = BaseCRUD(db).page(User, UserOutSchema, offset=offset, limit=limit, order_by=order_by_list, filters=filter_dict)
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)

@router.post("/create", summary="创建用户", response_model=UserOutSchema)
def create(user: UserCreateSchema, db: Session = Depends(get_db)) -> UserOutSchema:
    """创建用户"""
    # 检查用户名是否已存在
    existing_user = BaseCRUD(db).get(User, filters={"name": ("eq", user.name)})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    # 创建用户
    db_user = BaseCRUD(db).create(User, user)
    return JSONResponse(content=db_user.model_dump(), status_code=status.HTTP_201_CREATED)

@router.put("/update/{user_id}", summary="更新用户", response_model=UserOutSchema)
def update(user: UserUpdateSchema, user_id: int = Path(..., example=1), db: Session = Depends(get_db)) -> UserOutSchema:
    """更新用户"""
    # 检查用户是否存在
    existing_user = BaseCRUD(db).get(User, filters={"id": ("eq", user_id)})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if existing_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员不允许修改")
    # 更新用户
    db_user = BaseCRUD(db).update(User, user_id, user)
    return JSONResponse(content=db_user.model_dump(), status_code=status.HTTP_200_OK)

@router.delete("/delete/{user_id}", summary="删除用户", response_model=UserOutSchema)
def delete(user_id: int = Path(..., example=1), db: Session = Depends(get_db)) -> JSONResponse:
    """删除用户"""
    existing_user = BaseCRUD(db).get(User, filters={"id": ("eq", user_id)})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if existing_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员不允许删除")
    result = BaseCRUD(db).delete(User, user_id)
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get("/", summary="登陆页面", response_class=HTMLResponse)
async def login_page(request: Request):
    # 渲染登录页面
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": "",
            "success": False,
        },
    )

@router.post("/login",summary="登陆请求", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == "admin" and password == "123456":  # 简单检查用户名和密码是否非空
        # 登录成功，跳转到根路径
        return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    else:
        # 登录失败，返回登录页面并显示错误信息
        return templates.TemplateResponse(
            name="login.html",
            context={
                "request": request,
                "message": "用户名和密码错误",
                "success": False,
            },
        )

@router.get("/home",summary="首页页面", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request, "nav_links": nav_links}
    )

@router.get("/about", summary="关于页面",response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        name="about.html",
        context={"request": request, "nav_links": nav_links}
    )

@router.get("/task", summary="模拟fastapi自带后台任务-模拟流式响应")
async def stream_response(background_tasks: BackgroundTasks, *args, **kwargs):
    background_tasks.add_task(task, *args, **kwargs)
    return stream_response(
        data=task(*args, **kwargs),
        headers={"X-Custom-Header": "Streaming-Response"},
        media_type="text/plain",
    )

@router.websocket("/ws", name="websocket")
async def websocket_endpoint(websocket: WebSocket):
    # ws://127.0.0.1:8000/api/v1/system/auth/ws
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
