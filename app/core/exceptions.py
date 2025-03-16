# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request, status, HTTPException, templating
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from app.core.logger import logger

def register_exception_handler(app: FastAPI) -> None:

    @app.exception_handler(exc_class_or_status_code=HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """请求异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content=exc.detail)

    @app.exception_handler(exc_class_or_status_code=RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求参数验证异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc.body}")
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=exc.body)

    @app.exception_handler(exc_class_or_status_code=ResponseValidationError)
    async def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
        """响应参数验证异常处理器"""
        logger.error(f"请求地址: {request.url}, 错误详情: {exc.body}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(exc.body))
