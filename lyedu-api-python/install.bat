@echo off
REM LyEdu API Python - 使用国内镜像安装依赖
REM 在命令提示符中执行: install.bat

set MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple

echo 1. 创建虚拟环境 (python -m venv venv) ...
python -m venv venv
if errorlevel 1 (
    echo 若本机用 py 启动器，请改为: py -3 -m venv venv
    exit /b 1
)

echo 2. 安装依赖 (清华源) ...
call venv\Scripts\activate.bat
pip install -r requirements.txt -i %MIRROR%

echo 完成。激活环境: venv\Scripts\activate.bat  启动: uvicorn main:app --host 0.0.0.0 --port 9700
