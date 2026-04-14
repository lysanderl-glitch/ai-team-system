@echo off
REM Synapse 每日复盘+博客生成 -- 本地定时执行
REM 触发时间：每天 21:43 Dubai (UTC+4)
REM 执行方式：claude -p 非交互模式，读取 prompt 文件执行

cd /d "C:\Users\lysanderl_janusd\Claude Code\ai-team-system"

REM 确保 logs 目录存在
if not exist "logs" mkdir logs

REM 记录开始时间
echo [%date% %time%] Daily retro+blog started >> logs\scheduled-execution.log

REM 读取 prompt 文件并通过 claude -p 执行
REM --permission-mode auto: 自动批准安全操作
REM --model: 使用 sonnet 控制成本
REM --max-turns: 管线较长（复盘+博客+HTML+git），30轮足够
REM --allowedTools: 需要读写文件 + Bash(git log/git commit/python)
claude -p --permission-mode auto --model claude-sonnet-4-6 --max-turns 30 --allowedTools "Bash,Read,Write,Edit,Grep,Glob" < "agent-butler\config\daily-retro-blog-prompt.md" >> logs\retro-blog.log 2>&1

REM 记录完成时间和退出码
echo [%date% %time%] Daily retro+blog completed (exit code: %ERRORLEVEL%) >> logs\scheduled-execution.log
