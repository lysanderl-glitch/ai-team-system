---
name: video-tutorial
description: |
  视频教程生成 Pipeline。从源文档自动生成分镜脚本、scenes.json 配置，
  并调用 video-gen.py 完成录制+配音+合成的全流程视频制作。
  Use when creating video tutorials from documentation, guides, or feature demos.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "<topic> --source <path/to/doc.html>"
---

# /video-tutorial — 视频教程自动生成

你是 RD 团队的 ai_systems_dev 和 Content_ops 团队的 content_strategist，
现在协作执行视频教程生成任务。

## 输入解析

从 `$ARGUMENTS` 中提取：
- **topic**: 视频主题（第一个参数）
- **--source PATH**: 源文档路径（HTML/MD 格式）
- **--voice NAME**: TTS 声音覆盖（可选）
- **--rate RATE**: 语速覆盖（可选）
- **--output PATH**: 输出路径覆盖（可选）

如果没有提供 --source，询问用户提供源文档路径。

## Step 1: 读取源文档

```!
cat <source_path>
```

读取源文档，理解其内容结构、核心概念、功能演示。

## Step 2: 读取示例配置了解格式

```!
cat tools/video-pipeline/examples/spe-tutorial.json
```

了解 scenes.json 的标准格式和场景类型。

## Step 3: 生成分镜脚本

基于源文档内容，设计分镜脚本。遵循以下原则：

### 教学设计原则

**Hook-Problem-Solution 结构**：
1. **Hook (0-30s)**: 共鸣痛点，激发兴趣
   - 用 `hook` 场景类型
   - chaos_items: 列出目标用户的典型困扰（6-10 个）
   - 标题简洁有力，突出核心价值

2. **Problem → Solution (30s - 结尾前30s)**: PDCA 知识排序
   - 每个功能/命令用 `terminal-demo` 场景
   - 先展示问题，再演示解决方案
   - 每个命令配 sidebar 说明卡片
   - 按使用顺序排列（而非重要性排列）

3. **CTA (最后30s)**: 行动号召
   - 用 `cta` 场景类型
   - 回顾整体架构
   - 给出明确的第一步行动指令

### 分镜质量标准

- **总时长**: 3-5 分钟（180-300 秒），每个 terminal-demo 场景 20-40 秒
- **旁白文字**: 口语化，短句为主，每句不超过 30 个字
- **终端命令**: 真实可执行的命令，输出使用 HTML color classes
- **Sidebar**: 每个 terminal-demo 至少一个 sidebar 卡片
- **字幕**: 与旁白同步但可以更简短
- **进度指示**: 主要功能节点设置 `progress_label`

### 终端演示最佳实践

1. **命令输入**: 使用真实的 CLI 命令，让观众感受到可操作性
2. **输出设计**: 使用以下 color classes 高亮关键信息：
   - `highlight-green` + `flash-green`: 成功状态
   - `highlight-cyan` + `bold`: 重点数据
   - `highlight-yellow`: 警告/注意
   - `highlight-red`: 错误/问题
   - `highlight-blue`: 信息/链接
   - `highlight-purple`: 特殊标记
   - `dim`: 次要信息（ID、时间戳等）
   - `output-line`: 普通输出
3. **节奏控制**: 
   - `delay_before`: 命令前的停顿（让观众准备好）
   - `delay_after`: 输出后的停留（让观众消化）
   - `clear_before: true`: 新功能开始时清屏

### Sidebar 类型选择指南

| 场景内容 | 推荐 sidebar type | 说明 |
|----------|-------------------|------|
| 功能介绍 | `info-card` | 用 HTML 列出功能要点 |
| 流程步骤 | `flow-steps` | 带编号和动画的步骤列表 |
| 颜色/标签说明 | `color-legend` | 带色块的图例 |
| 闭环/循环概念 | `pdca` | PDCA 环形图 |
| 架构层次 | `info-card` | 用分层 div 展示 |

## Step 4: 生成 scenes.json

将分镜脚本转化为符合 schema 的 JSON 配置文件。

默认参数：
- `voice`: "zh-CN-YunxiNeural"（男声，专业）
- `voice_rate`: "+10%"
- `resolution`: [1920, 1080]
- `template`: "terminal-tutorial.html"
- `brand.accent_color`: "#14b8a6"
- `brand.company`: "Janus Digital"
- `brand.copyright_year`: "2026"

将生成的配置写入 `tools/video-pipeline/examples/<topic-slug>.json`。

```!
# 验证 JSON 格式有效
python -c "import json; json.load(open('tools/video-pipeline/examples/<topic-slug>.json', encoding='utf-8')); print('JSON valid')"
```

## Step 5: 生成视频

调用统一 CLI 入口：

```!
cd tools/video-pipeline && python video-gen.py --config examples/<topic-slug>.json
```

如果用户指定了 --voice 或 --rate 或 --output，附加对应参数。

如果生成失败：
1. 检查错误信息
2. 常见问题：FFmpeg 未安装、Playwright 浏览器未安装、edge-tts 网络超时
3. 修复后重试

## Step 6: 报告结果

输出生成结果：

```
视频教程生成完成！

主题：<topic>
场景数：<N> 个
总时长：约 <M> 分钟

输出文件：
  配置文件：tools/video-pipeline/examples/<topic-slug>.json
  最终视频：tools/video-pipeline/output/<filename>.mp4

如需调整：
  修改旁白 → 编辑 scenes.json 的 narration 字段 → 重新运行 --skip-record
  修改动画 → 编辑 scenes.json 的 commands 字段 → 重新运行 --skip-narration
  修改声音 → 重新运行加 --voice zh-CN-XiaoyiNeural
```

---

## 注意事项

- scenes.json 中的 HTML 输出（output 数组中的字符串）使用模板内置的 CSS classes
- narration 文本使用中文口语风格，自然断句
- 每个 scene 的 id 必须唯一且使用 snake_case
- chaos_items 数量建议 6-10 个，文本简短（10 字以内）
- hook_cards 对应产品的核心命令/功能（3-5 个）
- arch_layers 在 CTA 场景中展示完整架构，与 hook_cards 对应
