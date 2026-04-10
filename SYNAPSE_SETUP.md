# Synapse 快速开始

**三步完成，5分钟上手。**

---

## 第一步：下载到本地

打开 Windows **命令提示符**或 **PowerShell**，粘贴以下命令回车：

```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/lysanderl-glitch/ai-team-system/archive/refs/heads/main.zip' -OutFile \"$env:USERPROFILE\Downloads\synapse.zip\"; Expand-Archive \"$env:USERPROFILE\Downloads\synapse.zip\" -DestinationPath \"$env:USERPROFILE\Documents\Synapse\" -Force; Rename-Item \"$env:USERPROFILE\Documents\Synapse\ai-team-system-main\" 'ai-team-system' -ErrorAction SilentlyContinue"
```

完成后，文件位于：`C:\Users\你的用户名\Documents\Synapse\ai-team-system`

> **不想用命令行？** 直接浏览器访问 https://github.com/lysanderl-glitch/ai-team-system → 点绿色 **Code** → **Download ZIP** → 解压到任意位置即可。

---

## 第二步：用 Claude Code 打开

1. 打开 **Claude Code**
2. 点击 **Open Folder**（打开文件夹）
3. 选择 `ai-team-system` 文件夹

---

## 第三步：发送引导词

将以下内容复制粘贴到对话框发送：

```
你好，请以 Lysander 身份问候我，并介绍当前 Synapse 团队。
```

Lysander 会回复问候并列出所有可用团队，体系立即生效。

---

## 可选：安装增强功能

> 核心功能无需此步骤。如需使用文章 HTML 生成等工具，额外执行：

```powershell
cd "$env:USERPROFILE\Documents\Synapse\ai-team-system"
pip install markdown pygments pyyaml
```

---

*Synapse — Janus Digital AI 协作运营体系*
