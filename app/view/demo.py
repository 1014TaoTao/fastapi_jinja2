# -*- coding: utf-8 -*-

from typing import Any, Optional
from fastapi import Request, APIRouter, Depends, status, Path, Form, templating
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session

from app.core.agent import Agent
from app.core.crud import BaseCRUD
from app.model.demo import UserFilterParams, User, UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.core.database import get_db
from app.core.config import settings

templates = templating.Jinja2Templates(directory="templates")

router = APIRouter()

def json_response(result: bool, message: str, data: Optional[Any] = None):
    return JSONResponse(
        status_code=200 if result else 400,
        content={"result": result, "message": message, "data": data}
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
        return json_response(result=False, message="用户名已存在")
    
    user_data = UserCreateSchema(name=username, password=password, description=description)
    user = BaseCRUD(db).create(User, user_data)
    return json_response(result=True, message="用户创建成功", data=user.model_dump())

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
        return json_response(result=False, message="用户不存在")

    if existing_user.is_superuser:
        return json_response(result=False, message="超级管理员不允许修改")

    user_data = UserUpdateSchema(name=username, password=password, description=description)
    user = BaseCRUD(db).update(User, user_id, user_data)
    return json_response(result=True, message="用户更新成功", data=user.model_dump())

@router.delete("/user/{user_id}", summary="删除用户")
def delete(
    user_id: int = Path(..., example=1),
    db: Session = Depends(get_db)
):
    """删除用户"""
    existing_user = BaseCRUD(db).get(User, filters={"id": ("eq", user_id)})
    if not existing_user:
        return json_response(result=False, message="用户不存在")

    if existing_user.is_superuser:
        return json_response(result=False, message="超级管理员不允许删除")

    result = BaseCRUD(db).delete(User, user_id)
    return json_response(result=True, message="用户删除成功", data=result)

@router.get("/", summary="登陆页面")
async def login_page(request: Request):
    # 渲染登录页面
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": "",
            "result": False,
        },
    )

@router.post("/login", summary="登陆请求")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = BaseCRUD(db).get(User, filters={"username": ("eq", username)})
    if not existing_user or existing_user.password != password:
        return templates.TemplateResponse(
            name="login.html",
            context={
                "request": request,
                "message": "用户名或密码错误",
                "result": False,
            },
        )
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

@router.get("/home", summary="首页页面")
async def home(request: Request):
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )

@router.get("/ai", summary="大模型")
async def home(request: Request):
    return templates.TemplateResponse(
        name="ai.html",
        context={"request": request}
    )

@router.post("/ai", summary="智能体")
async def home(model_type: str= Form(...), query: str= Form(...)):
    if model_type == "qwen":
        agent = Agent(base_url=settings.QWEN_BASE_URL, model=settings.QWEN_MODEL, api_key=settings.QWEN_API_KEY)
    elif model_type == "deepseek":
        agent = Agent(base_url=settings.DEEPSEEK_BASE_URL, model=settings.DEEPSEEK_MODEL, api_key=settings.DEEPSEEK_API_KEY)
    else:
        return json_response(result=False, message="模型类型错误")
    
    result = await agent.seed_message(query)
    

    return json_response(result=True, message="对话成功", data=result)