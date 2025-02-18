# -*- coding: utf-8 -*-

import json
import logging
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from jsonpath import jsonpath



logger = logging.getLogger(__name__)

class BaseAssertion:
    """断言基类"""
    
    @staticmethod
    def equals(actual: Any, expect: Any) -> bool:
        return actual == expect
    
    @staticmethod
    def not_equals(actual: Any, expect: Any) -> bool:
        return actual != expect
    
    @staticmethod
    def contains(actual: Any, expect: Any) -> bool:
        return expect in str(actual)
    
    @staticmethod
    def not_contains(actual: Any, expect: Any) -> bool:
        return expect not in str(actual)
    
    @staticmethod
    def greater_than(actual: Any, expect: Any) -> bool:
        return float(actual) > float(expect)
    
    @staticmethod
    def less_than(actual: Any, expect: Any) -> bool:
        return float(actual) < float(expect)
    
    @staticmethod
    def jsonpath_equals(actual: Dict, expect: str) -> bool:
        result = jsonpath(actual, expect)
        return bool(result)

class RequestHandler:
    """请求处理类"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 2):
        """
        :param timeout: 超时时间(秒)
        :param max_retries: 最大重试次数
        """
        self.session = requests.Session()
        # 设置重试机制
        self.session.mount('http://', HTTPAdapter(max_retries=max_retries))
        self.session.mount('https://', HTTPAdapter(max_retries=max_retries))
        self.timeout = timeout
        self.assertion = BaseAssertion()

    def send_request(
        self,
        url: str,
        method: str,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        :param url: 请求地址
        :param method: 请求方法
        :param headers: 请求头
        :param params: 查询参数
        :param body: 请求体
        :param files: 文件
        :param timeout: 超时时间
        :return: 响应结果
        """
        # 准备请求数据
        kwargs = {
            'url': url,
            'method': method.upper(),
            'headers': headers,
            'params': params,
            'timeout': timeout or self.timeout
        }
        
        # 处理请求体
        if files:
            kwargs['files'] = files
        elif body:
            if headers and 'application/json' in headers.get('Content-Type', ''):
                kwargs['json'] = body
            else:
                kwargs['data'] = body

        # 发送请求
        response = self.session.request(**kwargs)
        
        # 处理响应
        try:
            response_body = response.json()
        except json.JSONDecodeError:
            response_body = response.text

        result = {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'headers': dict(response.headers),
            'body': response_body,
            'request': {
                'url': url,
                'method': method,
                'headers': headers,
                'params': params,
                'body': body,
                'files': files
            }
        }
        return result


    def assert_response(self, response: Dict[str, Any], expected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        断言响应结果
        :param response: 响应结果
        :param expected: 断言配置列表
        :return: 断言结果列表
        """
        results = []
        for expect in expected:
            actual = None
            expect_type = expect.get('type')
            expect_rule = expect.get('rule')
            expect_value = expect.get('expect')

            # 获取实际值
            if expect_type == 'status_code':
                actual = response['status_code']
            elif expect_type == 'response_time':
                actual = response['response_time']
            elif expect_type == 'body':
                actual = response['body']
            elif expect_type == 'headers':
                actual = response['headers']
            
            # 执行断言
            assertion_method = getattr(self.assertion, expect_rule, None)
            if assertion_method:
                is_pass = assertion_method(actual, expect_value)
                results.append({
                    'type': expect_type,
                    'rule': expect_rule,
                    'expect': expect_value,
                    'actual': actual,
                    'result': is_pass
                })
            else:
                raise ValueError(msg=f"不支持的断言规则: {expect_rule}")
    
        return results

