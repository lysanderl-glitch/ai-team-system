@echo off
REM Synapse 定时任务注册脚本
REM 需要以管理员权限运行

cd /d "C:\Users\lysanderl_janusd\Claude Code\ai-team-system"

echo ========================================
echo  Synapse 情报管线定时任务注册
echo ========================================
echo.

REM 注册情报日报任务（每天 8:00am）
echo [1/2] 注册情报日报任务...
schtasks /create /tn "Synapse\DailyIntelligence" /xml "scripts\scheduled-tasks\daily-intelligence-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 08:00 执行情报日报
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

REM 注册情报行动任务（每天 10:00am）
echo [2/2] 注册情报行动任务...
schtasks /create /tn "Synapse\IntelligenceAction" /xml "scripts\scheduled-tasks\intelligence-action-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 10:00 执行情报行动
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

echo ========================================
echo  注册完成！
echo ========================================
echo.
echo 查看已注册任务：
schtasks /query /tn "Synapse\*" /fo TABLE
echo.
echo 手动触发测试：
echo   schtasks /run /tn "Synapse\DailyIntelligence"
echo   schtasks /run /tn "Synapse\IntelligenceAction"
echo.
pause
