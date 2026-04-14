@echo off
REM Synapse 定时任务注册脚本
REM 需要以管理员权限运行

cd /d "C:\Users\lysanderl_janusd\Claude Code\ai-team-system"

echo ========================================
echo  Synapse 全部定时任务注册 (6个Agent)
echo ========================================
echo.

REM 注册任务自动恢复（每天 6:00am）
echo [1/6] 注册任务自动恢复...
schtasks /create /tn "Synapse\TaskAutoResume" /xml "scripts\scheduled-tasks\task-auto-resume-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 06:00 执行任务自动恢复
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

REM 注册日历同步任务（每天 6:15am）
echo [2/6] 注册SPE日历同步...
schtasks /create /tn "Synapse\CalendarSync" /xml "scripts\scheduled-tasks\calendar-sync-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 06:15 执行日历同步
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

REM 注册情报日报任务（每天 8:00am）
echo [3/6] 注册情报日报...
schtasks /create /tn "Synapse\DailyIntelligence" /xml "scripts\scheduled-tasks\daily-intelligence-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 08:00 执行情报日报
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

REM 注册情报行动任务（每天 10:00am）
echo [4/6] 注册情报行动...
schtasks /create /tn "Synapse\IntelligenceAction" /xml "scripts\scheduled-tasks\intelligence-action-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 10:00 执行情报行动
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

REM 注册日终复盘任务（每天 20:00）
echo [5/6] 注册SPE日终复盘...
schtasks /create /tn "Synapse\DailyReview" /xml "scripts\scheduled-tasks\daily-review-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 20:00 执行日终复盘
) else (
    echo       失败！请确认以管理员权限运行
)
echo.

REM 注册每日复盘+博客生成任务（每天 21:43）
echo [6/6] 注册每日复盘+博客生成...
schtasks /create /tn "Synapse\DailyRetroBlog" /xml "scripts\scheduled-tasks\daily-retro-blog-task.xml" /f
if %ERRORLEVEL% EQU 0 (
    echo       成功！每天 21:43 执行复盘+博客生成
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
echo   schtasks /run /tn "Synapse\TaskAutoResume"
echo   schtasks /run /tn "Synapse\CalendarSync"
echo   schtasks /run /tn "Synapse\DailyIntelligence"
echo   schtasks /run /tn "Synapse\IntelligenceAction"
echo   schtasks /run /tn "Synapse\DailyReview"
echo   schtasks /run /tn "Synapse\DailyRetroBlog"
echo.
pause
