# SPE 快速入门视频 — 制作执行方案（Production SOP）

> **执行者**：Content Ops 团队 - video_producer / ai_visual_creator
> **对应分镜脚本**：`obs/03-process-knowledge/spe-video-script-mvp.md`
> **视频时长**：约 4 分钟
> **形式**：屏幕录制 + AI 旁白（剪映 TTS）
> **工具栈**：OBS Studio + 剪映桌面版（全免费）

---

## Part 1：制作前准备清单

### 1.1 工具安装与配置

#### OBS Studio 安装

1. 打开浏览器，访问 https://obsproject.com/download
2. 点击 **Windows** 下载按钮，下载安装程序
3. 运行安装程序，全部选默认选项，点"下一步"直到安装完成
4. 首次启动 OBS 时，弹出"自动配置向导"，选择 **"我只使用录制功能"**，点击"下一步"完成向导

**OBS 录制设置（必须手动配置）**：

打开 OBS → 菜单栏 → 文件 → 设置，按以下逐项配置：

**视频 选项卡**：
| 设置项 | 值 | 说明 |
|--------|------|------|
| 基础（画布）分辨率 | 1920x1080 | 录制画面大小 |
| 输出（缩放）分辨率 | 1920x1080 | 保持与画布一致，不缩放 |
| 常用帧率值 | 30 | 教程视频 30fps 足够，文件更小 |

**输出 选项卡**（选择"高级"模式）：
| 设置项 | 值 | 说明 |
|--------|------|------|
| 录制格式 | MKV | 录制时用 MKV 防崩溃丢失，后续转 MP4 |
| 编码器 | 如有 NVIDIA 显卡选 `NVENC H.264`；否则选 `x264` | 硬件编码更快 |
| 码率控制 | CRF | 恒定质量模式 |
| CRF 值 | 18 | 数字越小画质越高，18 是高画质平衡点 |
| 关键帧间隔 | 2 | 秒 |

**音频 选项卡**：
| 设置项 | 值 | 说明 |
|--------|------|------|
| 采样率 | 44.1 kHz | 标准 |
| 声道 | 立体声 | 标准 |

> **重要**：我们的视频不录制麦克风音频（旁白后期用 TTS 合成），但 OBS 默认会录制桌面音频。进入 OBS 主界面底部的"音频混合器"区域，将"桌面音频"和"麦克风"全部**点击喇叭图标静音**，确保录制素材无杂音。

**设置录制热键**：

打开 OBS → 文件 → 设置 → 快捷键 选项卡：

| 操作 | 快捷键 |
|------|--------|
| 开始录制 | `Alt + F9`（OBS默认） |
| 停止录制 | `Alt + F9`（同一个键切换） |

点击"应用"→"确定"。

**添加录制源**：

回到 OBS 主界面：
1. 在底部"来源"面板，点击 **+** 号
2. 选择 **"显示器采集"**
3. 弹出窗口中命名为 `SPE-Screen`，点击"确定"
4. 在属性窗口中，选择你的主显示器，点击"确定"
5. 预览画面应该显示你的整个桌面

#### 剪映桌面版安装

1. 打开浏览器，访问 https://www.capcut.cn/ （中国大陆）或 https://www.capcut.com/ （海外）
2. 点击"免费下载"，下载桌面版安装包
3. 运行安装程序，按默认选项安装
4. 首次启动后，用手机号或邮箱注册/登录（免费账户即可）
5. 进入主界面后不需要做额外设置，后续在剪辑时配置项目参数

#### 终端环境准备

确保以下已安装：

1. **Windows Terminal**：Windows 11 自带。如果没有，打开 Microsoft Store 搜索 "Windows Terminal" 安装
2. **JetBrains Mono 字体**：
   - 访问 https://www.jetbrains.com/mono/
   - 点击 "Download" 下载 zip 文件
   - 解压后，全选所有 `.ttf` 文件 → 右键 → "为所有用户安装"
3. **Starship prompt**（可选但推荐）：
   - 打开 PowerShell（管理员），执行：
   ```powershell
   winget install --id Starship.Starship
   ```
   - 安装完成后，需要配置 PowerShell profile（见下方 1.2 节）

---

### 1.2 终端美化方案

#### Windows Terminal 配置

1. 打开 Windows Terminal
2. 按 `Ctrl + ,` 打开设置
3. 点击左下角 **"打开 JSON 文件"**（齿轮图标旁边）
4. 这会用文本编辑器打开 `settings.json`
5. **完整替换** `profiles` → `defaults` 部分（如果没有就新增），以及添加 `schemes`：

找到 `"profiles"` 下的 `"defaults": {}` 部分，替换为：

```json
"defaults": {
    "font": {
        "face": "JetBrains Mono",
        "size": 18,
        "weight": "normal"
    },
    "cursorShape": "filledBox",
    "cursorColor": "#14b8a6",
    "colorScheme": "SPE Dark",
    "opacity": 100,
    "useAcrylic": false,
    "padding": "16, 16, 16, 16",
    "scrollbarState": "hidden",
    "antialiasingMode": "cleartype"
}
```

在 `settings.json` 的根级别（与 `"profiles"` 同级），找到 `"schemes": [...]` 数组（如果没有就创建），添加以下配色方案：

```json
"schemes": [
    {
        "name": "SPE Dark",
        "background": "#0f172a",
        "foreground": "#e2e8f0",
        "cursorColor": "#14b8a6",
        "selectionBackground": "#334155",
        "black": "#1e293b",
        "brightBlack": "#475569",
        "red": "#ef4444",
        "brightRed": "#f87171",
        "green": "#22c55e",
        "brightGreen": "#4ade80",
        "yellow": "#eab308",
        "brightYellow": "#facc15",
        "blue": "#0ea5e9",
        "brightBlue": "#38bdf8",
        "purple": "#a855f7",
        "brightPurple": "#c084fc",
        "cyan": "#14b8a6",
        "brightCyan": "#2dd4bf",
        "white": "#e2e8f0",
        "brightWhite": "#f8fafc"
    }
]
```

> **配色说明**：背景色 `#0f172a` 是分镜脚本指定的深色，与 SPE 使用手册一致。青色 `#14b8a6` 是 SPE 品牌辅色，用于光标和高亮。蓝色 `#0ea5e9` 是 SPE 品牌主色。

6. 保存文件，关闭 Windows Terminal 再重新打开，配色立即生效

#### Starship Prompt 配置

Starship 可以让终端 prompt 更简洁美观。配置步骤：

**第一步：让 PowerShell 加载 Starship**

1. 打开 PowerShell
2. 执行以下命令打开 profile 文件：
   ```powershell
   notepad $PROFILE
   ```
3. 如果提示文件不存在，选择"是"创建新文件
4. 在文件中粘贴以下全部内容（如果已有内容，追加到末尾）：
   ```powershell
   # 启动 Starship prompt
   Invoke-Expression (&starship init powershell)

   # 清除默认的 PowerShell 启动消息
   Clear-Host
   ```
5. 保存并关闭

**第二步：创建 Starship 配置文件**

1. 打开文件资源管理器，导航到 `C:\Users\你的用户名\.config\`
   - 如果 `.config` 文件夹不存在，手动创建它
2. 在 `.config` 文件夹内新建文件 `starship.toml`
3. 用文本编辑器打开 `starship.toml`，粘贴以下全部内容：

```toml
# SPE Video Recording — Minimal Prompt
# 目标：录制视频时保持 prompt 干净简洁

# 总体格式：单行 prompt
format = """$character"""

# 光标符号
[character]
success_symbol = "[>](bold cyan)"
error_symbol = "[>](bold red)"

# 禁用所有不需要的模块
[aws]
disabled = true

[azure]
disabled = true

[gcloud]
disabled = true

[kubernetes]
disabled = true

[docker_context]
disabled = true

[git_branch]
disabled = true

[git_status]
disabled = true

[nodejs]
disabled = true

[python]
disabled = true

[rust]
disabled = true

[package]
disabled = true

[directory]
disabled = true

[cmd_duration]
disabled = true

[time]
disabled = true

[username]
disabled = true

[hostname]
disabled = true

[line_break]
disabled = true
```

4. 保存文件
5. 关闭并重新打开 Windows Terminal

> **效果**：终端现在只显示一个青色的 `>` 作为 prompt，极其干净，适合视频录制。录制完成后，如果想恢复日常 prompt，将 `starship.toml` 重命名为 `starship.toml.bak`，再新建一个默认的 `starship.toml` 即可。

#### 终端窗口尺寸

录制时终端需要占屏幕左侧约 70%（右侧 30% 留给后期叠加信息图）：

1. 打开 Windows Terminal
2. 将窗口拖到屏幕左侧
3. 手动调整窗口大小为约 **1344 x 1080 像素**（即 1920 的 70%）
4. 验证方法：打开 OBS 预览，确认终端占据画面左侧约 70%，右侧留有空间

> **精确方法**：在 OBS 中可以添加一条临时参考线。右键"来源" → 添加"颜色源" → 设置为半透明红色 → 大小设为 576x1080 → 拖到画面右侧。录制前删除这个参考源。

#### 桌面环境

1. 右键桌面 → 个性化 → 背景 → 选择 **纯色** → 颜色选择 **纯黑色**（`#000000`）
2. 右键桌面 → 个性化 → 颜色 → 选择 **深色** 模式
3. 右键任务栏 → 任务栏设置 → 打开 **"自动隐藏任务栏"**
4. 隐藏所有桌面图标：右键桌面 → 查看 → 取消勾选 **"显示桌面图标"**

---

### 1.3 录制环境准备

#### 系统准备

1. **开启勿扰模式**：
   - 点击任务栏右下角时间区域 → 点击"专注"或"勿扰" → 开启
   - 或者：设置 → 系统 → 通知 → 打开"勿扰"
2. **关闭所有无关程序**：只保留 Windows Terminal 和 OBS
3. **断开不必要的外设**：避免 USB 弹窗
4. **确保电量充足或连接电源**

#### 预制终端输出数据

视频中所有命令输出都是**预制文本**，不依赖真实 API。需要提前准备好模拟脚本。

**创建预制脚本目录**：

打开 PowerShell，执行：
```powershell
mkdir C:\spe-video-assets
mkdir C:\spe-video-assets\scripts
```

**场景 2 预制脚本**（`/capture` 演示）：

在 `C:\spe-video-assets\scripts\` 下新建文件 `scene2_capture.ps1`，内容如下：

```powershell
# Scene 2a: /capture 基本用法
Write-Host ""
Write-Host "  " -NoNewline
Write-Host "已捕获到收件箱" -ForegroundColor Green -NoNewline
Write-Host "：「给王总回邮件确认合同细节」"
Write-Host "  ID: CAP-2026-0412-001 | 来源: claude_cli" -ForegroundColor DarkGray
Write-Host ""
```

在 `C:\spe-video-assets\scripts\` 下新建文件 `scene2_capture_auto.ps1`：

```powershell
# Scene 2b: /capture auto
Write-Host ""
Write-Host "  扫描当前对话，提取行动项..." -ForegroundColor Cyan
Start-Sleep -Milliseconds 800
Write-Host ""
Write-Host "  发现 2 条新行动项：" -ForegroundColor White
Write-Host "    1.「更新投标文件中的报价表」 → " -NoNewline
Write-Host "已捕获" -ForegroundColor Green
Write-Host "    2.「确认供应商交货时间」 → " -NoNewline
Write-Host "已捕获" -ForegroundColor Green
Write-Host ""
Write-Host "  收件箱当前共 5 条待处理项" -ForegroundColor Yellow
Write-Host ""
```

**场景 3 预制脚本**（`/plan-day` 演示）：

新建 `scene3_planday.ps1`：

```powershell
# Scene 3: /plan-day
$separator = [string]::new([char]0x2501, 35)

Write-Host ""
Write-Host "  $separator" -ForegroundColor DarkCyan
Write-Host "    2026-04-12（周日）日程概览" -ForegroundColor Cyan
Write-Host "  $separator" -ForegroundColor DarkCyan
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  今日日程（Google Calendar）" -ForegroundColor White
Write-Host "    09:00-10:00  团队周会" -ForegroundColor Gray
Write-Host "    14:00-15:00  客户演示会议" -ForegroundColor Gray
Write-Host "    16:00-16:30  1:1 with 技术负责人" -ForegroundColor Gray
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  建议时间块" -ForegroundColor White
Write-Host "    10:00-12:00  深度工作 - 审阅 Janus 项目方案" -ForegroundColor DarkYellow
Write-Host "    15:00-16:00  处理收件箱 + 决策队列" -ForegroundColor DarkYellow
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  Big Rocks（今日最重要的事）" -ForegroundColor White
Write-Host "    1. 审阅 Janus 项目交付方案" -ForegroundColor Cyan -NoNewline
Write-Host " [来源: active_tasks]" -ForegroundColor DarkGray
Write-Host "    2. 确认竞品分析报告" -ForegroundColor Cyan -NoNewline
Write-Host " [来源: inbox]" -ForegroundColor DarkGray
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  收件箱分流（4 条待处理）" -ForegroundColor White
Write-Host "    -> 决策:「n8n OAuth 迁移方案选择」" -ForegroundColor Magenta
Write-Host "    -> 委派:「更新官网价格页面」-> 建议派单 Growth 团队" -ForegroundColor Blue
Write-Host "    -> 个人:「给王总回邮件」" -ForegroundColor Cyan
Write-Host "    -> 参考:「竞品定价策略研究」-> 归档到 OBS" -ForegroundColor DarkGray
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  OKR 进度提醒" -ForegroundColor White
Write-Host "    「每周发布1篇博客」- 本周尚未发布，" -NoNewline
Write-Host "进度落后" -ForegroundColor Red
Write-Host ""
```

**场景 4 预制脚本**（`/time-block` 演示）：

新建 `scene4_timeblock.ps1`：

```powershell
# Scene 4a: /time-block 常规用法
Write-Host ""
Write-Host "  已创建时间块：" -ForegroundColor Green
Write-Host "    审阅Janus方案" -ForegroundColor White
Write-Host "    2026-04-13 10:00-12:00" -NoNewline -ForegroundColor Gray
Write-Host "（自动匹配高精力时段）" -ForegroundColor Yellow
Write-Host "    Banana（黄色）- 常规任务" -ForegroundColor DarkYellow
Write-Host "    提醒：提前 10 分钟" -ForegroundColor Gray
Write-Host ""
```

新建 `scene4_timeblock_focus.ps1`：

```powershell
# Scene 4b: /time-block focus 模式
Write-Host ""
Write-Host "  已创建深度工作块：" -ForegroundColor Green
Write-Host "    深度工作 - Focus Time" -ForegroundColor White
Write-Host "    2026-04-12 10:00-12:00" -NoNewline -ForegroundColor Gray
Write-Host "（高精力时段）" -ForegroundColor Yellow
Write-Host "    Peacock（青色）- 深度工作" -ForegroundColor Cyan
Write-Host "    提醒：提前 10 分钟" -ForegroundColor Gray
Write-Host ""
```

**场景 5 预制脚本**（`/weekly-review` 演示）：

新建 `scene5_weeklyreview.ps1`：

```powershell
# Scene 5: /weekly-review
$separator = [string]::new([char]0x2501, 35)

Write-Host ""
Write-Host "  $separator" -ForegroundColor DarkCyan
Write-Host "    2026-W16 每周回顾报告" -ForegroundColor Cyan
Write-Host "  $separator" -ForegroundColor DarkCyan
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  本周成就" -ForegroundColor White
Write-Host "    完成 SPE Phase 1-4 全部开发并交付" -ForegroundColor Green
Write-Host "    情报日报系统上线运行" -ForegroundColor Green
Write-Host "    3 个远程定时 Agent 配置完成" -ForegroundColor Green
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  OKR 进度 (2026-Q2)" -ForegroundColor White
Write-Host "    「每周发布1篇博客」- 本周已完成" -ForegroundColor Green
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  决策回顾" -ForegroundColor White
Write-Host "    本周新增决策: 2 项" -ForegroundColor Gray
Write-Host "    D-2026-0412-001: SPE 体系方案选型" -ForegroundColor Gray -NoNewline
Write-Host " [已决策]" -ForegroundColor Green
Write-Host "    D-2026-0412-002: SessionEnd Hook 方案" -ForegroundColor Gray -NoNewline
Write-Host " [已决策]" -ForegroundColor Green
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  时间分配" -ForegroundColor White
Write-Host "    深度工作: 12h (35%)  |  会议: 6h (18%)" -ForegroundColor Cyan
Write-Host "    常规任务: 10h (29%)  |  学习: 4h (12%)" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Milliseconds 300

Write-Host "  下周焦点建议" -ForegroundColor White
Write-Host "    1. 设定 Q2 个人 OKR" -ForegroundColor Yellow
Write-Host "    2. 验证 SPE 自动化 Agent 稳定性" -ForegroundColor Yellow
Write-Host ""
```

#### 录制前检查清单（每次录制前过一遍）

- [ ] OBS 已打开，预览画面正确显示桌面
- [ ] 音频全部静音（桌面音频 + 麦克风均已静音）
- [ ] Windows Terminal 已打开，使用 SPE Dark 配色
- [ ] Starship prompt 显示为单个青色 `>`
- [ ] 终端字体确认为 JetBrains Mono 18pt
- [ ] 终端窗口位于屏幕左侧，约占 70% 宽度
- [ ] 桌面纯黑背景，无图标
- [ ] 任务栏已自动隐藏
- [ ] 勿扰模式已开启
- [ ] 所有无关程序已关闭
- [ ] 预制脚本已准备好（`C:\spe-video-assets\scripts\` 下 6 个 .ps1 文件）
- [ ] 磁盘空间充足（预计录制素材约 2-3 GB）

---

## Part 2：逐场景录制指南

> **总体原则**：每个场景单独录制为一个素材片段，后期在剪映中组装。这样出错时只需重录单个场景。

### 场景 1：Hook（00:00 - 00:30）

**此场景无需终端录制**。Hook 画面全部在后期制作：
- 杂乱待办列表的画面 → 用 Canva 制作静态图 + 剪映添加抖动特效
- "碎裂"过渡 → 剪映内置转场效果
- 干净终端界面 → 场景 2 的开头画面

**需要准备的素材**：
1. 便签/Slack/日历混乱叠加的静态图片（在 Part 5 的信息图部分制作）
2. 干净终端的截图（录制场景 2 时顺带截取）

**录制操作**：无。此场景完全由后期合成。

---

### 场景 2：/capture 演示（00:30 - 01:15）

#### 录制前准备

1. 打开 Windows Terminal，确保使用 SPE Dark 配色
2. 清屏：在终端输入 `Clear-Host` 并回车
3. 确保当前目录不会显示在 prompt 中（如果用了 Starship 配置则已自动隐藏）
4. 打开 OBS，确认预览画面正确

#### 录制步骤（素材 2a：/capture 基本用法）

1. 按 `Alt + F9` 开始录制
2. **等待 2 秒**（给后期剪辑留空间）
3. 模拟打字输入以下内容（速度：中等偏慢，让观众看清每个字符）：
   ```
   /capture 给王总回邮件确认合同细节
   ```
   > **打字技巧**：不要一口气打完。先打 `/capture `（带空格），停顿约 0.5 秒，再打后面的中文描述。这模拟真人的思考节奏。
4. 打完后**停顿 1 秒**，然后按 `Enter`
5. 立即在终端中执行预制脚本来显示输出：
   ```
   C:\spe-video-assets\scripts\scene2_capture.ps1
   ```
   > **重要**：这一步在实际录制中会露出脚本路径。有两种处理方式：
   > - **方式 A（推荐）**：录制时分两段。第一段录制打字 + 回车，第二段只录制输出结果。后期剪辑时拼接，中间用一帧黑屏过渡。
   > - **方式 B**：提前在 PowerShell profile 中定义函数别名，让 `/capture` 实际调用脚本（见下方"高级技巧"）。
6. 输出显示完毕后，**停顿 2 秒**让观众阅读
7. 按 `Alt + F9` 停止录制

#### 高级技巧：模拟真实命令（推荐方式 B）

在 PowerShell profile（`notepad $PROFILE`）中追加以下函数：

```powershell
# 模拟 SPE 命令用于视频录制
function /capture {
    param([Parameter(ValueFromRemainingArguments)]$args)
    $text = $args -join ' '
    if ($text -eq 'auto') {
        & C:\spe-video-assets\scripts\scene2_capture_auto.ps1
    } else {
        & C:\spe-video-assets\scripts\scene2_capture.ps1
    }
}
function /plan-day { & C:\spe-video-assets\scripts\scene3_planday.ps1 }
function /time-block {
    param([Parameter(ValueFromRemainingArguments)]$args)
    $text = $args -join ' '
    if ($text -match 'focus') {
        & C:\spe-video-assets\scripts\scene4_timeblock_focus.ps1
    } else {
        & C:\spe-video-assets\scripts\scene4_timeblock.ps1
    }
}
function /weekly-review { & C:\spe-video-assets\scripts\scene5_weeklyreview.ps1 }
```

保存后重启 Terminal。现在直接输入 `/capture 给王总回邮件确认合同细节` 就会显示预制输出，录制时看起来完全真实。

> **注意**：PowerShell 函数名以 `/` 开头在某些版本中可能有兼容性问题。如果不行，改用不带斜杠的名字（如 `capture`），录制时输入 `capture` 即可，后期字幕中写 `/capture`。或者使用 `Set-Alias` 方式。

#### 录制步骤（素材 2b：/capture auto）

1. 清屏：输入 `Clear-Host` 回车
2. 按 `Alt + F9` 开始录制
3. 等待 2 秒
4. 模拟打字输入：`/capture auto`
5. 停顿 0.5 秒，按 `Enter`
6. 脚本自动逐行显示扫描结果（内置了 Sleep 延迟）
7. 全部输出完成后，停顿 3 秒
8. 按 `Alt + F9` 停止录制

#### 可能的录制难点

| 问题 | 解决方案 |
|------|----------|
| 打字速度不自然 | 多练几次，或者后期在剪映中调整播放速度 |
| 输出文本颜色不对 | 检查 PowerShell 脚本中的颜色参数是否正确 |
| 光标闪烁太快/太慢 | Windows Terminal 设置中目前无法调整光标闪烁频率，保持默认即可 |

**预期素材时长**：素材 2a 约 20 秒，素材 2b 约 20 秒

---

### 场景 3：/plan-day 演示（01:15 - 02:15）

#### 录制前准备

1. 清屏：`Clear-Host`
2. 确认终端窗口位置没有变化

#### 录制步骤

1. 按 `Alt + F9` 开始录制
2. 等待 2 秒
3. 模拟打字输入：`/plan-day`
4. 停顿 0.5 秒，按 `Enter`
5. 脚本自动逐区域显示输出（内置了 300ms 延迟模拟加载效果）
6. 全部输出完成后，**停顿 4 秒**（这是最长的输出，观众需要更多时间阅读）
7. 按 `Alt + F9` 停止录制

#### 注意事项

- 这个场景的输出最长，确保终端窗口足够高，不会出现滚动条截断内容
- 如果输出超出一屏：在终端设置中临时将字体大小从 18 降到 16，或增大终端窗口高度
- "收件箱分流"是这个场景的重点，后期需要在此处添加高亮框，所以录制时确保该区域清晰可见

**预期素材时长**：约 30 秒

---

### 场景 4：/time-block 演示（02:15 - 03:00）

#### 录制前准备

1. 清屏：`Clear-Host`

#### 录制步骤（素材 4a：常规时间块）

1. 按 `Alt + F9` 开始录制
2. 等待 2 秒
3. 模拟打字输入：`/time-block "审阅Janus方案" 2h tomorrow`
   > **打字提示**：先打 `/time-block `，停顿，然后打引号和任务名，停顿，再打 `2h tomorrow`。分段打字更自然。
4. 停顿 0.5 秒，按 `Enter`
5. 输出显示后，停顿 2 秒
6. 按 `Alt + F9` 停止录制

#### 录制步骤（素材 4b：focus 模式）

1. 不要清屏（保留上一条命令的输出在上方，模拟连续操作的感觉）
2. 按 `Alt + F9` 开始录制
3. 等待 1 秒
4. 模拟打字输入：`/time-block focus 2h`
5. 停顿 0.5 秒，按 `Enter`
6. 输出显示后，停顿 2 秒
7. 按 `Alt + F9` 停止录制

**预期素材时长**：素材 4a 约 15 秒，素材 4b 约 12 秒

---

### 场景 5：/weekly-review 演示（03:00 - 03:35）

#### 录制前准备

1. 清屏：`Clear-Host`

#### 录制步骤

1. 按 `Alt + F9` 开始录制
2. 等待 2 秒
3. 模拟打字输入：`/weekly-review`
4. 停顿 0.5 秒，按 `Enter`
5. 脚本逐区域显示输出
6. 全部输出完成后，停顿 3 秒
7. 按 `Alt + F9` 停止录制

#### 注意事项

- 输出内容较长，确认字体大小下能一屏显示完整
- 后期需要对"本周成就"和"时间分配"区域做高亮处理

**预期素材时长**：约 25 秒

---

### 场景 6：总结 + CTA（03:35 - 04:00）

**此场景无需终端录制**。画面全部在后期制作：
- SPE 四层架构图动画 → 使用预制信息图 G1
- CTA 文字逐行出现 → 剪映文字动画
- 结尾 logo → 静态图片

**需要准备的素材**：
1. SPE 四层架构图（信息图 G1）
2. CTA 文字内容（直接在剪映中添加）
3. Synapse Personal Engine logo + Janus Digital 版权信息（静态图片）

---

## Part 3：AI 配音制作指南

### 3.1 旁白文本准备

在制作 TTS 音频之前，需要将分镜脚本中的旁白文本做 TTS 适配处理。

**创建旁白文本文件**：

新建文件 `C:\spe-video-assets\narration\`，为每个场景创建单独的文本文件：

**`scene1_hook.txt`**：
```
Synapse，帮你管好了44人的AI团队。
但你自己呢？
脑子里突然冒出的想法，Slack里堆积的消息，日历上散落的会议，这些谁来管？
今天用4分钟，我带你上手SPE。
4个命令，让你的每一天，都不漏一件事。
```

**`scene2_capture.txt`**：
```
第一个命令，capture。随时随地把想法扔进收件箱。
比如你突然想起要给王总回邮件，直接capture加上描述，一秒存入。
不用切应用，不用开备忘录。想到就说，说完继续干活。
还有个更厉害的，会话结束前输入capture auto。
AI会自动扫描你整段对话，把聊天中提到的所有待办全部提取出来，一条都不漏。
而且，如果你配了Session End Hook，关闭会话时这步会自动执行。连capture auto都不用打。
```

**`scene3_planday.txt`**：
```
收件箱有东西了，然后呢？每天早上第一件事，plan day。
一个命令，SPE自动做6件事。
日历、任务、Slack、OKR，四个信息源自动汇总，然后给你一份今日焦点报告。
注意看这个收件箱分流。AI自动把你昨天capture的东西分成四类。需要你决策的、可以派给团队的、要自己做的、还有纯参考的。你只需要扫一眼确认就行。
两分钟，你就知道今天最重要的事是什么，和什么时候做。
```

**`scene4_timeblock.txt`**：
```
知道要做什么了，接下来锁定时间。time block帮你在Google Calendar上创建专属时间块。
告诉它任务名、时长、日期。它会自动找到你日历上的空闲时段。而且优先安排在你精力最好的时候。上午状态好？深度工作就放上午。
focus模式专门用来创建深度工作时段，青色标记，一眼就能在日历上认出来。
还支持deadline模式创建截止日期提醒，红色标记，到期前自动通知你。
每种任务类型都有专属颜色。打开日历一眼就知道这块时间是干什么的。
```

**`scene5_weeklyreview.txt`**：
```
最后一个命令，每周五花10分钟，weekly review。
本周干了什么、OKR进了多少、做了哪些关键决策、时间花在哪了。一张报告全看清。
系统还会给你下周的焦点建议。这就是SPE的回顾层。让你的每一周都比上一周更好。
```

**`scene6_cta.txt`**：
```
回顾一下。4个命令，4个动作。
想到就capture。早上plan day看今日焦点。重要的事time block锁进日历。周五weekly review复盘一周。
捕获、规划、执行、回顾。一个闭环，零遗漏。
现在就打开Claude Code，输入capture，把你脑子里第一件想到的事存进去。
明天早上，用plan day开始你高效的一天。
```

#### TTS 适配处理规则

对比原始分镜脚本旁白和上方文本，注意以下改动：

| 原始写法 | TTS 适配 | 原因 |
|----------|----------|------|
| `...`（省略号） | 句号或逗号 | TTS 不识别省略号的停顿含义，用标点控制节奏 |
| `/capture` | `capture` | TTS 会把斜杠读出来（如"斜杠capture"），去掉斜杠 |
| `/plan-day` | `plan day` | 同上，且连字符会导致异常停顿 |
| `/time-block` | `time block` | 同上 |
| `/weekly-review` | `weekly review` | 同上 |
| 英文缩写大写 `SPE` | `SPE` | 大写缩写 TTS 通常会逐字母读，此处保留（如果 TTS 读成单词，改为 `S P E`，字母间加空格） |
| `SessionEnd Hook` | `Session End Hook` | 拆开以确保正确发音 |

### 3.2 剪映 TTS 使用步骤

剪映桌面版内置了"文本朗读"功能（免费），可以将文本转为 AI 语音。

#### 声音选择

打开剪映 → 新建项目 → 点击顶部"文本"→ 输入任意文字 → 右侧面板找到"文本朗读" → 浏览声音列表。

**推荐声音**（按优先级排序）：

| 声音名称 | 类型 | 推荐理由 |
|----------|------|----------|
| **云希** / "活力男声" | 中文男声 | 语气专业偏年轻，适合技术教程，类似 Fireship 的节奏感 |
| **云扬** / "成熟男声" | 中文男声 | 语气沉稳，适合正式教程 |
| **晓晓** / "温和女声" | 中文女声 | 语气亲和，适合引导型教程 |

> **选择建议**：建议先用"云希"试录场景 1 的旁白，听一遍感受语气是否匹配。不满意再换。最终全部场景必须使用同一个声音。

#### 逐场景生成 TTS 音频

对每个场景的旁白文本，执行以下步骤：

1. 打开剪映 → 新建项目（项目名：`SPE-Video-Narration`）
2. 点击顶部工具栏 **"文本"** → **"默认文本"**
3. 时间线上出现一个文本轨道，双击它打开编辑
4. 将 `scene1_hook.txt` 的全部内容粘贴到文本框中
5. 在右侧属性面板中找到 **"文本朗读"**（或"AI 朗读"），点击开启
6. 选择推荐声音（如"云希"）
7. 调整参数：
   - **语速**：调到 **1.1x - 1.2x**（中等偏快，保持教程节奏感）
   - **音调**：保持默认（0）
   - **音量**：保持默认（100%）
8. 点击 **"开始朗读"** / **"生成语音"**
9. 生成完成后，**试听一遍**。如果某些句子的停顿不自然，回到文本中调整标点：
   - 加句号 `.` → 长停顿（约 0.5-0.8 秒）
   - 加逗号 `,` → 短停顿（约 0.2-0.3 秒）
   - 加感叹号 `!` → 语气上扬
   - 删除标点 → 连续读，无停顿
10. 满意后，右键音频轨道 → **"导出音频"**（或直接使用剪映项目内的音频轨道）
11. 导出保存到 `C:\spe-video-assets\narration\scene1_hook.wav`

**对每个场景重复步骤 3-11**，最终得到 6 个音频文件：
- `scene1_hook.wav`
- `scene2_capture.wav`
- `scene3_planday.wav`
- `scene4_timeblock.wav`
- `scene5_weeklyreview.wav`
- `scene6_cta.wav`

#### 音频后处理

所有 TTS 音频生成后，在剪映中：
1. 逐个试听，记录每段音频的时长
2. 确认总时长在 3:00 - 3:30 之间（余下时间用于画面停顿和转场）
3. 如果某段语速过快（听不清），将该段 TTS 语速降到 1.0x 重新生成
4. 如果总时长超过 3:30，优先压缩场景 3（最长）的旁白

---

## Part 4：剪辑合成流程

### 4.1 剪映项目设置

1. 打开剪映桌面版
2. 点击 **"新建项目"**，项目名：`SPE-Quick-Start-MVP`
3. 项目打开后，点击右上角齿轮图标（项目设置），配置：

| 设置项 | 值 |
|--------|------|
| 分辨率 | 1920 x 1080 |
| 帧率 | 30fps |
| 画幅比例 | 16:9 |

### 4.2 素材导入顺序

点击左上角 **"导入"** 按钮，按以下顺序导入素材（保持有序）：

**文件夹 1：录屏素材**
- `scene2_capture_basic.mkv` — 场景 2a
- `scene2_capture_auto.mkv` — 场景 2b
- `scene3_planday.mkv` — 场景 3
- `scene4_timeblock.mkv` — 场景 4a
- `scene4_timeblock_focus.mkv` — 场景 4b
- `scene5_weeklyreview.mkv` — 场景 5

> **MKV 转 MP4**：如果剪映不支持 MKV，先在 OBS 中点击菜单 → 文件 → 转封装（Remux），将 MKV 转为 MP4。

**文件夹 2：旁白音频**
- `scene1_hook.wav`
- `scene2_capture.wav`
- `scene3_planday.wav`
- `scene4_timeblock.wav`
- `scene5_weeklyreview.wav`
- `scene6_cta.wav`

**文件夹 3：信息图素材**
- `G1_spe_architecture.png` — SPE 四层架构图
- `G2_inbox_triage.png` — 收件箱分流示意图
- `G3_energy_timeline.png` — 精力分配时段图
- `G4_pdca_cycle.png` — PDCA 循环图
- `G5_progress_indicator.png` — 四命令进度指示器（4 个状态各一张）
- `G6_color_codes.png` — 颜色编码速查卡
- `hook_messy_todo.png` — 场景 1 杂乱待办列表图
- `spe_logo_outro.png` — 结尾 logo

**文件夹 4：背景音乐**
- `bgm_tech_ambient.mp3`（见 4.7 节选择建议）

### 4.3 时间线组装

剪映时间线从左到右代表时间推进。按以下顺序在时间线上排列素材：

**轨道说明**：
- 轨道 1（最底层）：背景音乐（全程）
- 轨道 2：旁白音频
- 轨道 3：屏幕录制 / 主画面
- 轨道 4：信息图叠加层
- 轨道 5：文字标注 / 字幕

#### 逐场景组装步骤

**场景 1（00:00 - 00:30）**：
1. 将 `hook_messy_todo.png` 拖到轨道 3，持续时间设为 3 秒
2. 将 `scene1_hook.wav` 拖到轨道 2，与画面起始点对齐
3. 3 秒处添加转场效果（见 4.5 节）
4. 3 秒后放入场景 2 录屏素材的第一帧作为"干净终端"画面
5. 在旁白说到"4 个命令"时（大约 0:22），将四个命令卡片图（从 G5 素材裁剪）添加到轨道 4，设置从底部滑入动画

**场景 2（00:30 - 01:15）**：
1. 将 `scene2_capture_basic.mkv` 拖到轨道 3，放在场景 1 画面后面
2. 将 `scene2_capture.wav` 拖到轨道 2，起始点对齐场景 2 画面
3. **音画对位关键点**：旁白说"直接 capture 加上描述"时，画面上应正在打字输入命令。用剪映的分割工具（`Ctrl + B`）微调视频素材的起始位置
4. 在旁白说到"/capture auto"时，切换到 `scene2_capture_auto.mkv` 素材
5. 在旁白提到"SPE 四层架构图"时，将 `G1_spe_architecture.png` 放到轨道 4，位置在画面右侧 30% 区域，持续约 5 秒，设置淡入淡出（各 0.3 秒）
6. 将 G5 进度指示器（/capture 高亮版）放在轨道 4 左上角，贯穿整个场景 2

**场景 3（01:15 - 02:15）**：
1. 将 `scene3_planday.mkv` 拖到轨道 3
2. 将 `scene3_planday.wav` 拖到轨道 2
3. **音画对位关键点**：旁白说"一个命令"时，画面上刚按下回车，开始显示输出
4. 旁白说到"收件箱分流"时，在轨道 4 添加一个半透明白色矩形框，框住终端输出中"收件箱分流"区域，持续 3 秒，设置闪烁一次效果
5. 同时将 `G2_inbox_triage.png` 放到轨道 4 右侧区域，淡入淡出各 0.3 秒，持续约 5 秒
6. 更新 G5 进度指示器为 /plan-day 高亮版

**场景 4（02:15 - 03:00）**：
1. 将 `scene4_timeblock.mkv` 和 `scene4_timeblock_focus.mkv` 依次拖到轨道 3
2. 将 `scene4_timeblock.wav` 拖到轨道 2
3. 旁白说"精力最好的时候"时，在轨道 4 右侧添加 `G3_energy_timeline.png`
4. 旁白说到颜色编码时，在轨道 4 右下角添加 `G6_color_codes.png`
5. 更新 G5 进度指示器为 /time-block 高亮版

**场景 5（03:00 - 03:35）**：
1. 将 `scene5_weeklyreview.mkv` 拖到轨道 3
2. 将 `scene5_weeklyreview.wav` 拖到轨道 2
3. 旁白说到"回顾层"时，在轨道 4 右侧添加 `G4_pdca_cycle.png`
4. 更新 G5 进度指示器为 /weekly-review 高亮版

**场景 6（03:35 - 04:00）**：
1. 将 `G1_spe_architecture.png` 放到轨道 3 作为主画面（全屏显示）
2. 将 `scene6_cta.wav` 拖到轨道 2
3. 旁白说到"现在就打开 Claude Code"时，画面切换为 CTA 文字（在剪映中用文字工具添加，逐行出现，每行间隔 1 秒）
4. 最后 3 秒放入 `spe_logo_outro.png` 作为结尾画面
5. G5 进度指示器四个命令全部高亮

### 4.4 音画对位方法

这是剪辑中最关键也最耗时的步骤。核心原则：**观众听到什么就看到什么**。

**具体操作**：

1. 先只放旁白音频到轨道 2，从头播放，记录关键时间点：
   - 每句话的开始/结束时间
   - 提到命令名称的精确时间
   - 需要配合画面动作的时间
2. 然后将录屏素材放到轨道 3，用剪映的分割工具（快捷键 `Ctrl + B`）在关键时间点切割
3. 拖动素材片段，使画面动作与旁白对齐
4. 如果录屏太长，用"变速"功能加速非关键部分（如等待输出时）
5. 如果录屏太短，在输出显示后多停留几帧

**对齐检查**：逐场景播放，确认以下关键对位点：

| 场景 | 旁白内容 | 画面应该显示 |
|------|----------|-------------|
| 2 | "直接 capture 加上描述" | 正在打字输入命令 |
| 2 | "一秒存入" | 输出结果刚出现 |
| 2 | "capture auto" | 正在打字输入 /capture auto |
| 3 | "一个命令" | 刚按下回车 |
| 3 | "收件箱分流" | 输出滚动到分流区域 |
| 4 | "告诉它任务名" | 正在打字输入 |
| 4 | "focus 模式" | 正在打字输入 focus 命令 |
| 5 | "weekly review" | 输出开始显示 |

### 4.5 转场效果

在剪映中，点击两个素材之间的连接点，会弹出转场效果选择面板。

**推荐转场**（保持统一风格）：

| 使用场景 | 转场效果 | 剪映中的名称 | 时长 |
|----------|----------|-------------|------|
| 场景 1 → 场景 2 | 碎裂/破碎效果 | "基础" → "闪白" 或 "特效" → "故障" | 0.5 秒 |
| 场景 2 → 场景 3 | 左推 | "基础" → "左推" / "覆盖（左）" | 0.3 秒 |
| 场景 3 → 场景 4 | 左推 | 同上 | 0.3 秒 |
| 场景 4 → 场景 5 | 左推 | 同上 | 0.3 秒 |
| 场景 5 → 场景 6 | 淡入淡出 | "基础" → "淡化" / "叠化" | 0.5 秒 |

> **原则**：场景 2-5 之间使用相同的"左推"转场，保持连贯。首尾用特殊转场做区分。

### 4.6 字幕制作

#### 自动生成字幕

1. 在剪映中，确保旁白音频已全部放置在时间线上
2. 点击顶部工具栏 **"文本"** → **"智能字幕"** → **"识别字幕"**
3. 选择语言：**中文**
4. 点击 **"开始识别"**，等待处理完成
5. 字幕自动生成在时间线的文本轨道上

#### 手动校正

自动识别的字幕需要逐条检查：

1. 双击时间线上的每一条字幕进行编辑
2. 重点检查以下容易识别错误的内容：

| 正确文本 | 常见误识别 |
|----------|-----------|
| SPE | SBE / SPD / 是PE |
| capture | 凯普处 / 卡普切 |
| plan-day | 普兰Day / 盘蝶 |
| time-block | 太门Block / 泰姆布洛克 |
| weekly-review | 维克里Review / 微客力 |
| Synapse | 赛纳普斯 / 思耐普斯 |
| OKR | OK啊 / OKER |
| Slack | 思莱克 / 斯拉克 |
| SessionEnd Hook | 赛声恩Hook / 色森德 |

3. 将所有英文术语手动修正为正确拼写
4. 确认每条字幕的显示时间与旁白匹配（开始/结束时间）

#### 字幕样式设置

选中任意一条字幕 → 在右侧属性面板中设置：

| 属性 | 值 |
|------|------|
| 字体 | 思源黑体（Source Han Sans）或微软雅黑 |
| 字号 | 32-36（在 1080p 下清晰可读） |
| 字体颜色 | 白色 `#FFFFFF` |
| 描边 | 开启，黑色 `#000000`，宽度 2px |
| 背景 | 关闭（不加字幕底色条） |
| 位置 | 画面底部居中，距底约 10% |
| 对齐 | 居中 |

设置好一条后，右键 → **"应用到全部字幕"**。

### 4.7 背景音乐

#### 选择建议

在剪映的 **"音频"** → **"音乐"** 库中搜索以下关键词：

| 搜索关键词 | 推荐风格 |
|-----------|---------|
| `科技` / `tech` | 低调的电子环境音 |
| `企业` / `corporate` | 轻快但不抢眼的商务背景乐 |
| `教程` / `tutorial` | 专为教程设计的平缓背景乐 |
| `ambient` | 环境氛围音 |

**选择原则**：
- 无人声/歌词
- 节奏平稳，不能有突然的高潮或重拍
- 音量低，不能盖过旁白
- 时长 4 分钟以上（不够可循环）

#### 音量调节

1. 将背景音乐拖到轨道 1（最底层）
2. 选中音乐轨道，在右侧属性面板中将 **音量调到 10%-15%**（即非常小声）
3. 验证方法：播放任意一段旁白区域，确认能清晰听到旁白，背景音乐仅作为"存在感"
4. 如果旁白的某个停顿处音乐太突出，用"音量关键帧"在该处进一步降低音量

#### 音乐淡入淡出

1. 选中音乐轨道
2. 在剪映中找到 **"淡入淡出"** 设置（通常在音频属性面板中）
3. 设置：
   - 开头淡入：2 秒
   - 结尾淡出：3 秒

### 4.8 导出设置

全部剪辑完成后：

1. 点击右上角 **"导出"** 按钮
2. 配置导出参数：

| 设置项 | 值 | 说明 |
|--------|------|------|
| 分辨率 | 1920 x 1080 | Full HD |
| 帧率 | 30fps | 与项目一致 |
| 编码 | H.264 | 兼容性最好 |
| 码率 | 16 Mbps（或"推荐"） | 高画质 |
| 格式 | MP4 | 通用格式 |

3. 导出路径选择 `C:\spe-video-assets\output\`
4. 文件名：`SPE-Quick-Start-MVP-v1.mp4`
5. 点击 **"导出"**，等待完成

---

## Part 5：侧边信息图设计规格

### 通用设计规范

| 规范项 | 值 |
|--------|------|
| **品牌主色** | `#0ea5e9`（天蓝色） |
| **品牌辅色** | `#14b8a6`（青色/teal） |
| **强调色** | `#f59e0b`（琥珀色，用于高亮） |
| **背景色** | `#0f172a`（深蓝黑色，与终端一致） |
| **半透明背景** | `#0f172a` + 80% 不透明度 |
| **文字主色** | `#e2e8f0`（浅灰白） |
| **文字辅色** | `#94a3b8`（中灰） |
| **标题字体** | Inter Bold 或 思源黑体 Bold |
| **正文字体** | Inter Regular 或 思源黑体 Regular |
| **圆角** | 12px（所有卡片和框） |

### G1：SPE 四层架构图

**出现场景**：场景 2（右侧，"捕获层"高亮）、场景 6（全屏居中）

**尺寸**：场景 2 用 480 x 600 px；场景 6 用 1200 x 800 px

**内容布局**：

```
┌──────────────────────────────┐
│     SPE 四层架构              │ ← 标题，Inter Bold 22px，#e2e8f0
│                              │
│  ┌────────────────────────┐  │
│  │  📥 捕获层 /capture     │  │ ← 层 1，背景 #14b8a6（品牌辅色），白色文字
│  └────────────────────────┘  │
│           ↓                  │
│  ┌────────────────────────┐  │
│  │  📋 处理层 /plan-day    │  │ ← 层 2，背景 #0ea5e9（品牌主色）
│  └────────────────────────┘  │
│           ↓                  │
│  ┌────────────────────────┐  │
│  │  ⏰ 执行层 /time-block  │  │ ← 层 3，背景 #8b5cf6（紫色，区分）
│  └────────────────────────┘  │
│           ↓                  │
│  ┌────────────────────────┐  │
│  │  📊 回顾层 /weekly-review│ │ ← 层 4，背景 #f59e0b（琥珀色）
│  └────────────────────────┘  │
│                              │
│     └────── 循环箭头 ──────┘  │ ← 从"回顾"回到"捕获"的弧形箭头
└──────────────────────────────┘
  背景：#0f172a，80% 不透明度
  圆角：12px
```

**Canva 制作步骤**：
1. 打开 Canva → 自定义尺寸 → 输入 480 x 600
2. 背景色设为 `#0f172a`
3. 添加 4 个圆角矩形，依次填充上述颜色
4. 每个矩形内添加文字
5. 在矩形之间添加向下箭头
6. 最底部到最顶部画一条弧形箭头（Canva 元素库搜索 "curved arrow"）
7. 导出为 PNG（透明背景）

**AI 生成 SVG 的 Prompt**（替代方案）：

```
Create a vertical process diagram in SVG format, 480x600px. Dark background #0f172a at 80% opacity with 12px rounded corners.

Four rounded rectangle blocks stacked vertically with downward arrows between them:
1. "Capture /capture" — background #14b8a6, white text
2. "Process /plan-day" — background #0ea5e9, white text
3. "Execute /time-block" — background #8b5cf6, white text
4. "Review /weekly-review" — background #f59e0b, white text

Add a curved arrow from the bottom block back to the top block on the right side, indicating a cycle. Use Inter or sans-serif font. Title at top: "SPE Architecture" in #e2e8f0.
```

---

### G2：收件箱分流示意图

**出现场景**：场景 3（右侧，持续约 5 秒）

**尺寸**：480 x 400 px

**内容布局**：

```
┌──────────────────────────────┐
│   收件箱分流                  │ ← 标题
│                              │
│         ┌──────┐             │
│         │ 📬   │             │ ← 收件箱图标，居中
│         │ 收件箱│             │
│         └──┬───┘             │
│       ┌──┬─┴─┬──┐           │
│       ↓  ↓   ↓  ↓           │ ← 四条箭头分流
│    ┌───┐┌───┐┌───┐┌───┐     │
│    │决策││委派││个人││参考│     │
│    │ 🔴 ││ 🔵 ││ 🟢 ││ ⚪ │     │ ← 四个色块分类桶
│    └───┘└───┘└───┘└───┘     │
│                              │
└──────────────────────────────┘
```

**配色**：
- 决策桶：`#ef4444`（红色）
- 委派桶：`#0ea5e9`（蓝色）
- 个人桶：`#14b8a6`（青色）
- 参考桶：`#6b7280`（灰色）

**Canva 制作步骤**：
1. 自定义尺寸 480 x 400
2. 背景 `#0f172a` + 80% 不透明度
3. 顶部放一个大的矩形作为"收件箱"
4. 从收件箱向下画 4 条线/箭头
5. 底部放 4 个小矩形，分别填充上述颜色
6. 每个矩形内写分类名
7. 导出 PNG

---

### G3：精力分配时段图

**出现场景**：场景 4（右侧）

**尺寸**：480 x 280 px

**内容布局**：

```
┌──────────────────────────────┐
│   每日精力分配                 │ ← 标题
│                              │
│   高  ████████░░░░░░░░       │ ← 渐变条：青色→黄色→灰色
│   精  │上午  │下午  │傍晚│     │
│   力  │深度  │常规  │轻量│     │
│   低  │工作  │任务  │收尾│     │
│                              │
│   6:00   10:00  14:00  18:00  │ ← 时间轴
└──────────────────────────────┘
```

**配色**：
- 高精力（上午）：`#14b8a6`（青色）
- 中精力（下午）：`#f59e0b`（琥珀色）
- 低精力（傍晚）：`#6b7280`（灰色）
- 渐变条从左到右颜色过渡

**Canva 制作**：
1. 自定义尺寸 480 x 280
2. 使用 3 个相邻的矩形模拟渐变条
3. 下方添加时间刻度文字
4. 每段上方标注工作类型

---

### G4：PDCA 循环图

**出现场景**：场景 5（右侧，"回顾"环节高亮）

**尺寸**：400 x 400 px

**内容布局**：

```
┌──────────────────────────┐
│                          │
│        ┌─Plan──┐         │
│        │ 规划   │         │ ← 蓝色 #0ea5e9
│   ┌───→│       │───┐     │
│   │    └───────┘   ↓     │
│ ┌─┴────┐      ┌────┴─┐   │
│ │ Act  │      │ Do   │   │
│ │ 改进  │      │ 执行  │   │ ← 紫色 #8b5cf6
│ └──↑───┘      └──┬───┘   │    绿色 #22c55e
│   │    ┌───────┐  │      │
│   │    │Check  │  │      │
│   └────│ 回顾  │←─┘      │ ← 琥珀色 #f59e0b，高亮加粗边框
│        └───────┘         │
│                          │
└──────────────────────────┘
```

**特殊处理**：
- "Check/回顾"环节用**加粗边框**（4px）+ **发光效果**来高亮
- 从"Check"到"Plan"的箭头也加粗，表示"回顾驱动下一轮规划"

**Canva 制作**：
1. 自定义尺寸 400 x 400
2. 搜索 Canva 元素库 "cycle diagram" 找到四象限循环模板
3. 修改颜色和文字
4. 加粗"Check/回顾"的边框

---

### G5：四命令进度指示器

**出现场景**：全程（左上角常驻）

**尺寸**：300 x 50 px

**内容布局**（水平排列）：

```
[/capture] ── [/plan-day] ── [/time-block] ── [/weekly-review]
  高亮          灰色           灰色             灰色
```

**需要制作 5 个版本**：

| 版本 | 高亮项 | 使用场景 |
|------|--------|----------|
| G5-1 | /capture | 场景 2 |
| G5-2 | /plan-day | 场景 3 |
| G5-3 | /time-block | 场景 4 |
| G5-4 | /weekly-review | 场景 5 |
| G5-5 | 全部高亮 | 场景 6 |

**配色**：
- 高亮状态：背景 `#14b8a6`，文字白色
- 未激活状态：背景 `#1e293b`，文字 `#475569`
- 连接线：`#334155`

**Canva 制作**：
1. 自定义尺寸 300 x 50
2. 创建 4 个小圆角矩形排成一排
3. 用线段连接
4. 为 G5-1 版本：第一个矩形填充 `#14b8a6`，其余填充 `#1e293b`
5. 复制 4 次，分别修改高亮位置
6. 全部导出 PNG（透明背景）

---

### G6：颜色编码速查卡

**出现场景**：场景 4（右下角）

**尺寸**：320 x 200 px

**内容布局**：

```
┌──────────────────────────┐
│  时间块颜色编码            │ ← 标题
│                          │
│  🟦 Peacock 青色 = 深度工作│
│  🟨 Banana 黄色 = 常规任务 │
│  🟥 Tomato 红色 = Deadline │
│  🟩 Sage 绿色 = 学习/发展  │
│                          │
└──────────────────────────┘
```

**配色**：
- Peacock 色块：`#14b8a6`
- Banana 色块：`#f59e0b`
- Tomato 色块：`#ef4444`
- Sage 色块：`#22c55e`

**Canva 制作**：
1. 自定义尺寸 320 x 200
2. 背景 `#0f172a` + 80% 不透明度
3. 每行放一个小色块 + 对应文字
4. 导出 PNG

---

### 场景 1 用素材：杂乱待办列表

**尺寸**：1920 x 1080 px（全屏）

**内容**：模拟一个桌面上散乱堆叠的各种待办信息：
- 2-3 张黄色便签（手写体文字，如"给王总打电话"）
- 1 个 Slack 消息截图（模拟的）
- 1 个 Google Calendar 通知截图（模拟的）
- 内容倾斜摆放，互相叠压，制造杂乱感

**Canva 制作**：
1. 自定义尺寸 1920 x 1080
2. 背景设为浅灰色（模拟桌面）
3. 搜索"sticky note"元素，放置 2-3 个
4. 添加文本框模拟 Slack 消息
5. 各元素旋转 5-15 度，制造杂乱感
6. 导出 PNG

---

### 结尾 Logo 画面

**尺寸**：1920 x 1080 px（全屏）

**内容**：

```
┌────────────────────────────────────────────┐
│                                            │
│                                            │
│         Synapse Personal Engine             │ ← Inter Bold 48px, #e2e8f0
│                                            │
│         ─────────────────────               │ ← 分割线, #14b8a6
│                                            │
│    详细使用手册见 spe-user-guide.html        │ ← Inter Regular 24px, #94a3b8
│                                            │
│                                            │
│                                            │
│              Janus Digital                  │ ← Inter Light 18px, #475569
│              2026                           │
│                                            │
└────────────────────────────────────────────┘
  背景：#0f172a（纯色，不透明）
```

---

## Part 6：质量自检清单

视频导出后，用以下清单逐项检查。播放 3 遍：第 1 遍关注视觉，第 2 遍关注音频，第 3 遍关注内容。

### 视觉一致性检查

- [ ] 终端配色全程统一（SPE Dark 方案，背景 #0f172a）
- [ ] 终端字体全程统一（JetBrains Mono 18pt）
- [ ] 信息图风格统一（同一套配色、字体、圆角）
- [ ] 进度指示器（G5）在每个场景正确切换高亮状态
- [ ] 所有信息图使用半透明背景，不遮挡终端重要内容
- [ ] 转场效果统一（场景 2-5 之间用相同的左推转场）
- [ ] 无杂物画面（桌面图标、任务栏、通知弹窗等）
- [ ] 终端窗口位置全程一致（不能有跳动）

### 音画同步检查

- [ ] 旁白提到命令名时，画面正在输入/显示该命令
- [ ] 旁白停顿时，画面给出阅读时间
- [ ] 旁白提到信息图内容时，对应信息图已在画面中
- [ ] 没有旁白和画面严重不同步的地方（容差 <0.5 秒）
- [ ] 背景音乐在旁白停顿时不会突然变得突兀
- [ ] 视频开头和结尾的音乐淡入淡出正常

### 字幕准确性检查

- [ ] 所有英文术语拼写正确：SPE、/capture、/plan-day、/time-block、/weekly-review
- [ ] 所有中文字幕与旁白实际内容一致
- [ ] 字幕显示时间与旁白匹配（不超前、不滞后）
- [ ] 字幕在画面底部位置统一，不与终端内容重叠
- [ ] 字幕可读性良好（字号够大、描边清晰）

### 技术内容准确性检查

- [ ] 所有命令名称正确：/capture、/plan-day、/time-block、/weekly-review
- [ ] 命令输出格式与 SPE 使用手册一致
- [ ] 收件箱分流的四个类别正确：决策、委派、个人、参考
- [ ] 时间块颜色编码正确：Peacock=深度工作、Banana=常规、Tomato=Deadline、Sage=学习
- [ ] OKR 追踪逻辑描述准确
- [ ] 未出现错误的功能承诺（如未实现的功能）

### 品牌元素检查

- [ ] 品牌主色 #0ea5e9 和辅色 #14b8a6 使用正确
- [ ] "Synapse Personal Engine" 名称出现在结尾
- [ ] "Janus Digital" 版权信息在结尾画面
- [ ] 配色与 SPE 使用手册（spe-user-guide.html）保持一致

### 输出格式检查

- [ ] 分辨率：1920 x 1080
- [ ] 帧率：30fps
- [ ] 格式：MP4 / H.264
- [ ] 文件大小合理（4 分钟视频约 300-500 MB）
- [ ] 视频在不同播放器中均可正常播放（Windows 自带播放器 + 浏览器）
- [ ] 视频总时长在 3:30 - 4:30 之间

### 整体观感检查

- [ ] 从头到尾完整观看一遍，节奏是否流畅
- [ ] 是否有无聊/拖沓的段落需要加速
- [ ] 是否有信息过密、来不及消化的段落需要延长停顿
- [ ] 旁白语气是否全程一致（无突然变调/变速）
- [ ] 推荐找 1-2 位未参与制作的人试看，收集反馈

---

## 附录：素材文件清单总览

```
C:\spe-video-assets\
├── scripts\                              ← 预制终端输出脚本
│   ├── scene2_capture.ps1
│   ├── scene2_capture_auto.ps1
│   ├── scene3_planday.ps1
│   ├── scene4_timeblock.ps1
│   ├── scene4_timeblock_focus.ps1
│   └── scene5_weeklyreview.ps1
│
├── narration\                            ← 旁白文本 + TTS 音频
│   ├── scene1_hook.txt
│   ├── scene2_capture.txt
│   ├── scene3_planday.txt
│   ├── scene4_timeblock.txt
│   ├── scene5_weeklyreview.txt
│   ├── scene6_cta.txt
│   ├── scene1_hook.wav                   ← TTS 生成
│   ├── scene2_capture.wav
│   ├── scene3_planday.wav
│   ├── scene4_timeblock.wav
│   ├── scene5_weeklyreview.wav
│   └── scene6_cta.wav
│
├── graphics\                             ← 信息图素材
│   ├── G1_spe_architecture.png
│   ├── G2_inbox_triage.png
│   ├── G3_energy_timeline.png
│   ├── G4_pdca_cycle.png
│   ├── G5-1_progress_capture.png
│   ├── G5-2_progress_planday.png
│   ├── G5-3_progress_timeblock.png
│   ├── G5-4_progress_weeklyreview.png
│   ├── G5-5_progress_all.png
│   ├── G6_color_codes.png
│   ├── hook_messy_todo.png
│   └── spe_logo_outro.png
│
├── recordings\                           ← OBS 录屏原素材
│   ├── scene2_capture_basic.mkv
│   ├── scene2_capture_auto.mkv
│   ├── scene3_planday.mkv
│   ├── scene4_timeblock.mkv
│   ├── scene4_timeblock_focus.mkv
│   └── scene5_weeklyreview.mkv
│
└── output\                               ← 最终导出
    └── SPE-Quick-Start-MVP-v1.mp4
```

---

## 附录：制作流程总览（执行顺序）

```
Phase 1：环境搭建
  ├─ 安装 OBS Studio + 配置录制参数
  ├─ 安装剪映桌面版
  ├─ 安装 JetBrains Mono 字体
  ├─ 配置 Windows Terminal（SPE Dark 配色方案）
  ├─ 配置 Starship prompt（最小化 prompt）
  └─ 创建预制脚本（6 个 .ps1 文件）+ 配置模拟命令函数

Phase 2：素材制作（可并行）
  ├─ [ai_visual_creator] 制作信息图 G1-G6 + Hook 素材 + Logo
  └─ [video_producer] 准备旁白文本 + TTS 音频生成

Phase 3：屏幕录制
  ├─ 配置桌面环境（纯黑背景、隐藏任务栏、勿扰模式）
  ├─ 执行录制前检查清单
  ├─ 逐场景录制（场景 2 → 3 → 4 → 5）
  └─ 检查录制素材完整性

Phase 4：剪辑合成
  ├─ 创建剪映项目 + 导入所有素材
  ├─ 时间线组装（按场景顺序）
  ├─ 音画对位调整
  ├─ 添加信息图叠加层
  ├─ 添加转场效果
  ├─ 生成字幕 + 手动校正
  ├─ 添加背景音乐 + 调整音量
  └─ 导出 MP4

Phase 5：质量检查
  ├─ 执行全部自检清单（6 大类）
  ├─ 邀请 1-2 人试看 + 收集反馈
  └─ 根据反馈修改后重新导出
```
