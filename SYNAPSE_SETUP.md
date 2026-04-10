# Synapse 快速开始

**三步完成，5分钟上手。**

---

## 第一步：下载到本地

打开 **PowerShell**（按 `Win + X` → 选择 Windows PowerShell），粘贴以下命令回车：

```powershell
Invoke-WebRequest -Uri 'https://github.com/lysanderl-glitch/ai-team-system/archive/refs/heads/main.zip' -OutFile "$env:USERPROFILE\Downloads\synapse.zip"
Expand-Archive -Path "$env:USERPROFILE\Downloads\synapse.zip" -DestinationPath "$env:USERPROFILE\Claude Code" -Force
Rename-Item -Path "$env:USERPROFILE\Claude Code\ai-team-system-main" -NewName 'ai-team-system' -ErrorAction SilentlyContinue
```

完成后，文件位于：`C:\Users\你的用户名\Claude Code\ai-team-system`

---

## 第二步：用 Claude Code 打开

1. 打开 **Claude Code**
2. 点击 **Open Folder**（打开文件夹）
3. 选择 `ai-team-system` 文件夹

---

## 第三步：发送任意消息开始使用

在 Claude Code 对话框发送任意内容，Lysander 会**自动以问候语开场**：

> 总裁您好，我是 Lysander，Multi-Agents 团队为您服务！

收到这句问候说明体系加载成功。之后直接说出你的目标即可。

> ⚠️ **如果第一条回复没有出现 Lysander 问候语**，说明 Claude Code 打开的目录不对，请确认打开的是 `ai-team-system` 根目录（里面能看到 `CLAUDE.md` 文件）。

---

## 可选：安装增强功能

> 核心功能无需此步骤。如需使用文章 HTML 生成等工具，额外执行：

```powershell
cd "$env:USERPROFILE\Documents\Synapse\ai-team-system"
pip install markdown pygments pyyaml
```

---

*Synapse — Janus Digital AI 协作运营体系*
