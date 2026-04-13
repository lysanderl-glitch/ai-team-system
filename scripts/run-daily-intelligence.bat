@echo off
REM Synapse 情报日报 -- 本地定时执行
REM 触发时间：每天 8:00am Dubai (UTC+4)
REM 执行方式：claude -p 非交互模式，读取 prompt 文件执行

cd /d "C:\Users\lysanderl_janusd\Claude Code\ai-team-system"

REM 确保 logs 目录存在
if not exist "logs" mkdir logs

REM 记录开始时间
echo [%date% %time%] Daily intelligence started >> logs\intelligence-execution.log

REM 读取 prompt 文件并通过 claude -p 执行
REM --permission-mode auto: 自动批准安全操作（用户需提前在 settings 中配置允许规则）
REM --model: 使用 sonnet 控制成本
REM --max-turns: 限制最大轮次防止无限循环
REM --allowedTools: 限制可用工具集
claude -p --permission-mode auto --model claude-sonnet-4-6 --max-turns 30 --allowedTools "Bash,Read,Write,Edit,Grep,Glob,WebSearch,WebFetch" < "agent-butler\config\daily-intelligence-prompt.md" >> logs\intelligence-daily.log 2>&1

REM 记录完成时间和退出码
echo [%date% %time%] Daily intelligence completed (exit code: %ERRORLEVEL%) >> logs\intelligence-execution.log
