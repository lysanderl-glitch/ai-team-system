---
title: 视频教程自动化生产 Pipeline — 项目知识沉淀
date: 2026-04-12
author: OBS 团队 - knowledge_engineer
tags: [视频制作, Pipeline, 自动化, HTML Cinema, 经验沉淀, Content Ops]
description: 团队首次视频内容制作的全流程经验，从战略分析到 MVP 成片，记录关键决策、技术架构和可复用模式
---

# 视频教程自动化生产 Pipeline — 项目知识沉淀

## 概述

**项目背景**：Synapse 体系需要面向用户的教程视频（首个目标：SPE 快速入门），但团队从未做过视频内容，也没有人可以录屏+配音。

**目标**：建立可复用的视频制作能力，而非仅完成一个视频。

**成果**：
- MVP 成片 2:41，1920x1080，H.264，约 6MB，全自动零人工
- 封装为 `video-gen.py` CLI + `/video-tutorial` Skill，后续任何教程视频可一键生成
- Content Ops 团队从 6 人扩编至 8 人（新增 video_scriptwriter + video_producer）

**项目时间线**：
1. 战略分析 — 确认可行性，AI 工具链可替代 65-70% 人工
2. 团队扩编 — HR 审批 video_scriptwriter + video_producer 入职
3. 分镜脚本创作 — 基于 ADDIE 教学设计模型，评审通过 4.1/5.0
4. 方案转向 — 从"人工录屏"转向"HTML Cinema Pipeline"
5. Pipeline 开发 — HTML 动画 + Playwright 录制 + Edge TTS 配音 + FFmpeg 合成
6. MVP 成片 — 全自动生成完成
7. 工具封装 — CLI + Skill 双层可复用基础设施

---

## 关键决策与经验教训

### 决策1：HTML Cinema Pipeline > 人工录屏

- **背景**：最初方案是 OBS Studio 录屏 + 剪映后期（见 `spe-video-production-guide.md`），但实际执行发现 AI Agent 团队无法操作 GUI 录屏软件，需要人类手动操作每一帧
- **决策**：将视频制作转化为代码问题 — HTML/CSS/JS 动画模拟终端界面，Playwright headless 浏览器自动录制，完全消除人工环节
- **效果**：100% 代码驱动，零人工操作，每次修改只需改 JSON 配置重新运行
- **经验**：**AI Agent 团队的"不公平优势"是把一切变成代码问题。** 当遇到需要人类手动操作的环节，先问"能不能用代码替代"，答案通常是"能"

### 决策2：MVP 先行验证

- **背景**：完整分镜脚本设计了 6 个场景、4 分钟内容，但首次尝试新技术栈风险高
- **决策**：先做一个包含核心场景的短片验证全流程（录制 + 配音 + 合成），确认工具链可行后再扩展
- **效果**：2:41 分钟 MVP 成片验证了 Pipeline 每个环节都能跑通
- **经验**：**新能力建设必须 MVP 先行。** 不要一步到位设计完美方案，先用最小成本验证"技术上能不能做到"，再考虑"做到什么程度"

### 决策3：免费工具起步

- **背景**：视频制作领域有大量付费工具（Synthesia、HeyGen、专业配音等），预算审批会拖慢验证速度
- **决策**：全链路使用免费工具 — Edge TTS（微软免费语音合成）、Playwright（开源浏览器自动化）、FFmpeg（开源音视频处理）
- **效果**：验证阶段零成本，配音质量已达可用水平
- **经验**：**AI 工具链发展快，免费方案已能达到 MVP 品质。** 验证阶段不要在工具选型上花时间，先用免费方案跑通，品质不够再升级

### 决策4：工具封装为可复用基础设施

- **背景**：MVP 验证成功后，面临选择 — 是把 Pipeline 当作一次性项目交付，还是封装为通用工具
- **决策**：投入额外工作量，将 Pipeline 封装为 `video-gen.py` CLI（开发者直接调用）+ `/video-tutorial` Skill（AI Agent 通过对话调用）双层架构
- **效果**：后续任何教程视频只需准备 `scenes.json` 配置即可一键生成，无需重新搭建环境
- **经验**：**每个新能力建设完成后，立即封装为可复用工具。** 封装的边际成本远低于下次从零开始的成本。双层架构（CLI + Skill）确保开发者和 Agent 都能使用

### 决策5：ADDIE 教学设计模型指导脚本创作

- **背景**：团队首次做教程内容，缺乏教学设计经验
- **决策**：引入 ADDIE 模型（Analysis-Design-Development-Implementation-Evaluation）指导分镜脚本创作，使用 PDCA 循环排列知识点
- **效果**：脚本评审 4.1/5.0，知识点按"捕获 -> 规划 -> 执行 -> 回顾"自然衔接
- **经验**：**内容制作不是"录个屏就行"，教学设计方法论显著提升内容质量。** ADDIE 模型适用于所有教程类内容

---

## 技术架构

### HTML Cinema Pipeline 流程

```
分镜脚本（人工/AI设计）
    ↓
scenes.json（标准化场景配置）
    ↓
HTML 模板注入（terminal-tutorial.html + scenes.json → 动态渲染）
    ↓
Playwright 录制（headless Chromium → WebM/视频流）
    ↓
Edge TTS 配音（narration 文本 → MP3 音频）
    ↓
FFmpeg 合成（视频 + 音频 → MP4）
    ↓
最终成片（1920x1080, H.264）
```

### 工具链

| 环节 | 工具 | 成本 | 说明 |
|------|------|------|------|
| 动画渲染 | HTML/CSS/JS + Playwright Chromium | 免费 | 纯代码驱动终端模拟动画 |
| AI 配音 | Edge TTS (`zh-CN-YunxiNeural`) | 免费 | 微软语音合成，中文男声 |
| 视频合成 | FFmpeg | 免费 | 跨平台音视频处理 |
| 脚本设计 | Claude AI + ADDIE 模型 | 已有 | 分镜脚本 + scenes.json 生成 |

### 关键文件索引

| 文件 | 用途 |
|------|------|
| `tools/video-pipeline/video-gen.py` | 统一 CLI 入口，编排全流程 |
| `tools/video-pipeline/generate-narration.py` | TTS 配音生成模块 |
| `tools/video-pipeline/templates/terminal-tutorial.html` | 通用 HTML 动画模板 |
| `tools/video-pipeline/examples/spe-tutorial.json` | SPE 教程的 scenes.json 配置（可做参考模板） |
| `tools/video-pipeline/compose.sh` | FFmpeg 合成脚本 |
| `tools/video-pipeline/build.sh` | 完整构建脚本 |
| `.claude/skills/video-tutorial/SKILL.md` | `/video-tutorial` Skill 定义 |
| `obs/03-process-knowledge/spe-video-script-mvp.md` | SPE 教程分镜脚本（ADDIE 模型范例） |
| `obs/03-process-knowledge/spe-video-production-guide.md` | 早期"人工录屏"方案（已被 Pipeline 取代，保留作对比参考） |

### scenes.json 核心结构

```json
{
  "title": "视频标题",
  "voice": "zh-CN-YunxiNeural",
  "voice_rate": "+10%",
  "resolution": [1920, 1080],
  "template": "terminal-tutorial.html",
  "scenes": [
    {
      "id": "scene_id",
      "type": "hook | terminal-demo | cta",
      "duration": 30,
      "narration": "旁白文本",
      "commands": [...],
      "sidebar": { "type": "info-card | flow-steps | pdca", ... }
    }
  ]
}
```

场景类型：`hook`（开场痛点共鸣）、`terminal-demo`（终端命令演示）、`cta`（行动号召结尾）。

---

## 质量指标

| 指标 | 值 |
|------|-----|
| 分镜脚本评审 | 4.1 / 5.0 |
| 成片分辨率 | 1920 x 1080 (Full HD) |
| 编码格式 | H.264 |
| 成片时长 | 2:41 |
| 文件大小 | ~6 MB |
| 自动化率 | 100%（零人工操作） |
| 人工干预点 | 0（从 scenes.json 到 MP4 全自动） |

---

## 适用场景

本 Pipeline 当前最适合以下类型的视频：

- **CLI/终端工具教程** — 天然适配，HTML 模板就是终端模拟器
- **系统功能演示** — 任何可以用命令行交互展示的功能
- **内部培训视频** — 标准化操作流程的视频化
- **产品快速入门** — Slash Command 类产品的上手指引

暂不适合：
- 需要真实 GUI 操作的演示（如 Figma 设计流程）
- 需要真人出镜的内容
- 纯概念性/非操作性的讲解视频

---

## 未来优化方向

### 短期可执行

| 优化项 | 方案 | 预期效果 |
|--------|------|----------|
| 配音质量提升 | 升级到 Fish Audio（~$10/月）或 Azure TTS 付费层 | 更自然的语调和停顿 |
| 动画节奏调优 | 调整 scenes.json 的 `duration`、`delay_before`、`delay_after` 参数 | 更舒适的观看节奏 |
| 多语言支持 | 切换 TTS 声音参数（如 `en-US-GuyNeural`） | 英文版教程 |

### 中期扩展

| 优化项 | 方案 | 预期效果 |
|--------|------|----------|
| 新场景类型 | 开发非终端类 HTML 模板（架构图演示、流程图动画、数据可视化） | 覆盖更多视频类型 |
| 背景音乐 | FFmpeg 合成时叠加低音量 BGM | 更专业的观感 |
| 字幕文件生成 | 从 narration 自动生成 SRT 字幕 | 支持字幕显示和翻译 |

---

## 方法论总结（可迁移到其他项目）

1. **代码化优先**：AI Agent 团队做任何新事情，第一个问题是"能不能代码化"
2. **MVP 验证 -> 工具封装**：先最小成本验证可行性，成功后立即封装为可复用工具
3. **免费起步 -> 按需升级**：验证阶段用免费工具，品质瓶颈出现时再投资
4. **教学设计指导内容**：内容类项目引入专业方法论（ADDIE/PDCA），不要"凭感觉做"
5. **方案转向不是失败**：从人工录屏转向 HTML Cinema Pipeline 不是"方案做错了"，是团队在执行中发现了更优路径。保留原方案文档作对比参考，本身就是知识
