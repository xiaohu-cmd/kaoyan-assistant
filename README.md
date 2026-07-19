# 考研助手 (Kaoyan Assistant)

个人考研备考管理平台 — 一站式的考研学习管理工具，支持学习计划、番茄钟计时、英语单词与阅读训练、院校信息查询等功能。

## 技术栈

- **后端**: Python 3.10+ / FastAPI / SQLite
- **前端**: Vanilla JS (SPA) / Chart.js

## 快速开始

### Windows

双击 `start.bat` 启动应用，浏览器将自动打开 `http://localhost:8000`。

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p data uploads
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

然后打开浏览器访问 `http://localhost:8000`。

## 使用说明

1. 打开应用后，在登录界面注册一个新账号
2. 登录后，进入「设置」页面配置目标院校和考试日期
3. 使用以下功能模块：
   - **仪表盘**: 查看学习进度概览、倒计时、热力图
   - **学习计划**: 管理学习任务，按阶段（基础/强化/冲刺）组织
   - **英语学习**: 单词记忆（含5500词库）、阅读理解训练、写作练习
   - **学习资源**: 资料管理、笔记与错题本、闪卡复习
   - **院校信息**: 查询和收藏目标院校招生信息

## 数据存储

所有数据存储在 `data/kaoyan.db` SQLite 数据库中。可通过「设置」页面的「导出数据」功能备份数据。

## 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/ -v

# 启动开发服务器
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
