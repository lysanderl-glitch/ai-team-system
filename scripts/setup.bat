@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║       Synapse 体系安装脚本 (Windows)             ║
echo ╚══════════════════════════════════════════════════╝
echo.

set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..

:: ── STEP 1：检查基础依赖 ──────────────────────────────
echo [1/3] 检查基础依赖...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [❌] Python 未安装
    echo     请下载安装：https://www.python.org/downloads/
    echo     安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [✅] %%i

git --version >nul 2>&1
if errorlevel 1 (
    echo [⚠️ ] Git 未安装（可选，用于自动更新）
    echo     下载地址：https://git-scm.com/downloads
) else (
    for /f "tokens=*" %%i in ('git --version') do echo [✅] %%i
)

echo.

:: ── STEP 2：安装 Python 依赖 ──────────────────────────
echo [2/3] 安装 Python 依赖...
echo.

pip install -r "%ROOT_DIR%\agent-butler\requirements.txt" --quiet
if errorlevel 1 (
    echo [❌] Python 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo [✅] 依赖安装完成 (pyyaml, watchdog, markdown, pygments)
echo.

:: ── STEP 3：验证安装 ──────────────────────────────────
echo [3/3] 验证安装...
echo.

cd /d "%ROOT_DIR%\agent-butler"
python -c "from hr_base import load_org_config; c=load_org_config(); teams=list(c['teams'].keys()); print(f'[✅] HR知识库加载成功，团队数：{len(teams)}'); print(f'     团队：{teams}')"
if errorlevel 1 (
    echo [❌] HR知识库验证失败
    pause
    exit /b 1
)

cd /d "%ROOT_DIR%"
python scripts\generate-article.py obs\03-process-knowledge\daily-workflow-sop.md >nul 2>&1
if errorlevel 1 (
    echo [⚠️ ] 文章生成脚本异常（不影响核心功能）
) else (
    echo [✅] 文章生成脚本正常
)

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║            Synapse 安装完成！                    ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo 下一步：
echo.
echo   1. 打开 Obsidian → Open folder as vault
echo      选择：%ROOT_DIR%\obs
echo.
echo   2. 打开 Claude Code → Open Folder
echo      选择：%ROOT_DIR%
echo.
echo   3. 在 Claude Code 中发送：
echo      "你好，请以 Lysander 身份问候我，并介绍 Synapse 团队。"
echo.
echo   详细指南见：COLLEAGUE_GUIDE.md
echo   首次引导词见：FIRST_PROMPT.md
echo.
pause
