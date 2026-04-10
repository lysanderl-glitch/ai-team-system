@echo off
chcp 65001 >nul
echo ==========================================
echo   Agent System 安装脚本 (Windows)
echo ==========================================
echo.

:: 步骤1: 检查基础依赖
echo 【步骤1/3】检查基础依赖...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装，请先安装 Python 3.8+
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i

git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Git 未安装，请先安装 Git
    echo   下载地址: https://git-scm.com/downloads
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('git --version') do echo [OK] %%i

claude --version >nul 2>&1
if errorlevel 1 (
    echo [警告] Claude Code 未安装
    echo   安装参考: https://docs.anthropic.com/en/docs/claude-code/setup
) else (
    echo [OK] Claude Code 已安装
)

echo.
echo 基础依赖检查完成
echo.

:: 步骤2: 安装Python依赖
echo 【步骤2/3】安装Python依赖...
echo.

set SCRIPT_DIR=%~dp0
pip install -r "%SCRIPT_DIR%..\agent-butler\requirements.txt" --quiet
if errorlevel 1 (
    echo [错误] Python依赖安装失败
    pause
    exit /b 1
)
echo [OK] Python依赖安装完成 (pyyaml, watchdog)
echo.

:: 步骤3: 验证安装
echo 【步骤3/3】验证安装...
echo.

cd /d "%SCRIPT_DIR%..\agent-butler"
python -c "from hr_base import load_org_config; c=load_org_config(); print('[OK] 团队加载成功:', list(c['teams'].keys()))"
if errorlevel 1 (
    echo [错误] hr_base 验证失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   安装完成！
echo ==========================================
echo.
echo 下一步：
echo   1. 用 Obsidian 打开 obs\ 文件夹（作为 Vault）
echo   2. 在 ai-team-system 目录启动 Claude Code: claude
echo   3. 查看帮助: type README.md
echo.
pause
