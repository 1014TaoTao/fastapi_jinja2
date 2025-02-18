# -*- coding: utf-8 -*-

import uuid
from typing import Any, Optional, List, Dict, Annotated
from fastapi import Request, APIRouter, Depends, Query, status, HTTPException, Path, BackgroundTasks, Form, templating, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlmodel import Session
from openai import OpenAI
from pydantic import ValidationError

from app.core.crud import BaseCRUD
from app.model.demo import UserFilterParams, User, UserCreateSchema, UserUpdateSchema, UserOutSchema
from app.core.database import get_db 
from app.core.setting import Settings, get_settings
from app.utils.tasks import task

templates = templating.Jinja2Templates(directory="templates")

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


@router.get("/", response_class=HTMLResponse)
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


@router.post("/login", response_class=HTMLResponse)
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


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        name="about.html",
        context={"request": request}
    )


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    # 渲染初始页面
    return templates.TemplateResponse(
        name="chat.html",
        context={
            "request": request,
            "model_type": "",
            "message": "",
            "response": "",
            "error_message": "",
        },
    )


@router.post("/chat", summary="大模型对话")
async def ai(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)], 
    model_type: str = Form(...), 
    message: str = Form(...),
    response_class=HTMLResponse
):
    response = None

    def chat(api_key, base_url, model):
        try:
            content: str = 'You are a helpful assistant.'
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': content},
                    {'role': 'user', 'content': message}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return templates.TemplateResponse(
                name="chat.html",
                context={
                    "model_type": model_type,
                    "message": message,
                    "request": request,
                    "response": str(e),
                    "error_message": "",
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

    if model_type == "qwen":
        response = chat(settings.QWEN_API_KEY,
                        settings.QWEN_BASE_URL, settings.QWEN_MODEL)
    else:
        response = chat(settings.DEEPSEEK_API_KEY,
                        settings.DEEPSEEK_BASE_URL, settings.DEEPSEEK_MODEL)
    return templates.TemplateResponse(
        name="chat.html",
        context={
            "model_type": model_type,
            "message": message,
            "request": request,
            "response": response,
            "error_message": "",
        },
        status_code=status.HTTP_200_OK
    )

@router.websocket("/ws", name="websocket")
async def websocket_endpoint(websocket: WebSocket):
    # ws://127.0.0.1:8000/api/v1/system/auth/ws
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@router.get("/task", summary="模拟fastapi自带后台任务-模拟流式响应")
async def stream_response(background_tasks: BackgroundTasks, *args, **kwargs):

    background_tasks.add_task(task, *args, **kwargs)
    return stream_response(
        data=task(*args, **kwargs),
        headers={"X-Custom-Header": "Streaming-Response"},
        media_type="text/plain",
    )

