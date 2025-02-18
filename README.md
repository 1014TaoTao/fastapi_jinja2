<div align="center">
   <p align="center">
      <img src="./static/favicon.png" height="150" alt="logo"/>
   </p>
      <h1 align="center" style="margin: 30px 0 30px; font-weight: bold;">Fastapi_Jinja2</h1>

   <p align="center">
      <a href="https://gitee.com/tao__tao/fastapi_jinja2.git">
         <img src="https://gitee.com/tao__tao/fastapi_jinja2/badge/star.svg?theme=dark">
      </a>
      <a href="https://github.com/1014TaoTao/fastapi_jinja2.git">
         <img src="https://img.shields.io/github/stars/1014TaoTao/fastapi_jinja2?style=social">
      </a>
      <a href="https://gitee.com/tao__tao/fastapi_jinja2/blob/master/LICENSE">
         <img src="https://img.shields.io/badge/License-MIT-orange">
      </a>
      <img src="https://img.shields.io/badge/Python-≥3.10-blue">
   </p>
</div>

## FastAPI-Jinja2 项目简介

### 项目概述

FastAPI-Jinja2 是一个整合了多个流行技术栈的开源项目，旨在帮助开发者迅速启动并运行基于以下技术的Web应用程序：

- **FastAPI**: 高性能的Web框架，支持异步编程。
- **Jinja2**: 强大的模板引擎，用于生成HTML页面。
- **SQLModel**: 简单易用的ORM工具，简化数据库操作。
- **Loguru**: 灵活的日志记录库，提升日志管理效率。
- **Celery**: 分布式任务队列，处理后台任务。

### 参与和支持

感谢您的关注和支持！如果您觉得这个项目对您有帮助，请给我们点个Star！您的支持是我们前进的动力。同时，也欢迎各位开发者参与贡献，共同完善这个项目。

### 主要特性

- **快速上手**: 提供完整的项目结构和示例代码，减少初期配置时间。
- **模块化设计**: 各个组件独立开发，便于维护和扩展。
- **文档齐全**: 详细的README文档和API文档，方便学习和参考。
- **社区支持**: 完全开源，欢迎提交问题和Pull Request。

### 目录结构

```sh
fastapi_jinja2
├─ app
│  ├─ core                 # 核心层模块
│  ├─ model                # 数据层模块
│  ├─ config               # 配置层模块
│  ├─ view                 # 视图层模块
│  └─ utils                # 工具类模块
├─ logs                    # 日志目录
├─ static                  # 静态目录
├─ templates               # 模板目录
├─ .env                    # 项目环境配置文件
├─ .gitignore.py           # git 忽略文件
├─ main.py                 # 项目启动文件
├─ requirements.txt        # 项目依赖文件
├─ sqlite.db               # 项目数据库文件
└─ README.md               # 项目说明文档
```

### 快速开始

- 1、克隆项目

  - git clone <https://gitee.com/tao__tao/fastapi_jinja2.git>

- 2、安装依赖：

  - cd fastapi_jinja2
  - pip install -r requirements.txt

- 3、启动项目：

  - python3 main.py

- 4、访问项目：
  
  - 前端地址：<http://0.0.0.0:8000/)>
  - 账号：`admin` 密码：`123456`
  - 接口地址：<http://127.0.0.1:8000/docs>

### 特别鸣谢

感谢以下项目的贡献和支持，使本项目得以顺利完成：

- [FastAPI 项目](https://fastapi.tiangolo.com/)
- [Jinja2 项目](https://jinja.palletsprojects.com/en/stable/)
