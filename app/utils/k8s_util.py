# -*- coding: utf-8 -*-

import os

from kubernetes import client, config
from kubernetes.client.api_client import ApiClient


class K8sUtil:
    """
    Kubernetes API封装类
    """
    def __init__(self):
        # 获取kubeconfig文件路径
        config_path = os.path.join(r"../../../data/config")
        # 加载kubeconfig文件
        config.load_kube_config(config_file=config_path)
        v1_core = client.CoreV1Api()
        # 创建API客户端
        self.k8s_client = ApiClient()
        # 创建CoreV1Api实例
        self.api_instance = client.CoreV1Api(api_client=self.k8s_client)

    def get_namespaces(self) -> list:
        """
        Get list of namespaces.
        获取命名空间列表。
        """
        # 获取所有命名空间
        return self.api_instance.list_namespace(watch=False).items

    def get_services(self) -> list:
        """
        Get list of all services.
        获取所有服务的列表。
        """
        # 获取所有命名空间下的服务
        return self.api_instance.list_service_for_all_namespaces(watch=False).items

    def get_pods(self) -> list:
        """
        Get list of all pods.
        获取所有Pod的列表。
        """
        # 获取所有命名空间下的Pod
        return self.api_instance.list_pod_for_all_namespaces(watch=False).items
