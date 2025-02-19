# -*- coding: utf-8 -*-

import json
from typing import Optional
from fastapi import Request, APIRouter, Depends, Query, status, HTTPException, Path, BackgroundTasks, Form, templating, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlmodel import Session

from app.core.crud import BaseCRUD
from app.model.demo import UserFilterParams, User, UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.core.database import get_db 
from app.utils.tasks import task
from app.core.logger import logger

templates = templating.Jinja2Templates(directory="templates")

router = APIRouter()

def json_response(success: bool, message: str, data: Optional[dict] = None):
    return JSONResponse(
        status_code=200 if success else 400,
        content={"success": success, "message": message, "data": data}
    )

@router.get("/users", summary="用户列表")
def list(
    request: Request,
    filters: UserFilterParams = Depends(),
    db: Session = Depends(get_db)
):
    if filters:
        filters = filters.__dict__

    result = BaseCRUD(db).list(User, UserOutSchema, filters=filters)

    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "users": result
        },
    )

@router.post("/user", summary="创建用户")
def create(
    username: str = Form(...),
    password: str = Form(...),
    description: str = Form(None), 
    db: Session = Depends(get_db)
):
    """创建用户"""
    existing_user = BaseCRUD(db).get(User, filters={"name": ("eq", username)})
    if existing_user:
        return json_response(success=False, message="用户名已存在")
    
    user_data = UserCreateSchema(name=username, password=password, description=description)
    user = BaseCRUD(db).create(User, user_data)
    return json_response(success=True, message="用户创建成功", data=user.model_dump())

@router.put("/user/{user_id}", summary="更新用户")
def update(
    username: str = Form(...),
    password: str = Form(...),
    description: str = Form(None), 
    user_id: int = Path(..., example=1), 
    db: Session = Depends(get_db)
):
    """更新用户"""
    existing_user = BaseCRUD(db).get(User, filters={"id": ("eq", user_id)})
    if not existing_user:
        return json_response(success=False, message="用户不存在")

    if existing_user.is_superuser:
        return json_response(success=False, message="超级管理员不允许修改")

    user_data = UserUpdateSchema(name=username, password=password, description=description)
    user = BaseCRUD(db).update(User, user_id, user_data)
    return json_response(success=True, message="用户更新成功", data=user.model_dump())


@router.delete("/user/{user_id}", summary="删除用户")
def delete(
    user_id: int = Path(..., example=1),
    db: Session = Depends(get_db)
):
    """删除用户"""
    existing_user = BaseCRUD(db).get(User, filters={"id": ("eq", user_id)})
    if not existing_user:
        return json_response(success=False, message="用户不存在")

    if existing_user.is_superuser:
        return json_response(success=False, message="超级管理员不允许删除")

    result = BaseCRUD(db).delete(User, user_id)
    return json_response(success=True, message="用户删除成功", data=result)


@router.get("/", summary="登陆页面")
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


@router.post("/login", summary="登陆请求")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = BaseCRUD(db).get(User, filters={"name": ("eq", username)})
    if not existing_user or existing_user.password != password:
        return templates.TemplateResponse(
            name="login.html",
            context={
                "request": request,
                "message": "用户名或密码错误",
                "success": False,
            },
        )
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@router.get("/home", summary="首页页面")
async def home(request: Request):
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )


# @router.get("/task", summary="模拟fastapi自带后台任务-模拟流式响应")
# async def stream_response(background_tasks: BackgroundTasks, *args, **kwargs):
#     background_tasks.add_task(task, *args, **kwargs)
#     return stream_response(
#         data=task(*args, **kwargs),
#         headers={"X-Custom-Header": "Streaming-Response"},
#         media_type="text/plain",
#     )

# @router.websocket("/ws", name="websocket")
# async def websocket_endpoint(websocket: WebSocket):
#     # ws://127.0.0.1:8000/api/v1/system/auth/ws
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")
