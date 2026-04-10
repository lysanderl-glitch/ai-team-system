---
title: 凭证管理说明
category: 流程知识
tags: [凭证, 安全, Meld Encrypt]
created: 2026-04-10
author: Lysander
type: 说明文档
---

# 凭证管理说明

## 存储位置

凭证文件：`obs/credentials.mdenc`（Meld Encrypt 加密，已加入 .gitignore）

## 日常使用

在 Obsidian 中打开 `credentials.mdenc`，右上角三个点 → **Encrypt note** 解密 → 输入密码 → 正常查看/编辑 → 保存后自动重新加密。

## AI 调用方式

```bash
# 查看所有 Key 名（无需密码）
PYTHONUTF8=1 python creds.py list

# 获取单个凭证
PYTHONUTF8=1 python creds.py get GITHUB_TOKEN -p "密码"

# 导出全部凭证（JSON）
PYTHONUTF8=1 python creds.py export -p "密码"
```

## 凭证内容格式（解密后 JSON）

```json
{
  "GITHUB_TOKEN": "ghp_xxx",
  "NOTION_TOKEN": "ntn_xxx",
  "OPENAI_API_KEY": "sk-xxx"
}
```

## 安全规则

1. 密码只在当次命令中使用，不存储不记录
2. `credentials.mdenc` 已在 `.gitignore`，不会上传 GitHub
3. 每次 AI 需要凭证时，先用 `list` 确认 Key 名，再向总裁请求密码
