# ⚙️ WF-02 / WF-03 工作流设计规格 + WF-07修复方案

> **Page ID:** 33d3e99820c781ba92abfe636cf95f04
> **Parent:** 📊 PMO自动化管理体系

---

> 本文档包含完整的n8n工作流设计，可在登录n8n后直接按照配置。
> n8n管理台：[https://n8n.lysander.bond](https://n8n.lysander.bond)

---

## WF-02 任务状态变更通知

### 功能说明
当 Asana 中某个任务被标记为完成时，自动向责任 PM 发送 Slack 通知。

### n8n 节点配置

**Node 1: Asana Trigger**
- 类型: `Asana Trigger`
- Resource: `Task`
- Events: `task.completed`
- Team ID: `1213938170960375`

**Node 2: IF 过滤**
- 类型: `IF`
- 条件: `{{ $json.type }}` equals `task`
- 过滤掉非任务事件

**Node 3: Asana Get Task**
- 类型: `Asana`
- Operation: `Get`
- Resource: `Task`
- Task ID: `{{ $json.resource.gid }}`
- Opt Fields: `name,assignee,projects,completed_at,custom_fields`

**Node 4: Code 解析任务信息**
```javascript
const task = $input.item.json;
const projectName = task.projects?.[0]?.name || '未分配项目';
const assigneeName = task.assignee?.name || '未分配';
const taskName = task.name || '';
const completedAt = task.completed_at ? new Date(task.completed_at).toLocaleDateString('zh-CN') : '未知';

return [{
  json: {
    taskName,
    projectName,
    assigneeName,
    completedAt,
    taskUrl: `https://app.asana.com/0/${task.projects?.[0]?.gid}/${task.gid}`,
    slackMessage: `✅ *任务完成*\n*任务*: ${taskName}\n*所属项目*: ${projectName}\n*完成时间*: ${completedAt}\n*责任人*: ${assigneeName}`
  }
}];
```

**Node 5: Slack Send Message**
- 类型: `Slack`
- Operation: `Send Message`
- Channel: `#project-updates`（或指定PM的DM）
- Message: `{{ $json.slackMessage }}`

### 连接顺序
```
Asana Trigger → IF → Asana Get Task → Code → Slack Send Message
```

---

## WF-03 里程碑提醒

### 功能说明
每天早上 09:00 扫描未来 3 天内将到期的任务（标准：任务名称含"里程碑"或打了里程碑标签），向 PM 发送 Slack 提醒。

### n8n 节点配置

**Node 1: Schedule Trigger**
- 类型: `Schedule Trigger`
- Cron: `0 9 * * *`（每日 09:00）
- Timezone: `Asia/Dubai`

**Node 2: Code 计算日期范围**
```javascript
const now = new Date();
const in3Days = new Date(now);
in3Days.setDate(now.getDate() + 3);

return [{
  json: {
    today: now.toISOString().split('T')[0],
    deadline: in3Days.toISOString().split('T')[0]
  }
}];
```

**Node 3: Asana Get Tasks**
- 类型: `Asana`
- Operation: `Get Many`
- Resource: `Task`
- Workspace: `你的Workspace GID`
- Additional Fields:
  - `due_on.before`: `{{ $json.deadline }}`
  - `due_on.after`: `{{ $json.today }}`
  - `completed`: `false`
  - `opt_fields`: `name,due_on,assignee,projects`

**Node 4: Code 过滤里程碑任务**
```javascript
const tasks = $input.all();
const milestones = tasks
  .map(t => t.json)
  .filter(t => 
    t.name?.includes('里程碑') || 
    t.name?.includes('milestone') ||
    t.name?.includes('M') && /M\d{2}/.test(t.name)
  );

if (milestones.length === 0) {
  return [{ json: { skip: true, message: '无即将到来的里程碑' } }];
}

const today = new Date().toISOString().split('T')[0];
let message = `🚨 *里程碑提醒*（未来3天内）\n`;

milestones.forEach(m => {
  const project = m.projects?.[0]?.name || '未分配';
  const assignee = m.assignee?.name || '-';
  const daysLeft = Math.ceil((new Date(m.due_on) - new Date(today)) / 86400000);
  const urgency = daysLeft === 0 ? '🔴 今天到期' : daysLeft === 1 ? '🟡 明天到期' : `🟢 ${daysLeft}天后`;
  message += `\n${urgency} *${m.name}*\n   └ 项目: ${project} | 责任: ${assignee} | 截止: ${m.due_on}`;
});

return [{ json: { skip: false, message, count: milestones.length } }];
```

**Node 5: IF 有里程碑？**
- 条件: `{{ $json.skip }}` equals `false`

**Node 6: Slack Send Message**
- Channel: 你的Slack DM或#pmo-alerts
- Message: `{{ $json.message }}`

### 连接顺序
```
Schedule Trigger → Code 日期 → Asana Get Tasks → Code 过滤 → IF → Slack
```

---

## WF-07 行动项归属修复

### 问题描述
当前WF-07在Asana创建行动项时，没有关联 `projects` 字段，导致创建的任务是"孤儿"状态。

### 修复方案
在WF-07 的 **创建 Asana 任务** 节点之前，添加以下逻辑节点：

**新增 Node X: 查询Notion项目注册表**
- 类型: `HTTP Request`
- Method: `POST`
- URL: `https://api.notion.com/v1/databases/33c3e99820c781fcac6fc8a54e6e8ad6/query`
- Headers:
  - `Authorization`: `Bearer {{$credentials.notionApi.key}}`
  - `Notion-Version`: `2022-06-28`
- Body:
```json
{
  "filter": {
    "property": "状态",
    "select": { "equals": "交付中" }
  }
}
```

**新增 Node X+1: Code 匹配项目**
```javascript
// 获取会议标题（从上游Fireflies节点传入）
const meetingTitle = $('Fireflies 获取会议').first().json.title || '';

// 获取Notion中的交付中项目
const notionProjects = $input.first().json.results || [];

let matchedAsanaGid = null;
let matchedProjectName = '未匹配';

for (const project of notionProjects) {
  const projectName = project.properties['项目名称']?.title?.[0]?.plain_text || '';
  const asanaLink = project.properties['交付Asana项目链接']?.url || '';
  const clientName = project.properties['客户名称']?.rich_text?.[0]?.plain_text || '';
  
  // 匹配逻辑：会议标题含项目名或客户名
  if (meetingTitle.includes(projectName) || meetingTitle.includes(clientName)) {
    // 从 Asana URL 提取项目 GID
    const gidMatch = asanaLink.match(/\/0\/(\d+)/);
    if (gidMatch) {
      matchedAsanaGid = gidMatch[1];
      matchedProjectName = projectName;
      break;
    }
  }
}

return [{
  json: {
    matchedAsanaGid,
    matchedProjectName,
    meetingTitle
  }
}];
```

**修改 创建Asana Task 节点**
在现有 Asana Create Task 节点的 Additional Fields 中，添加：
- `projects`: `{{ $json.matchedAsanaGid ? [$json.matchedAsanaGid] : [] }}`

### 修复后效果
- 当会议标题包含已知项目名称时：行动项自动归属该项目
- 当无法匹配时：行动项建入默认收件笺（保持现状）

---

*设计日期: 2026-04-09 | 执行人: 登录 n8n 后按照此文档配置*
