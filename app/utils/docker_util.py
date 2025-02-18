# -*- coding: utf-8 -*-

import docker


class DockerUtil:
    """
    Docker API封装
    """
    def __init__(self):
        # 连接当前docker服务
        self.client = docker.from_env()
        # 连接远程docker服务
        self.client = docker.Dockerclient("ssh://username@yourip", use_ssh_client=True)

    def get_docker_version(self):
        """docker版本信息"""
        return self.client.version()

    def get_container_list(self):
        """docker容器列表"""
        return self.client.containers.list()

    def get_image_list(self):
        """docker镜像列表"""
        return self.client.images.list()


# 创建DockerAPI对象
docker_api = DockerUtil()

# 调用封装的方法
version = docker_api.get_docker_version()
containers = docker_api.get_container_list()
images = docker_api.get_image_list()

# 打印结果
print("Docker版本信息:", version)
print("Docker容器列表:")
for container in containers:
    print(container.name)
print("Docker镜像列表:")
for image in images:
    print(image.tags)
