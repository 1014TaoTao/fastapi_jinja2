# -*- coding: utf-8 -*-

import time
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.log import logger


class CustomCORSMiddleware(CORSMiddleware):
    """CORS跨域中间件"""
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(
            app,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True
        )


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    记录请求日志中间件: 提供一个基础的中间件类，允许你自定义请求和响应处理逻辑。
    """
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time: float = time.time()
        
        logger.info(
            f"请求来源: {request.client.host if request.client else '未知'}, "
            f"请求方法: {request.method}, "
            f"请求路径: {request.url.path}, "
        )
        
        try:
            response: Response = await call_next(request)
            process_time: float = round(time.time() - start_time, 5)
            response.headers["X-Process-Time"] = str(process_time)
            
            if response.status_code == status.HTTP_200_OK:
                logger.info(
                    f"请求成功: {response.status_code},"
                    f"响应内容长度: {response.headers.get('content-length', '0')}, "
                    f"处理时间: {process_time}s"
                )
            else:
                logger.error(
                    f"请求失败: {response.status_code},"
                    f"响应内容长度: {response.headers.get('content-length', '0')}, "
                    f"处理时间: {process_time}s,"
                )
            return response
        
        except Exception as e:
            logger.error(f"系统异常: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"系统异常，请联系管理员: {str(e)}")

def register_middleware_handler(app: FastAPI) -> None:
    app.add_middleware(middleware_class=CustomCORSMiddleware)
    app.add_middleware(middleware_class=RequestLogMiddleware)
