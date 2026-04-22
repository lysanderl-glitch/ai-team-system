# PMO Auto V2.0 产品需求文档 (PRD)

---

## 1. 版本信息

| 字段 | 内容 |
|------|------|
| **版本号** | V2.0 Draft |
| **日期** | 2026-04-22 |
| **作者** | synapse_product_owner |
| **审批状态** | 待产品委员会审批（Lysander + strategy_advisor） |
| **基准版本** | V1.7.0（commit `106532a`，2026-04-22 verified） |
| **参考文档** | `09-system-spec-v170-verified.md`（源码验证版，15条差异） |

### 修订记录

| 版本 | 日期 | 描述 |
|------|------|------|
| v0.1 | 2026-04-22 | 初稿，基于 V1.7.0 源码审计 |
| v0.2 | 2026-04-22 | 依据总裁约束修订范围：REQ-001 范围锁定 target_team、REQ-005 修复方式改为 n8n Credentials Store、新增 REQ-009 团队范围可配置化、REQ-006/007/008 移出 V2.0 |

---

## 2. 背景与目标

### 2.1 V1.7.0 现状回顾

V1.7.0 于 2026-04-22 正式发布（E2E 验证通过），核心里程碑是引入 WF-08 Webhook 实时任务完成通知，彻底替代 V1.6.x 的纯轮询机制。基于 `09-system-spec-v170-verified.md` 的源码逐行审计，发现以下 **15 条与预期不符的差异**，是 V2.0 的核心输入：

**安全类（高优先级）**

1. **差异3：WF-06 硬编码凭证未移除**（`WF-06.json:104,119`）——节点 notes 声称"v1.5.6 已移除"，实际 `ASANA_PAT` 和 `SLACK_TOKEN` 仍以字符串明文写在 Code 节点中，与宣称状态矛盾，属于安全漏洞。

2. **差异2：config.yaml 明文存储生产凭证**（`:176-182`）——Asana PAT、Notion Token、Slack Bot Token、n8n JWT 均以明文存放在仓库，与 Synapse 凭证管理规范相违背。

**功能覆盖类（最大业务痛点）**

3. **差异（隐含）：Webhook 仅覆盖 2 个测试项目**——V1.7.0 灰度仅注册 STD-TEST 项目，其余所有活跃项目的任务完成事件仍依赖 WF-06 每 60min 兜底轮询，PM 无法实时收到通知，核心价值未完全兑现。

**数据一致性类**

4. **差异1：时区混用**（`config.yaml:org.timezone=Asia/Singapore` vs 所有 WF JSON `settings.timezone=Asia/Dubai`）——WF-02、WF-06、WF-08 均写入 Dubai 时区，与 config 定义不一致，scheduleTrigger 时段语义不可预测。

5. **差异7：WF-06 与 WF-08 去重未共享**（`WF-06.json:119` TODO 注释）——两路并行可在 60min 窗口内对同一任务产生重复 DM，源码明确标注 `TODO v1.7 共享幂等` 未实现。

6. **差异6：WF-06 注释与实现不一致**——注释称"过去15分钟时间窗口"，实际 `windowMs = 60min`，过时注释影响可维护性。

**WBS 能力类**

7. **差异（功能限制）：WBS L3/L4 无前置依赖字段**——`wbs_to_asana.py` 的 `wire_dependencies` 仅依赖从 WBS DB 读取的 `前置依赖` 字段，但 L3/L4 层级实际未在 Notion WBS 模板中补齐该字段，导致子任务级依赖链无法触发 WF-08 通知。

**架构与运维类**

8. **差异4：WF-05 vs WF-08 凭证读取方式不统一**——WF-05 从 `$getWorkflowStaticData('global').asanaPAT` 读取，WF-08 从 `$env.ASANA_PAT` 读取，双轨配置易漏，增加运维负担。

9. **差异8：WF-02 active=false**（`WF-02.json:3`）——生产部署时需手动在 n8n UI 激活，无自动化保障，属于部署风险。

10. **差异5：WF-01 空节点 `update-registry-asana-gid`**（`:278`，payload 为空）——历史遗留冗余节点仍参与连线（`:644`），增加 workflow 维护复杂度。

11. **差异13：WF-01 凭证 id 部分为空字符串**——多节点 `"credentials": {"notionApi": {"id": ""}}`，导入到新 n8n 实例后需逐个手动重绑定凭证。

12. **差异9：WBS DB `关键交付物` 字段缺失**——`config.yaml` 定义了 `key_deliverable` CF，Asana 任务中固定写入空字符串，配置与数据源不对齐。

13. **差异10：`create_project_hub.py` registry_url 回退问题**——通过 pmo-api 调用时 `charter_page_id` 传入的是 `registry_page_id`，`query_charter_page` 读 Registry 页面的 relation 字段为空，导致文档库章程条目外链缺失。

14. **差异14：WBS 脚本候选路径含开发本地路径**（`main.py:62-66`）——生产镜像中该路径不会命中，但属于硬编码债务。

15. **差异15：migrations 目录无 001/002 文件**——命名 `003_webhook_tables.sql` 暗示前置迁移，但实际不存在，迁移序号语义不完整。

### 2.2 V2.0 升级目标

基于上述差异，V2.0 聚焦解决以下核心问题：

**核心目标（P0 - 不做则 V2.0 不成立）**
- 无——V1.7.0 已达到可用状态，无影响系统运行的 P0 缺陷

**主要目标（P1 - V2.0 Beta 范围）**
- **目标1**：将 Asana Webhook 注册从灰度（2个项目）扩展到全量活跃项目，使 PM 实现实时任务完成通知，彻底消除60min轮询延迟

**次要目标（P2 - V2.0 GA 范围）**
- **目标2**：消除 WF-06 硬编码凭证安全漏洞（差异3）
- **目标3**：统一系统时区配置（差异1）
- **目标4**：实现 WF-06/WF-08 跨工作流幂等去重（差异7）
- **目标5**：补齐 WBS L3/L4 前置依赖字段（功能限制）
- **目标6**：清理历史遗留技术债务（差异5、6、8、10、12）

### 2.3 North Star Metric（北极星指标）

> **项目经理任务完成通知实时率**
> 定义：收到 Slack DM 通知的时间 ≤ 任务在 Asana 标记完成后 60 秒，且覆盖所有活跃项目
> 目标值：V2.0 GA 后达到 **≥ 95%** 的通知实时率（WF-08 Webhook 路径覆盖率）
> 当前基线：约 10%（仅 STD-TEST 2个项目走 Webhook，其余走60min轮询）

---

## 3. 用户与场景

### 3.1 主要用户画像

**用户 A：PMO 工程师（系统管理员）**

| 属性 | 描述 |
|------|------|
| 规模 | 1-3 人 |
| 技术背景 | 熟悉 n8n、Python、API 调用 |
| 主要关注 | 系统稳定性、配置正确性、部署可重复性 |
| 当前痛点 | WF-06 硬编码凭证有泄露风险；时区混用导致调试困难；Webhook 仅灰度覆盖 |
| 与系统交互频率 | 低频（故障排查、版本升级、配置变更） |

**用户 B：项目经理（PM）**

| 属性 | 描述 |
|------|------|
| 规模 | 10-20 人 |
| 技术背景 | 非技术，使用 Asana/Slack/Notion |
| 主要关注 | 任务进度可视、依赖链通知及时、信息不重复不遗漏 |
| 当前痛点 | 大部分项目没有实时通知，最多60分钟延迟才知道任务完成；偶尔收到重复DM |
| 与系统交互频率 | 高频（每天被动接收通知，每周主动查看任务状态） |

### 3.2 核心使用场景（Jobs-To-Be-Done 格式）

**场景 1（核心）：** 当工程师在 Asana 完成了一项任务，我作为下游负责 PM，希望在 1 分钟内收到 Slack DM 通知，这样我能立刻启动后续工作，而不是最多等 60 分钟。

- **当前体验**：仅 STD-TEST 项目的 PM 能实时收到；其他项目的 PM 等待 WF-06 轮询，最多60分钟延迟
- **V2.0 目标体验**：所有活跃项目的 PM 均在 ≤60秒内收到 Slack DM

**场景 2（可靠性）：** 当同一任务完成事件触发了 WF-08 和 WF-06 两条路径，我作为 PM，希望只收到 1 条 DM 通知，而不是收到 2 条相同内容的消息。

- **当前体验**：在60分钟窗口内，可能同时收到 WF-08（Webhook）和 WF-06（轮询）各发一条 DM
- **V2.0 目标体验**：系统通过共享幂等机制，保证每个任务完成事件只产生 1 条 PM 通知

**场景 3（运维）：** 当 PMO 工程师需要将系统部署到新服务器，我希望配置流程文档清晰、凭证管理规范，不需要手动在代码中找并替换硬编码的 token。

- **当前体验**：WF-06 有硬编码凭证，需手动修改代码才能安全部署
- **V2.0 目标体验**：所有凭证统一通过 n8n `$env` 变量读取，部署时只需配置环境变量

---

## 4. 需求优先级（RICE）

### 4.1 PMO Auto 产品线评分汇总

基于 `requirements_pool.yaml`（2026-04-22，requirements_analyst 完成评分），Effort 换算：S=1天，M=3天，L=8天，XL=20天。

| ID | 需求标题 | Reach | Impact | Confidence | Effort（天） | RICE Score | 优先级 | 备注 |
|----|---------|-------|--------|------------|------------|-----------|--------|------|
| REQ-005 | WF-06 Code节点移除硬编码凭证 | 3 | 3 | 1.0 | 1 | **9.00** | P2 | 修复方式：n8n Credentials Store 引用，非 env 变量；pmo-api 侧 config.yaml 明文维持现状 |
| REQ-009 | Asana 目标团队范围可配置化 | 3 | 1 | 1.0 | 0.5 | **6.00** | P1 | Beta 范围；总裁约束新增 |
| REQ-002 | WBS L3/L4前置依赖字段补齐 | 6 | 1 | 0.8 | 1 | **4.80** | P2 | — |
| REQ-001 | 全量项目Asana Webhook注册 | 8 | 2 | 0.8 | 3 | **4.27** | P1 | 范围限定为 target_team（ProjectProgressTesting），不是全量所有团队 |
| REQ-003 | 时区配置统一（SGT vs Dubai） | 5 | 0.5 | 1.0 | 1 | **2.50** | P2 | — |
| REQ-004 | WF-06/WF-08幂等去重共享 | 7 | 1 | 0.8 | 3 | **1.87** | P2 | — |
| REQ-006 | 服务器部署git clone化 | 2 | 0.5 | 0.8 | 3 | **0.27** | P3 | Deferred（移出 V2.0） |
| REQ-007 | 产品路线图自动维护机制 | — | — | — | — | — | — | Deferred（移出 V2.0） |
| REQ-008 | 需求自动捕获 | — | — | — | — | — | — | Deferred（移出 V2.0） |

### 4.2 分级决策

**P0（必须做，V2.0 不包含，V1.7.0 已满足）**：无。系统当前可运行，无阻断性故障。

**P1（V2.0 Beta 范围）**：
- REQ-009：Asana 目标团队范围可配置化（RICE 6.00，总裁约束新增，Beta 前置条件）
- REQ-001：target_team 范围 Webhook 注册（RICE 4.27，北极星指标直接驱动；范围锁定为 config.yaml `asana.target_team`，不是全量所有团队）

> P1 判断依据：REQ-009 是 REQ-001 的前置依赖，必须先完成团队范围可配置化，再执行 Webhook 批量注册。REQ-001 范围依据总裁约束收窄为 target_team 下项目，不扩展到其他团队。REQ-005 RICE 评分最高但属于 P2，原因是安全修复不阻断 Beta 功能验证，可在 GA 阶段完成。

**P2（V2.0 GA 范围，Beta 后完成）**：
- REQ-005：WF-06 硬编码凭证安全化（RICE 9.00，修复方式为 n8n Credentials Store 引用；pmo-api 侧 config.yaml 明文维持现状，依赖文件权限控制）
- REQ-002：WBS L3/L4 前置依赖字段（RICE 4.80）
- REQ-003：时区统一化（RICE 2.50）
- REQ-004：WF-06/WF-08 幂等去重共享（RICE 1.87）

**Deferred（移出 V2.0，归入 backlog/future）**：
- REQ-006：git clone 化部署（RICE 0.27，运维改进，不影响功能）
- REQ-007：产品路线图自动维护机制（Synapse 体系需求，范围超出 PMO Auto V2.0）
- REQ-008：需求自动捕获（Synapse 体系需求，范围超出 PMO Auto V2.0）

---

## 5. 功能规格

### 5.0 团队范围可配置化（REQ-009，P1-Beta）

**背景**

V1.7.0 代码中 Asana 团队 GID（`1213938170960375`，对应 ProjectProgressTesting 团队）以硬编码字符串的形式散布在代码和配置中。当需要将系统迁移至其他团队或增加多团队支持时，必须逐处搜索替换，存在遗漏风险。本需求将团队范围外化为 `config.yaml` 的 `asana.target_team` 字段，使 Webhook 注册、同步等所有依赖团队范围的逻辑统一从配置读取。

**预期行为**

1. `config.yaml` 新增 `asana.target_team` 字段，默认值为 ProjectProgressTesting 的 Team GID（`1213938170960375`），与现状保持一致。
2. 代码中所有引用该 GID 的位置改为从配置读取，不含任何硬编码的 `1213938170960375` 或 `ProjectProgressTesting` 字符串。
3. 修改 `config.yaml` 中 `asana.target_team` 值后，Webhook 批量注册脚本、定期同步任务等自动使用新团队范围，无需修改代码。

**验收标准（AC）**

- AC1：`config.yaml` 存在 `asana.target_team` 字段，默认值为 ProjectProgressTesting 的 Team GID
- AC2：代码全局搜索 `ProjectProgressTesting` 和原 GID 字符串 `1213938170960375`，结果为 0 条硬编码匹配（配置文件默认值除外）
- AC3：将 `asana.target_team` 修改为另一个测试团队 GID 后，执行批量注册脚本，注册目标为新团队下的项目（通过日志确认）

---

### 5.1 target_team 范围 Asana Webhook 注册（REQ-001，P1）

> **范围说明**：Webhook 注册范围锁定为 `config.yaml` 中 `asana.target_team` 所指定的团队（默认为 ProjectProgressTesting）。注册为累加操作，已注册项目幂等跳过，不删除现有订阅。本节前置依赖 §5.0 REQ-009 完成。

**背景问题描述**

V1.7.0 仅在 STD-TEST 项目完成了 Webhook 灰度验证（`webhook_gid=1214163857544647`），`webhook_subscriptions` 表中仅有 1 条活跃记录。当前除 STD-TEST 外的所有活跃项目，任务完成事件必须等待 WF-06 每 60 分钟轮询才能触发 PM 通知，与 V1.7.0 引入 WF-08 的核心价值（实时通知）相矛盾。

根据 `asana_webhook.py` 的 `/webhooks/asana/register` 端点，注册一个 Webhook 需要传入 `project_gid`，调用 Asana `POST /webhooks`，filters 默认为 `{resource_type:task, action:changed, fields:[completed]}`。全量注册的核心问题是：缺少一个能够自动枚举 target_team 下所有活跃项目并批量注册的运维机制。

**预期行为**

1. 系统提供一次性批量注册脚本（或 n8n 工作流），遍历 `config.yaml` 中 `asana.target_team` 所指向的团队下所有非 archived 项目，对每个项目调用 `POST /webhooks/asana/register`。
2. 注册结果写入 `webhook_subscriptions` 表，已注册项目幂等跳过（`project_gid PRIMARY KEY` 保证）；不删除已有的 Webhook 订阅。
3. 注册完成后，系统定期检查（每日）是否有新项目创建但未注册 Webhook，自动补注册。

**验收标准（AC）**

- AC1：执行批量注册后，通过 `GET /webhooks/asana/list` 查询，返回的活跃订阅数量等于当前 Asana 团队中非 archived 项目的总数（允许 ±1 的网络失败容错）。
- AC2：对任意一个在批量注册后新创建的 Asana 项目，在其内完成一个任务，pmo-api 日志中 `accepted=1`，WF-08 成功执行，对应 PM 在 60 秒内收到 Slack DM。
- AC3：重复执行批量注册脚本，`webhook_subscriptions` 表中记录数量不增加（幂等验证），日志显示已注册项目均为 `SKIP: already registered`。

---

### 5.2 WF-06 凭证安全化（REQ-005，P2）

**背景问题描述**

`WF-06_任务依赖通知.json` 的 Code 节点（`:104` 和 `:119`）中，`ASANA_PAT` 和 `SLACK_TOKEN` 以明文字符串硬编码：`const ASANA_PAT = '2/1213400756695149/...'`。节点 notes（`:121`）标称"v1.5.6 已移除硬编码凭证"，与实际代码直接矛盾。

对比 WF-08 的实现：Code 节点从 `$env.ASANA_PAT` 和 `$env.SLACK_BOT_TOKEN` 读取（`WF-08.json:86,101`）。V2.0 对 WF-06 的修复方式采用 **n8n 内置 Credentials Store 引用**（`$credentials.xxx`），而非 env 变量——这是 n8n 平台推荐的凭证管理标准方式，比 env 变量更安全（凭证加密存储，不出现在进程环境中）。

> **注意**：pmo-api 侧的 `config.yaml` 明文凭证维持现状，不在本需求范围内。pmo-api 侧凭证安全性依赖服务器文件权限控制（chmod 600）。

**预期行为**

1. WF-06 Code 节点中的所有硬编码凭证字符串替换为 n8n Credentials Store 引用（`$credentials.asanaPAT.apiKey`、`$credentials.slackBotToken.token` 等，具体字段名以 n8n Credentials 类型为准）。
2. 节点 notes 中移除"v1.5.6 已移除硬编码"的错误声明，替换为准确的实现描述。
3. pmo-api 侧 `config.yaml` 的 `secrets.*` 区域明文凭证维持现状（不在本需求范围内）。

**验收标准（AC）**

- AC1：在 WF-06 JSON 文件中，全局搜索 `2/1213400756695149`、`xoxb-` 等凭证前缀字符串，结果为 0 条匹配。
- AC2：在 n8n UI 中配置 Credentials Store 中对应凭证，手动触发 WF-06，Code 节点能成功读取凭证值并向 Asana API 发起请求（返回非 401）。
- AC3：删除 n8n Credentials Store 中对应凭证，手动触发 WF-06，Code 节点抛出明确的凭证缺失错误，而非因空字符串静默失败。

---

### 5.3 时区统一化（REQ-003，P2）

**背景问题描述**

`config.yaml` 在两处定义时区为 `Asia/Singapore`（SGT，UTC+8）：
- `organization.timezone: Asia/Singapore`（`:649`）
- `n8n.settings.timezone: Asia/Singapore`（`:666`）

但 n8n workflow JSON 文件的 `settings.timezone` 字段实际均写入 `Asia/Dubai`（GST，UTC+4）：
- `WF-02.json:147`
- `WF-06.json:285`
- `WF-08.json:226`

两者相差 4 小时。当 n8n scheduleTrigger 按 Dubai 时间触发时，日志和监控中的时间戳语义混乱。公司实际运营时区为 Dubai（与 n8n 实际配置一致），因此应以 Dubai 为准统一。

**预期行为**

1. `config.yaml` 中 `organization.timezone` 和 `n8n.settings.timezone` 均更新为 `Asia/Dubai`。
2. 所有 n8n workflow JSON 文件的 `settings.timezone` 保持 `Asia/Dubai`（已正确，无需修改）。
3. 代码中任何依赖 `config.yaml` 时区字段的逻辑（如日志时间戳生成）均改用 `Asia/Dubai`。

**验收标准（AC）**

- AC1：`config.yaml` 文件中，全局搜索 `Asia/Singapore`，结果为 0 条匹配。
- AC2：所有 n8n WF JSON 文件的 `settings.timezone` 字段值统一为 `Asia/Dubai`，通过脚本校验返回一致结果。
- AC3：pmo-api 的 Slack 通知消息中时间戳使用 Dubai 时间（UTC+4），在 Dubai 时区的设备上显示的时间与 Asana 任务完成时间误差 ≤ 5 分钟。

---

### 5.4 WF-06/WF-08 幂等共享（REQ-004，P2）

**背景问题描述**

V1.7.0 存在两条并行的任务完成通知路径：
- **主路径（WF-08）**：Asana Webhook → pmo-api → `notified_events` 表去重 → WF-08 发送 DM
- **兜底路径（WF-06）**：每 60 分钟轮询 → `staticData.notified`（内存 Set）本地去重 → 直接发送 DM

两条路径的去重机制相互独立。在 60 分钟窗口内，若 WF-08 已发送 DM，WF-06 的 `staticData.notified` 中无对应记录，仍会重复发送。源码注释（`WF-06.json:119`）明确标注 `TODO v1.7 共享幂等：调 pmo-api 去重后再发`，V1.7.0 未实现。

**预期行为**

1. WF-06 的 Code 节点在发送 DM 前，先调用 pmo-api `GET /webhooks/asana/health` 或新增的 `GET /events/notified?task_gid={gid}` 端点，查询该任务的 `event_key` 是否已在 `notified_events` 表中存在且 `status='forwarded'`。
2. 若已转发，WF-06 跳过该任务的 DM 发送，记录 `SKIP: already notified via WF-08`。
3. 若未转发（WF-08 未能处理），WF-06 正常发送 DM 并将通知结果写入统一的去重记录（或调用 pmo-api 接口登记）。

**验收标准（AC）**

- AC1：在 STD-TEST 项目中完成一个任务，确认 WF-08 成功发送 DM（日志 `accepted=1, notified=1`），60 分钟后 WF-06 运行时，该任务的 DM 不被重复发送（WF-06 日志显示 `SKIP: already notified via WF-08`）。
- AC2：模拟 WF-08 转发失败（停止 pmo-api 转发），60 分钟后 WF-06 检测到 `notified_events` 中该 event_key 无 `forwarded` 状态，自动补发 DM，PM 收到通知。
- AC3：通过 `GET /webhooks/asana/health` 端点返回的统计中，`duplicates_prevented` 指标在测试后大于 0，证明共享幂等机制生效。

---

### 5.5 WBS L3/L4 前置任务字段（REQ-002，P2）

**背景问题描述**

`wbs_to_asana.py` 的 `wire_dependencies` 函数（`:1135+`）通过读取 WBS DB 中每行的 `前置依赖` 字段（rich_text，逗号分隔 WBS 编码）来建立 Asana 任务依赖链。当依赖链建立后，WF-08 可在上游任务完成时通知下游 PM。

问题在于：Notion WBS 模板中，L3 和 L4 层级的行实际上未填写 `前置依赖` 字段（`wbs_to_asana.py:405` 虽有代码读取，但数据层面为空）。这意味着子任务级别的依赖关系无法通过 WF-08 触发，PM 只能在父任务层面收到通知，粒度不足。

**预期行为**

1. Notion WBS DB 的数据模板增加 L3/L4 层级前置依赖填写规范文档，指导 PMO 工程师正确填写。
2. 为保障向后兼容，`wbs_to_asana.py` 增加对 L3/L4 `前置依赖` 字段的覆盖率统计日志（coverage 当前已有 `wire_dependencies` 的 `<80% 记告警` 逻辑），L3/L4 覆盖率单独输出。
3. 对于历史存量项目（`前置依赖` 为空的 L3/L4 任务），提供可选的补跑脚本，通过父任务的 WBS 编码推断子任务依赖关系并补齐。

**验收标准（AC）**

- AC1：在新建测试项目的 Notion WBS DB 中，为至少 3 个 L3 任务填写 `前置依赖` 字段，执行 `wbs_to_asana.py` 后，对应 Asana 子任务之间的 `dependencies` 关系成功建立（通过 `GET /tasks/{gid}?opt_fields=dependencies` 验证）。
- AC2：`wbs_to_asana.py` 执行日志中出现 `L3/L4 dependency coverage: X%` 统计行，当 L3/L4 `前置依赖` 字段全部为空时，coverage 显示 `0%` 且触发 WARN 日志。
- AC3：完成带有 L3 前置依赖的 Asana 子任务后，依赖该任务的另一个 L3 子任务对应的 PM 在 60 秒内收到 Slack DM（通过 WF-08 Webhook 路径）。

---

### 5.6 其他需求（简述）

**REQ-006：服务器部署 git clone 化（P3）**

将当前手动 rsync 部署方式迁移为 git clone + pull 方式，配合 `.env` 文件管理凭证，降低部署漏文件风险。属于运维改进，不影响功能，列入 V2.1 规划。

**技术债务清理（V2.0 GA 内完成，不单独立需求）**
- 删除 WF-01 空节点 `update-registry-asana-gid`（差异5）
- 更新 WF-06 注释与实现一致（差异6）
- WF-05 凭证读取方式改为 `$env` 与 WF-08 统一（差异4）
- 补充 `migrations/001_*.sql`、`002_*.sql` 文件或重命名为 `001_*`（差异15）
- `config.yaml` 清理已 archive 的 charter DB 键注释（差异配置项）

---

## 6. 非功能需求

### 6.1 性能

| 指标 | 要求 |
|------|------|
| Webhook 端到端延迟 | Asana 任务完成 → PM 收到 Slack DM ≤ 60 秒（P99） |
| 批量 Webhook 注册吞吐 | 支持一次性注册 ≥ 50 个项目，总执行时间 ≤ 10 分钟 |
| pmo-api 响应时间 | `POST /webhooks/asana` 接受事件并返回 200 ≤ 500ms |
| WF-08 forward 超时 | 保持当前 `WF08_FORWARD_TIMEOUT=5s`，超时写入 outbox 重试 |

### 6.2 安全

| 要求 | 描述 |
|------|------|
| 凭证管理 | 所有 n8n workflow 凭证通过 `$env` 读取，禁止明文硬编码 |
| Webhook 验签 | 保持 HMAC-SHA256 常量时间比较（已实现，不降级） |
| 凭证存储 | `config.yaml` 的 `secrets.*` 区域移出仓库，通过部署时环境注入 |
| 审计日志 | pmo-api 的 `notified_events` 表保留 ≥ 30 天记录 |

### 6.3 可维护性

| 要求 | 描述 |
|------|------|
| 配置一致性 | `config.yaml` 中的时区/凭证/端点配置与 n8n workflow 实际使用保持同步 |
| 注释准确性 | 代码注释与实现一致，删除过时声明（如 WF-06 "v1.5.6 已移除" 注释） |
| 冗余节点清理 | 删除或明确标注历史遗留 pass-through 节点（WF-01 空节点、WF-05 expand-tasks） |
| 部署文档 | V2.0 发布时提供新实例部署检查清单，包含 n8n 凭证绑定、环境变量配置、WF-02 激活步骤 |

---

## 7. 交付里程碑

> 注：按阶段顺序排列，不标注时间，AI团队具备当日完成大部分工作的能力。

### V2.0 Beta 范围（完成 P1 需求）

- REQ-001：全量 Asana Webhook 注册脚本/工作流开发与测试
- 批量注册 E2E 验证（选取 3+ 个非 STD-TEST 项目进行验证）
- Beta 阶段 AC 验收（integration_qa 执行）

**Beta 准入门禁**：
- 北极星指标基线测量（记录 V1.7.0 当前实时率）
- REQ-001 AC1/AC2/AC3 全部通过

### V2.0 GA 范围（Beta 后完成 P2 需求）

- REQ-005：WF-06 凭证安全化
- REQ-002：WBS L3/L4 前置依赖字段规范 + 工具支持
- REQ-003：时区统一化配置变更
- REQ-004：WF-06/WF-08 幂等共享改造
- 技术债务清理（5项）
- GA 阶段 E2E 测试（qa_engineer 执行）

**GA 准入门禁**：
- 所有 P1+P2 需求 AC 全部通过
- RICE 评分 ≥ 1.87 的所有需求覆盖率 100%
- 安全扫描：WF-06、config.yaml 中无凭证明文残留
- 北极星指标实测值 ≥ 90%（接近目标 95%，GA 后持续优化）

**GA 总裁大版本验收**（L4 决策节点）：
- 产品委员会提交验收报告
- 北极星指标实测数据
- 所有已知差异处理状态（已修复/已知豁免/后续规划）

### V2.1 后续规划（P3 需求）

- REQ-006：git clone 化部署
- 监控面板：Webhook 注册状态可视化（项目注册覆盖率实时显示）
- 告警机制：未注册 Webhook 的项目自动告警（超过阈值通知 PMO 工程师）

---

## 8. 已知风险与假设

### 8.1 基于源码差异识别的风险

| 风险 | 来源 | 影响 | 缓解措施 |
|------|------|------|---------|
| WF-02 生产环境未激活 | 差异8：`active=false` | 等待导入的项目永不被处理 | V2.0 GA 部署检查清单中明确"激活 WF-02"步骤 |
| WF-01 凭证 id 空字符串 | 差异13：多节点空 credentials | 新实例导入后无法运行 WF-01 | 提供 WF-01 凭证重绑定操作手册 |
| Webhook 握手依赖 pmo-api 公网可达 | 架构设计 | pmo-api 内网部署时 Asana 无法回调 | 确认 pmo-api（端口8088）通过 Nginx 反向代理暴露公网 |
| 全量注册后 Asana Webhook 配额 | API 限制 | Asana 每工作区 Webhook 数量上限未知 | 注册前查询 `GET /webhooks` 确认当前配额，分批注册 |
| WF-06 兜底在全量 Webhook 后的必要性 | 架构设计 | Webhook 丢失时无兜底 | V2.0 保留 WF-06（60min 兜底），不降级为禁用 |

### 8.2 部署环境假设

| 假设项 | 详情 |
|--------|------|
| **Web 服务器** | Nginx 反向代理，pmo-api 通过 `https://pmo-api.lysander.bond`（或类似域名）公网可达 |
| **Docker 部署** | pmo-api 以 Docker 容器方式运行，环境变量通过 `docker run -e` 或 `.env` 文件注入 |
| **n8n 自托管** | n8n 实例运行于 `https://n8n.lysander.bond`（当前已验证），时区为 `Asia/Dubai` |
| **SQLite WAL 模式** | pmo-api 使用 SQLite WAL 模式（已实现），生产环境 I/O 满足并发 Webhook 处理需求 |
| **Asana 团队 GID** | 所有项目均属于同一 Asana 团队（`1213938170960375`），全量注册以该团队为边界 |
| **Slack Bot 权限** | Bot 具备 `users:read.email`、`chat:write` 权限（已在 V1.7.0 验证） |
| **凭证安全分层** | pmo-api config.yaml 凭证安全性依赖服务器文件权限（chmod 600）控制，n8n 平台使用内置 Credentials Store 管理 WF 侧凭证（加密存储，不暴露于进程环境） |

---

## 9. 验收清单

**产品委员会最终验收标准（checklist 格式）**

本清单由 `integration_qa`（Beta 阶段）和 `qa_engineer`（GA 阶段）在每个质量门禁节点核查。大版本 GA 前由 `synapse_product_owner` 汇总提交 Lysander 审核，Lysander 确认无阻断项后提交总裁大版本验收。

### PRD 评审门禁（当前阶段）

- [ ] PRD 结构完整，包含 9 个章节
- [ ] 所有需求来源均可追溯到 `09-system-spec-v170-verified.md` 或 `requirements_pool.yaml`
- [ ] RICE 评分已填写，优先级分级逻辑清晰
- [ ] 每个功能规格包含 3 条可测试的 AC
- [ ] 北极星指标已定义，包含当前基线值和目标值
- [ ] 技术债务清理项均已列出，不遗漏

### V2.0 Beta 门禁

- [ ] REQ-001 AC1：批量注册后活跃订阅数等于非 archived 项目数（±1）
- [ ] REQ-001 AC2：新建项目的 PM 在任务完成后 ≤ 60 秒收到 Slack DM
- [ ] REQ-001 AC3：重复注册幂等验证通过，日志显示 SKIP 记录
- [ ] pmo-api `GET /webhooks/asana/health` 返回正常，活跃订阅数与 AC1 一致
- [ ] Beta 阶段无 P0 阻断性缺陷

### V2.0 GA 门禁

- [ ] REQ-005 AC1：WF-06 JSON 中无凭证明文字符串残留（`2/1213400756695149`、`xoxb-` 全局搜索为0）
- [ ] REQ-005 AC2：通过 `$env` 读取凭证，WF-06 正常运行
- [ ] REQ-005 AC3：缺失环境变量时抛出明确错误
- [ ] REQ-002 AC1：L3 前置依赖字段建立 Asana 依赖关系成功
- [ ] REQ-002 AC2：日志输出 L3/L4 coverage 统计
- [ ] REQ-002 AC3：L3 任务完成触发 WF-08 PM 通知 ≤ 60 秒
- [ ] REQ-003 AC1：config.yaml 无 `Asia/Singapore` 残留
- [ ] REQ-003 AC2：所有 WF JSON timezone 统一为 `Asia/Dubai`
- [ ] REQ-003 AC3：Slack 通知时间戳为 Dubai 时间
- [ ] REQ-004 AC1：重复通知场景下 WF-06 显示 SKIP 日志
- [ ] REQ-004 AC2：WF-08 失败时 WF-06 自动补发 DM
- [ ] REQ-004 AC3：health 端点 `duplicates_prevented` > 0
- [ ] 技术债务：WF-01 空节点已删除
- [ ] 技术债务：WF-06 注释与实现一致
- [ ] 技术债务：WF-05 凭证改为 `$env` 方式
- [ ] 北极星指标实测值 ≥ 90%
- [ ] GA 阶段无 P1 未关闭缺陷，P2 缺陷均有明确跟进计划
- [ ] 部署文档已更新，包含 V2.0 新增步骤

### 总裁大版本验收门禁（L4）

- [ ] 产品委员会验收报告提交（含 QA 评分、北极星指标实测、差异处理状态）
- [ ] 北极星指标达标：通知实时率 ≥ 90%（目标 95%，GA 后持续优化）
- [ ] 无未修复的安全漏洞（凭证明文）
- [ ] Lysander 确认无阻断项，完成 L3 签发
- [ ] 总裁验收确认，V2.0 正式发布

---

*文档结束*

*编制：synapse_product_owner | 审查：Lysander CEO | 基准：V1.7.0（commit 106532a，2026-04-22）*
