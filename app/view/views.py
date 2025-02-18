# -*- coding: utf-8 -*-

from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request, WebSocket, templating, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from openai import OpenAI

from app.core.setting import Settings, get_settings
from app.utils.tasks import task

templates = templating.Jinja2Templates(directory="templates")

router = APIRouter()


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

