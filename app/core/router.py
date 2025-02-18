# -*- coding: utf-8 -*-

from fastapi import APIRouter, FastAPI

from app.view.views import router
from app.view.demo import router as demo_router

def register_router_handler(app: FastAPI):
    Router = APIRouter(prefix="")
    Router.include_router(router=router, tags=["项目接口"])
    Router.include_router(router=demo_router, tags=["案例接口"])
    app.include_router(Router)
