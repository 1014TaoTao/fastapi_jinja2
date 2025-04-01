# -*- coding: utf-8 -*-

import json
from fastapi import HTTPException, Query, Request, APIRouter, Depends, status, Path, Form, templating
from fastapi.responses import RedirectResponse, JSONResponse
from sqlmodel import Session, desc, func, select, asc, and_, or_

from app.model.user import User, UserCreateSchema, UserUpdateSchema, Page, Response
from app.core.database import get_db
from app.core.log import logger

templates = templating.Jinja2Templates(directory="templates")


router = APIRouter()

@router.get("/", summary="登陆页面")
async def index(
    request: Request, 
):
    return templates.TemplateResponse(request=request,name="login.html")

@router.get("/home", summary="首页页面")
async def home(
    request: Request
):
    return templates.TemplateResponse(request=request, name="home.html")

@router.post("/login", summary="登陆请求")
async def login(
    request: Request,
    username: str = Form(..., description="账号"), 
    password: str = Form(..., description="密码"), 
    db: Session = Depends(get_db)
):
    existing_user = db.exec(select(User).where(User.username == username)).first()
    if not existing_user or existing_user.password != password:
        logger.warning(f"用户名或密码错误")
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context=Response(
                code=status.HTTP_401_UNAUTHORIZED,
                message="用户名或密码错误"
            ).model_dump(),
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    logger.info(f"用户 {username} 登录成功")
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

@router.get("/users", summary="用户分页", response_model=Page)
async def list(
    request: Request,
    offset: int = Query(default=0, description="偏移量"),
    limit: int = Query(default=10, description="每页数量"),
    order_by: str | None = Query(default=None, description="排序字段", example={"id": "asc"}),
    name: str | None = Query(default=None, description="名称"),
    db: Session = Depends(get_db)
):
    sql = select(User)
    if name:
        sql = sql.where(and_(User.name.contains(name)))

    # 获取总数
    total = db.exec(select(func.count()).select_from(sql)).first()
    if total is None:
        total = 0

    # 处理排序
    if order_by:
        try:
            order_by_dict = json.loads(order_by)
            for key, value in order_by_dict.items():
                if not hasattr(User, key):
                    logger.warning(f"无效的排序字段: {key}")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"无效的排序字段: {key}")
                order_func = desc if value.lower() == 'desc' else asc
                sql = sql.order_by(order_func(getattr(User, key)))
        except json.JSONDecodeError:
            logger.warning("排序参数格式错误")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="排序参数格式错误")

    # 分页
    users = db.exec(sql.offset(offset).limit(limit)).all()

    logger.info("查询用户成功")
    return templates.TemplateResponse(
        request=request,
        name="user.html",
        context=Response(
            code=status.HTTP_200_OK,
            message="获取列表成功",
            data=Page(
                items=[User.model_validate(user).model_dump() for user in users],
                total=total,
                page_no=offset // limit + 1 if limit else 1,
                page_size=limit,
                total_pages=(total + limit - 1) // limit if limit else 1,
                has_next=offset + limit < total
            ).model_dump()
        ).model_dump(),
        status_code=status.HTTP_200_OK
    )

@router.post("/user", summary="创建用户", response_model=Response[User])
async def create(
    name: str = Form(..., description="用户名"),
    username: str = Form(...,  description="账号"),
    password: str = Form(..., description="密码"),
    description: str = Form(None, description="描述"), 
    db: Session = Depends(get_db)
):
    """创建用户"""
    existing_user = db.exec(select(User).where(User.username == username)).first()
    if existing_user:
        logger.warning(f"创建用户失败：账号 {username} 已存在")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"账号 {username} 已存在")
    
    user_create_schema = UserCreateSchema(
        name=name, 
        username=username, 
        password=password, 
        description=description
    )
    user = User.model_validate(user_create_schema)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"用户 {name}({username}) 创建成功")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=Response(
            message="创建用户成功",
            data=user.model_dump()
        ).model_dump()
    )

@router.get("/user/{id}", summary="用户详情", response_model=User)
async def detail(
    id: int = Path(..., description="用户ID"), 
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    existing_user = db.get(User, id)
    if not existing_user:
        logger.warning(f"用户{id}不存在")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    logger.info(f"获取用户{id}详情成功")
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=Response(code=status.HTTP_200_OK, message=f"获取用户{id}详情成功", data=existing_user.model_dump()).model_dump()
    )

@router.put("/user/{id}", summary="更新用户", response_model=User)
async def update(
    id: int = Path(..., description="用户ID"), 
    name: str | None = Form(None, description="用户名"),
    username: str | None = Form(None, description="用户名"),
    password: str | None = Form(None, description="密码"),
    description: str | None = Form(None, description="描述"), 
    db: Session = Depends(get_db)
):
    """更新用户"""
    existing_user = db.get(User, id)
    if not existing_user:
        logger.warning(f"用户{id}不存在")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"用户{id}不存在")
    if existing_user.is_superuser:
        logger.warning("超级管理员不允许修改")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员不允许修改")

    user_update_schema = UserUpdateSchema(name=name, username=username, password=password, description=description)
    update_data_dict = user_update_schema.model_dump(exclude_unset=True)
    
    existing_user.sqlmodel_update(update_data_dict)
    db.add(existing_user)
    db.commit()
    db.refresh(existing_user)
    logger.info(f"更新用户{id}成功")
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=Response(code=status.HTTP_200_OK, message=f"更新用户{id}成功", data=existing_user.model_dump()).model_dump()
    )

@router.delete("/user/{id}", summary="删除用户", response_model=User)
async def delete(
    id: int = Path(..., description="用户ID"), 
    db: Session = Depends(get_db)
):
    """删除用户"""
    existing_user = db.get(User, id)
    if not existing_user:
        logger.warning(f"用户{id}不存在")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"用户{id}不存在")
    if existing_user.is_superuser:
        logger.warning("超级管理员不允许删除")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="超级管理员不允许删除")
    
    db.delete(existing_user)
    db.commit()
    logger.info(f"删除用户{id}成功")
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=Response(code=status.HTTP_200_OK, message=f"删除用户{id}成功", data=existing_user.model_dump()).model_dump()
    )


