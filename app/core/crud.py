# -*- coding: utf-8 -*-

from typing import Any, Tuple, Type, TypeVar, Optional, Dict, List, Union
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select, func
from sqlalchemy.sql import expression, and_
from sqlalchemy import asc, desc


# 定义类型变量
T = TypeVar('T', bound=SQLModel)  # ORM 模型类型
S_Create = TypeVar('S_Create', bound=SQLModel)  # 创建 Schema 类型
S_Update = TypeVar('S_Update', bound=SQLModel)  # 更新 Schema 类型
S_Out = TypeVar('S_Out', bound=SQLModel)  # 响应 Schema 类型


class BaseCRUD:
    def __init__(self, session: Session):
        self.session = session
    def _filters(
            self,
            query: expression.Select,
            model: Type[T],
            filters: Dict[str, Optional[Union[Tuple[str, Any], Any]]] = {}
        ) -> expression.Select:
            """应用过滤条件到查询"""
            # 存在情况 filters = {'name': ('like', None), 'age': ('gt', 18), 'sex': None, 'sex': '男'}
            if not filters:
                return query

            filter_conditions = []
            for field, filter_value in filters.items():
                if filter_value is None:
                    continue  # 忽略值为 None 的过滤条件

                if isinstance(filter_value, tuple):
                    op, value = filter_value
                else:
                    op = "eq"  # 默认操作符为 'eq'
                    value = filter_value

                if value is None:
                    continue  # 忽略操作符为 'like' 且值为 None 的过滤条件
                if hasattr(model, field):
                    column = getattr(model, field)
                    if op == "eq":  # 精确匹配
                        filter_conditions.append(column == value)
                    elif op == "like":  # 模糊匹配
                        filter_conditions.append(column.like(f"%{value}%"))
                    elif op == "gt":  # 大于
                        filter_conditions.append(column > value)
                    elif op == "lt":  # 小于
                        filter_conditions.append(column < value)
                    elif op == "between":  # 范围匹配
                        filter_conditions.append(column.between(*value))
            return query.filter(and_(*filter_conditions)) if filter_conditions else query

    def _order_by(
        self,
        query: expression.Select,
        model: Type[T],
        order_by: Optional[List[Dict[str, str]]] = []
    ) -> expression.Select:
        """应用排序条件到查询"""
        if not order_by or not isinstance(order_by, list):
            return query

        for order in order_by:
            field = order.get("field")
            direction = order.get("direction", "asc")
            if hasattr(model, field):
                column = getattr(model, field)
                if direction.lower() == "desc":
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
        return query

    def get(
        self,
        model: Type[T],
        filters: Dict[str, tuple] = {}
    ) -> T:
        """根据条件获取单个对象"""
        query = select(model)
        query = self._filters(query, model, filters)
        db_obj = self.session.exec(query).first()
        return db_obj

    def list(
        self,
        model: Type[T],
        schema_out: Type[S_Out],
        filters: Optional[Dict[str, tuple]] = {}
    ) -> List[S_Out]:
        """查询列表"""
        # 查询数据
        query = select(model)
        if filters:
            query = self._filters(query, model, filters)

        db_objs = self.session.exec(query).all()
        return [schema_out.model_validate(db_obj).model_dump() for db_obj in db_objs]

    def page(
    self,
    model: Type[T],
    schema_out: Type[S_Out],
    offset: int = 0,
    limit: int = 10,
    order_by: Optional[List[Dict[str, str]]] = [],
    filters: Optional[Dict[str, tuple]] = {}
) -> Dict[str, Any]:
        """分页查询"""
        # 查询数据
        query = select(model)
        if filters:
            query = self._filters(query, model, filters)
        
        # 应用排序和分页
        if order_by:
            query = self._order_by(query, model, order_by)
        
        query = query.offset(offset).limit(limit)

        db_objs = self.session.exec(query).all()

        # 查询总记录数（应用过滤条件后）
        total = self.session.exec(func.count(model.id)).scalar()

        return {
            "items": [schema_out.model_validate(db_obj).model_dump() for db_obj in db_objs],
            "total": int(total),  # 总记录数（过滤后）
            "page_no": int(offset) // limit + 1,  # 当前页码
            "page_size": int(limit),  # 每页数量
            "total_pages": int((total + limit - 1) // limit),  # 总页数
            "has_next": offset + limit < total,  # 是否有下一页
            "has_prev": offset > 0 # 是否有上一页
        }

    def create(
        self,
        model: Type[T],
        schema_in: S_Create,
    ) -> T:
        """创建对象"""
        db_obj = model.model_validate(schema_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(
        self,
        model: Type[T],
        obj_id: int,
        schema_in: S_Update,
    ) -> T:
        """更新对象"""
        db_obj = self.session.get(model, obj_id)
        if db_obj:
            update_data = schema_in.model_dump(exclude_unset=True)
            db_obj.sqlmodel_update(update_data)
            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
        else:
            raise HTTPException(status_code=404, detail="更新对象不存在")
        return db_obj

    def delete(
        self,
        model: Type[T],
        obj_id: int,
    ) -> str:
        """删除对象"""
        db_obj = self.session.get(model, obj_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="删除对象不存在")
        self.session.delete(db_obj)
        self.session.commit()
        return f"{obj_id} 已删除"


# 分页查询案例，已调试通过，业务有需求直接复用
# @router.get("/page", summary="分页获取用户数据")
# def page(
#     request: Request,
#     offset: int = Query(0, description="偏移量", example=0),
#     limit: int = Query(10, description="每页数量", example=10),
#     order_by: Optional[str] = Query(None, description="排序字段", example='[{"field": "id", "direction": "desc"}]'),
#     filters: Optional[UserFilterParams] = Depends(lambda: None),  # 设置默认值为 None
#     db: Session = Depends(get_db)
# ):
#     """分页获取用户数据（支持排序和过滤）"""
#     

#     # 解析排序参数
#     if order_by:
#         try:
#             order_by = json.loads(order_by)  # 将字符串解析为列表
#         except json.JSONDecodeError:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="排序参数格式错误")
#     if filters:
#         filters = filters.__dict__

#     # 调用 BaseCRUD 的分页方法
#     result = BaseCRUD(db).page(User, UserOutSchema, offset=offset, limit=limit, order_by=order_by, filters=filters)
#     return JSONResponse(status_code=status.HTTP_200_OK, content=result)
