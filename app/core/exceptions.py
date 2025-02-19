# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request, logger, status, HTTPException, templating
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import logger


def register_exception_handler(app: FastAPI) -> None:
    """注册异常处理器"""
    @app.exception_handler(HTTPException)
    async def HttpExceptionHandler(request: Request, exc: HTTPException) -> JSONResponse:
        """HTTP异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    @app.exception_handler(RequestValidationError)
    async def ValidationExceptionHandler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求参数验证异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc}")
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=exc.body)

    @app.exception_handler(ResponseValidationError)
    async def ResponseValidationHandle(request: Request, exc: ResponseValidationError) -> JSONResponse:
        logger.error(f"请求地址: {request.url}, 错误详情: {exc}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc.body))

    @app.exception_handler(SQLAlchemyError)
    async def SQLAlchemyExceptionHandler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """数据库异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(exc.args))

    @app.exception_handler(ValueError)
    async def ValueExceptionHandler(request: Request, exc: ValueError) -> JSONResponse:
        """值异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc}")
        return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content=str(exc))

    templates = templating.Jinja2Templates(directory="templates")

    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc):
        return templates.TemplateResponse("404.html", {"request": request})
    
    @app.exception_handler(500)
    async def server_error_exception_handler(request: Request, exc):
        return templates.TemplateResponse("500.html", {"request": request})