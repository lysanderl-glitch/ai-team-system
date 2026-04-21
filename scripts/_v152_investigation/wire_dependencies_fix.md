# v1.5.2 wire_dependencies 根因分析 + 修复草稿

**调查者**：ai_systems_dev（子 Agent）
**日期**：2026-04-19（总裁当前日期 2026-04-19，事件 0423 即 04-19 跑的 E2E）
**活跃源**：`ai-team-system/scripts/wbs_to_asana.py`
**状态**：仅分析 + 草稿修复，不落盘活跃文件

---

## 0. 调查约束（必须先声明）

- `.env` 不存在于仓库根，`obs/credentials.mdenc` 为加密凭证，子 Agent 当前无用户密码
- 未找到任何 `wbs_run_*.log`（仅 `wbs_run_output.txt` 0 字节空文件）
- 未找到 `_0422_dep_backfill.py`（推测在仓库外或已清理）
- 未找到 `_post_step_errors_*.json` 落盘文件
- **因此 Step 3/6 的 Notion/Asana 实时查询和运行时补偿本轮无法完成**，需总裁提供密码后再跑

本报告以**代码静态分析 + 已知数据结构**定位根因，修复草稿不落盘至活跃路径。

---

## 1. 代码阅读结论（Step 1）

### `wire_dependencies` 定义位置

- 文件：`scripts/wbs_to_asana.py`
- 函数签名：`def wire_dependencies(code_to_gid, rows, pat, dry_run=False)`（第 824 行）
- 入口日志：`"  [v1.5] entering wire_dependencies"`（第 829 行）
- 出口日志：`"  [v1.5] wire_dependencies done, deps_written={linked}, deps_defined={wbs_deps_defined}, coverage={coverage:.1%}"`（第 864 行）
- Coverage 告警：`<80%` 时追加 `[COVERAGE-ALERT]` 并 `_record_post_step_error("wire_dependencies_coverage", ...)`

### 输入参数

| 参数 | 构造方式 | 关键点 |
|------|----------|--------|
| `code_to_gid` | 在 main() Step 4 循环中按 `lvl` 分支累积（L2→L3→L4→Gate） | **L1 被显式 `continue` 跳过，L1 不写入 map**（第 1034-1036 行） |
| `rows` | 来自 `read_wbs_from_notion(notion_token)` 的全量记录 | 未按 `registry_id` 过滤 |
| `pat` | Asana PAT | — |

### `前置依赖` 字段读取路径

```python
pred = _get_text(props, "前置依赖") or ""   # 第 405 行
```

`_get_text`（第 338 行）：读取 `rich_text` 类型的 `plain_text` 拼接。
**意味着**：若 Notion 中 `前置依赖` 字段类型为 **relation / multi_select / formula / rollup / title**（非 `rich_text`），则 `_get_text` 返回**空字符串**，下游 `parse_preds("")` 返回 `[]`，**0 条依赖**。

### `parse_preds` 逻辑（第 460 行）

```python
def parse_preds(pred_str):
    if not pred_str or str(pred_str).strip() in ("起点，无前置依赖", ""):
        return []
    return [p.strip() for p in str(pred_str).replace("，", ",").split(",") if p.strip()]
```

中文全角 `，` 已兼容。但**全角句号 `。` 或中文顿号 `、` 不兼容**，若 WBS 定义用这些分隔符，解析失败 → 匹配不到 code。

### 调用点

```
main()
 └─ Step 4（第 1027-1098）ThreadPoolExecutor 提交 CF futures（L3/L4 subtask _attach_subtask_cf）
 └─ pre-Step5: _wait_all_cf_futures(label="pre-Step5")  ← 第 1104
 └─ Step 5: wire_dependencies(code_to_gid, rows, pat, dry)  ← 第 1112
```

**顺序正确**：`wire_dependencies` 在 CF futures join 之后跑。v1.5.1 的 `_wait_all_cf_futures` 在第 1104 行，和设计一致。**这条顺序不是 0 依赖的根因**。

---

## 2. 日志分析（Step 2，受限）

**日志文件不存在**，仅 `wbs_run_output.txt` 空文件。无法直接验证是否：
- 打印了 `[v1.5] entering wire_dependencies` → 证明函数确实被调用
- 打印了 `deps_defined=0` → 证明 rows 中所有行的 `pred` 都被识别为空
- 打印了 `deps_defined=N, linked=0` → 证明依赖被识别但 addDependencies API 全部失败
- 打印了 `[COVERAGE-ALERT]` 或 `[WARN] 依赖失败` → 若有，可直接看到 Asana 端报错

**建议**：总裁下次 E2E 时用 `python wbs_to_asana.py ... 2>&1 | tee wbs_run_YYYYMMDD_HHMMSS.log`。v1.5.2 加日志路径强制参数。

---

## 3. Notion 数据对比（Step 3，受限）

无凭证，无法 query。但根据 `_migration/wbs_records.json` 旧快照可见 WBS DB 原始 schema：

```json
{"WBS编码": "S-D", "任务名称": "合同签署及立项", "前置依赖": "", ...}
```

旧快照 `前置依赖` 字段是**字符串**（推测 rich_text），但：
1. 旧快照每行**没有 `项目` 或 `registry_id` 字段**，说明 WBS DB 在 0423 之前一次迁移**新增了项目关联字段**
2. 新增字段若用了 **relation 类型**（指向项目注册表），则 `read_wbs_from_notion` 的**全量 query 会混入所有项目的 WBS 行**（0423 + 0422 + 之前）
3. 这会导致 `code` 冲突：多个项目共用同一批 WBS 模板（DA001/DS001...），`code_to_gid` 会被后写入的 gid 覆盖；`rows` 中同一 code 出现多次，`wire_dependencies` 的 `task_gid = code_to_gid[task_code]` 拿到最后一个项目的 gid → 跨项目 addDependencies 要么 403/400，要么静默失败

---

## 4. 根因 3 候选 + 概率排序（Step 4）

### 候选 A：`read_wbs_from_notion` 未按项目过滤（概率 55%）

**证据**：
- `notion_query_database(NOTION_WBS_DB_ID, notion_token)` 调用无 `filter_body`（第 392 行）
- 主流程也没有把 `project_registry_id` / `start_date` 之外的项目标识传给 `read_wbs_from_notion`
- 0422 首跑 + 0423 首跑都是 0 条依赖 → 说明 bug 是**稳定复现的结构性问题**，不是偶发

**后果**：
- rows 包含历史所有项目的 WBS 行
- 在 Step 4 的 `code_to_gid` 循环中，相同 `code` 会被**后写入的 gid 覆盖**
- `wire_dependencies` 中 `dep_gids = [code_to_gid[p] for p in preds]` 拿到的是**其他项目的 task gid**
- Asana `addDependencies` 跨项目依赖要么被拒（403），要么 silently succeed 到错误 task
- 但更致命：**Step 4 创建 L2 时，`code == "DA001"` 可能碰到 rows 最后一条"DA001"是其他项目的配置**，这条创建成功后 `code_to_gid["DA001"]` 固定；后续依赖建立时所有 preds 都指向"最后一条创建的"，**可能 preds 自引用自己 → 被 `p != task_code` 过滤掉 → linked=0**

此候选也解释了为何 0422 手工补的 89 条能成功：手工补用的是正确的 0422 项目内 gid map。

### 候选 B：`前置依赖` 字段类型已变更（relation / rollup / formula）（概率 30%）

**证据**：
- Notion WBS DB 在 0422 之前一次迁移若把 `前置依赖` 从 rich_text 改为 **relation**（关联同库前置 task），`_get_text` 返回空
- 或改为 **formula**（从 relation 动态生成逗号串），`_get_text` 也会返回空（formula 需 `_get_formula_plain`）
- 这能解释"0422 0423 首跑都是 0"——不是某次事件性问题，而是字段类型不匹配
- `wire_dependencies` 入口日志出现 but `deps_defined == 0` → 所有 rows `parse_preds` 返回 []

此候选需总裁提供凭证后 query 一条 0423 行的 raw JSON 即可确认（查 `properties["前置依赖"]["type"]`）。

### 候选 C：rows 中 pred 用中文分隔符（、；。）/ 多余空白导致 parse_preds 识别失败（概率 15%）

**证据**：
- `parse_preds` 只兼容半角 `,` 和全角 `，`
- 若总裁或模板工具把 "DA001、DA002" 写成顿号分隔，`split(",")` 拿到 `["DA001、DA002"]`，`p in in_scope` 永远失败
- 但 0422 手工补回 89 条成功说明"依赖关系本身是已知的"→ 总裁手工补时用的是 WBS 模板标准化过的编码串，可能并不经过 parse_preds
- 该候选概率较低，但**建议 v1.5.2 的 parse_preds 扩展分隔符兼容**（几乎零成本）

### 概率排序

| 排名 | 候选 | 概率 | 一句话诊断 |
|------|------|------|-----------|
| 1 | A. 缺项目过滤 | 55% | `read_wbs_from_notion` 未过滤 registry_id，code_to_gid 跨项目污染 |
| 2 | B. 字段类型变更 | 30% | `前置依赖` 可能不再是 rich_text，`_get_text` 空返回 |
| 3 | C. 分隔符不兼容 | 15% | 顿号/句号等非标分隔符导致 parse_preds 失败 |

---

## 5. v1.5.2 修复草稿（不落盘活跃路径）

### Patch 1：`read_wbs_from_notion` 增加 `registry_id` 过滤参数

```diff
--- a/scripts/wbs_to_asana.py
+++ b/scripts/wbs_to_asana.py
@@
-def read_wbs_from_notion(notion_token):
+def read_wbs_from_notion(notion_token, registry_id: str | None = None,
+                         project_field_name: str = "项目"):
     """
     从 Notion WBS工序数据库读取所有工序，返回结构化行列表。
+
+    [v1.5.2] 若提供 registry_id（项目注册表 page id），追加 relation filter
+    确保只读取本项目的 WBS 行。未提供时保持 v1.5.1 行为（全量，但打 WARN 日志）。
     """
     print(f"  正在查询 Notion 数据库 {NOTION_WBS_DB_ID} ...")
-    pages = notion_query_database(NOTION_WBS_DB_ID, notion_token)
+    filter_body = None
+    if registry_id:
+        filter_body = {
+            "property": project_field_name,
+            "relation": {"contains": registry_id},
+        }
+        print(f"  [v1.5.2] 按项目过滤 registry_id={registry_id}")
+    else:
+        print(f"  [v1.5.2][WARN] 未传 registry_id，全量读取（可能跨项目污染）")
+    pages = notion_query_database(NOTION_WBS_DB_ID, notion_token, filter_body=filter_body)
     print(f"  共获取 {len(pages)} 条记录")
```

`main()` 对应修改：从 CLI 新增 `--registry-id`，透传下去。

### Patch 2：`parse_preds` 放宽分隔符

```diff
 def parse_preds(pred_str):
     if not pred_str or str(pred_str).strip() in ("起点，无前置依赖", ""):
         return []
-    return [p.strip() for p in str(pred_str).replace("，", ",").split(",") if p.strip()]
+    # [v1.5.2] 兼容中文分隔符：逗号（全/半角）、顿号、分号（全/半角）
+    s = str(pred_str)
+    for ch in ("，", "、", "；", ";"):
+        s = s.replace(ch, ",")
+    return [p.strip() for p in s.split(",") if p.strip()]
```

### Patch 3：`_get_text` 兼容 relation/formula 类型（防御性）

```diff
 def _get_text(props, key):
-    """提取 rich_text 类型字段的纯文本"""
-    items = props.get(key, {}).get("rich_text", [])
-    return "".join(t.get("plain_text", "") for t in items).strip()
+    """提取文本（rich_text/formula/rollup/title），兼容字段类型变更"""
+    fld = props.get(key, {})
+    # rich_text
+    if fld.get("rich_text"):
+        return "".join(t.get("plain_text", "") for t in fld["rich_text"]).strip()
+    # formula.string
+    f = fld.get("formula", {})
+    if f and f.get("type") == "string":
+        return (f.get("string") or "").strip()
+    # rollup.array → 拼接 plain_text
+    r = fld.get("rollup", {})
+    if r and r.get("type") == "array":
+        out = []
+        for it in r.get("array", []):
+            if it.get("type") == "rich_text":
+                out.append("".join(t.get("plain_text","") for t in it.get("rich_text",[])))
+            elif it.get("type") == "title":
+                out.append("".join(t.get("plain_text","") for t in it.get("title",[])))
+        return ",".join(x for x in out if x).strip()
+    return ""
```

### Patch 4：`wire_dependencies` 入口打印 sample 便于下次排障

```diff
 def wire_dependencies(code_to_gid, rows, pat, dry_run=False):
     print("  [v1.5] entering wire_dependencies")
+    # [v1.5.2] 入口打印统计样本，便于日志排障
+    _non_empty_pred = [r for r in rows if (r.get("pred") or "").strip()]
+    print(f"  [v1.5.2] rows_with_pred={len(_non_empty_pred)}/{len(rows)} "
+          f"code_to_gid_size={len(code_to_gid)}")
+    for _r in _non_empty_pred[:3]:
+        print(f"  [v1.5.2][sample] code={_r.get('code')} pred={_r.get('pred')!r}")
     in_scope = set(code_to_gid.keys())
```

### Patch 5：日志强制落盘

在 `main()` 开头加 `--log-file` 可选参数 + `tee`-like 包装，或至少打印 `sys.argv` + `datetime.now()` 头部，便于 grep。

---

## 6. Step 6：运行时补偿（阻塞）

**无法执行**。需要总裁提供 `obs/credentials.md` 的解密密码以拿到 `ASANA_PAT` + `NOTION_TOKEN`。

**脚本骨架已预留**（未创建文件，等解锁后再生成）：

```python
# _0423_dep_backfill.py（待创建）
import os, sys, requests
from dotenv import load_dotenv
load_dotenv()
ASANA_PAT = os.environ["ASANA_PAT"]
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
PROJECT_GID = "1214145351020337"  # 0423 Asana
NOTION_WBS = "bd3c845d85a149daaa5c0a273a811106"
REGISTRY_ID = "347114fc-090c-80d1-b2ea-ee6c279e01f7"  # 0423

# 1) Notion query（带 relation filter=REGISTRY_ID）→ 得到 (code, pred) 列表
# 2) Asana GET /projects/{PROJECT_GID}/tasks?opt_fields=gid,name,custom_fields.name,custom_fields.text_value
#    子任务：递归 GET /tasks/{gid}/subtasks 直到 L4
# 3) 用任务名前缀 "[CODE]" 或 "任务编码" CF 构建 code_to_gid
# 4) 遍历 pred 行，POST /tasks/{gid}/addDependencies（幂等：先 GET dependencies 去重）
```

---

## 7. 推荐总裁交付路径

1. **立即**：提供凭证密码给子 Agent，执行 Step 3（query Notion 0423 样本 10 条 raw JSON）+ Step 6（运行时补 0423 依赖）
2. **短期**（今日内）：v1.5.2 合入 Patch 1+2+3+4，写入 `wbs_to_asana.py.bak_before_v152_*` 备份后落盘
3. **中期**：wbs_trigger 对所有 `[COVERAGE-ALERT]` 事件自动退火为 `STATUS_PARTIAL` 而非 `已完成`

---

**END**
