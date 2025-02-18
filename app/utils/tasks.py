# -*- coding: utf-8 -*-

from datetime import datetime


def task(*args, **kwargs):
    """
    任务执行异步同步
    """
    return {
            "message": f"{datetime.now()}同步函数执行了",
            "data": args,
            "kwargs": kwargs
        }

async def async_task(*args, **kwargs):
    """
    任务执行异步
    """
    return {
            "message": f"{datetime.now()}异步函数执行了",
            "data": args,
            "kwargs": kwargs
        }
