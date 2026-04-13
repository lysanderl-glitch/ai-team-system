@echo off
REM Synapse 任务自动恢复 -- 本地定时执行
REM 触发时间：每天 6:00am Dubai (UTC+4)
REM 执行方式：claude -p 非交互模式，读取 prompt 文件执行

cd /d "C:\Users\lysanderl_janusd\Claude Code\ai-team-system"

REM 确保 logs 目录存在
if not exist "logs" mkdir logs

REM 记录开始时间
echo [%date% %time%] Task auto-resume started >> logs\scheduled-execution.log

REM 读取 prompt 文件并通过 claude -p 执行
REM --permission-mode auto: 自动批准安全操作
REM --model: 使用 sonnet 控制成本
REM --max-turns: 任务恢复逻辑简单，10轮足够
REM --allowedTools: 只需读写文件
claude -p --permission-mode auto --model claude-sonnet-4-6 --max-turns 10 --allowedTools "Read,Edit,Glob" < "agent-butler\config\task-auto-resume-prompt.md" >> logs\task-auto-resume.log 2>&1

REM 记录完成时间和退出码
echo [%date% %time%] Task auto-resume completed (exit code: %ERRORLEVEL%) >> logs\scheduled-execution.log
