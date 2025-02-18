from typing import Type, TypeVar, Optional, Dict, Any, Union, List
import uuid
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select, func
from sqlalchemy.sql import expression, and_
from sqlalchemy import asc, desc

from app.core.logger import logger


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
            filters: Dict[str, tuple] = {} # {"id": ("eq", str(parsed_uuid))}
        ) -> expression.Select:
            """应用过滤条件到查询"""
            if not filters:
                return query

            filter_conditions = []
            for field, (op, value) in filters.items():
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
        order_by: Optional[List[Dict[str, str]]] = [] # [{'field': 'id', 'direction': 'desc'}]
    ) -> expression.Select:
        """应用排序条件到查询"""
        if not order_by or not isinstance(order_by, list):
            return query

        for order in order_by:
            field = order.get("field")
            direction = order.get("direction", "asc")  # 默认升序
            if hasattr(model, field):
                column = getattr(model, field)
                if direction.lower() == "desc":
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
        return query

    def _paginate_query(
        self,
        query: expression.Select,
        offset: int,
        limit: int
    ) -> expression.Select:
        """应用分页到查询"""
        return query.offset(offset).limit(limit)

    def get(
        self,
        model: Type[T],
        schema_out: Type[S_Out],
        filters: Dict[str, tuple] = {}
    ) -> Optional[S_Out]:
        """根据条件获取单个对象"""
        query = select(model)
        query = self._filters(query, model, filters)
        db_obj = self.session.exec(query).first()
        logger.debug(f"Retrieved object: {db_obj}")
        return schema_out.model_validate(db_obj) if db_obj else None

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
        query = self._filters(query, model, filters)
        query = self._order_by(query, model, order_by)
        query = self._paginate_query(query, offset, limit)
        db_objs = self.session.exec(query).all()
        items_list_dict = [schema_out.model_validate(db_obj).model_dump() for db_obj in db_objs]

        # 查询总记录数
        total_query = select(func.count(model.id))
        total_query = self._filters(total_query, model, filters)
        total = self.session.exec(total_query).scalar()

        logger.debug(f"Paged query result: {items_list_dict}, total: {total}")
        return {
            "items": items_list_dict,
            "total": total,
            "page_no": offset // limit + 1,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit,
            "has_next": offset + limit < total
        }

    def list(
        self,
        model: Type[T],
        schema_out: Type[S_Out],
        order_by: Optional[List[Dict[str, str]]] = [],
    ) -> List[S_Out]:
        """获取列表"""
        query = select(model)
        query = self._order_by(query, model, order_by)
        db_objs = self.session.exec(query).all()
        logger.debug(f"List query result: {db_objs}")
        return [schema_out.model_validate(db_obj) for db_obj in db_objs]

    def create(
        self,
        model: Type[T],
        schema_in: S_Create
    ) -> T:
        """创建对象"""
        db_obj = model.model_validate(schema_in) # 将输入数据转换为数据库对象
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        logger.debug(f"Created object: {db_obj}")
        return db_obj

    def update(
        self,
        model: Type[T],
        obj_id: uuid.UUID,
        schema_in: S_Update
    ) -> Optional[T]:
        """更新对象"""
        db_obj = self.session.get(model, obj_id)
        if db_obj:
            update_data = schema_in.model_dump(exclude_unset=True) # 只更新有值的字段
            # for key, value in update_data.items():
            #     setattr(db_obj, key, value)
            db_obj.sqlmodel_update(update_data)
            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
            logger.debug(f"Updated object: {db_obj}")
        else:
            logger.debug(f"Object not found: {obj_id}")
            raise HTTPException(status_code=404, detail="更新对象不存在")
        return db_obj

    def delete(
        self,
        model: Type[T],
        obj_id: uuid.UUID
    ) -> Dict[str, str]:
        """删除对象"""
        db_obj = self.session.get(model, obj_id)
        if db_obj:
            self.session.delete(db_obj)
            self.session.commit()
            logger.debug(f"Deleted object: {obj_id}")
            return {"msg": f"删除对象 {obj_id} 成功"}
        else:
            logger.debug(f"Object not found: {obj_id}")
            raise HTTPException(status_code=404, detail="删除对象不存在")

