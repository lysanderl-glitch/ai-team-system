#!/usr/bin/env python3
"""
SPE SessionEnd Hook — 会话结束自动任务捕获
在 Claude Code 会话关闭时触发，从对话记录中提取行动项。

工作原理：
1. 从 stdin 获取 JSON 输入（包含 transcript_path、session_id 等）
2. 读取对话记录（JSONL 格式）
3. 用关键词匹配提取行动项（不调用 API，轻量快速）
4. 写入 personal_tasks.yaml 的 inbox
5. 如在 git repo 中，自动 commit
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================================
# 配置
# ============================================================================

# personal_tasks.yaml 的路径（相对于本脚本所在的 repo 根目录）
PERSONAL_TASKS_REL = "agent-butler/config/personal_tasks.yaml"

# 关键词匹配规则
CHINESE_KEYWORDS = [
    r"需要",
    r"记一下",
    r"回头",
    r"待办",
    r"后续",
    r"跟进",
    r"别忘了",
    r"提醒我",
]

ENGLISH_KEYWORDS = [
    r"TODO",
    r"action item",
    r"follow up",
    r"remind me",
    r"need to",
]

# 任务模式：以 "- [ ]" 开头的行
TASK_CHECKBOX_PATTERN = re.compile(r"^\s*-\s*\[\s*\]\s*(.+)$", re.MULTILINE)

# 合并所有关键词为一个正则（捕获关键词所在的完整句子）
ALL_KEYWORDS = CHINESE_KEYWORDS + ENGLISH_KEYWORDS
KEYWORD_PATTERN = re.compile(
    r"[^。！？\.\!\?\n]*(?:" + "|".join(ALL_KEYWORDS) + r")[^。！？\.\!\?\n]*",
    re.IGNORECASE,
)

# 最大提取数量（防止误报过多）
MAX_ITEMS = 10

# 每条行动项最大字符数
MAX_ITEM_LENGTH = 200


# ============================================================================
# 核心函数
# ============================================================================


def get_repo_root() -> Path:
    """获取本脚本所在 git repo 的根目录。"""
    script_dir = Path(__file__).resolve().parent
    # 向上查找到包含 .git 的目录，或者回退到 ai-team-system 目录
    current = script_dir
    for _ in range(5):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    # Fallback: 假设 scripts/ 在 repo 根目录下
    return script_dir.parent


def read_stdin_input() -> dict:
    """从 stdin 读取 Claude Code hook 传入的 JSON 数据。"""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return {}


def parse_transcript(transcript_path: str) -> list[dict]:
    """
    解析 JSONL 格式的对话记录。
    只提取 user 和 assistant 的 message 文本内容。
    """
    messages = []
    path = Path(transcript_path)
    if not path.exists():
        return messages

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = entry.get("role", "")
            if role not in ("user", "assistant"):
                continue

            # 提取文本内容（content 可能是字符串或列表）
            content = entry.get("content", "")
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, str):
                        text_parts.append(part)
                content = "\n".join(text_parts)

            if content:
                messages.append({"role": role, "text": content})

    return messages


def extract_action_items(messages: list[dict]) -> list[str]:
    """
    从对话消息中提取行动项候选。
    返回去重后的字符串列表。
    """
    candidates = set()

    for msg in messages:
        text = msg["text"]

        # 1. 匹配 checkbox 任务
        for match in TASK_CHECKBOX_PATTERN.finditer(text):
            item = match.group(1).strip()
            if item and len(item) <= MAX_ITEM_LENGTH:
                candidates.add(item)

        # 2. 匹配关键词所在的句子
        # 只从 user 消息中提取关键词匹配（assistant 中的关键词可能是建议而非用户意图）
        if msg["role"] == "user":
            for match in KEYWORD_PATTERN.finditer(text):
                item = match.group(0).strip()
                # 清理前后多余的标点和空白
                item = re.sub(r"^[，,、：:\s]+", "", item)
                item = re.sub(r"[，,、：:\s]+$", "", item)
                if item and 4 <= len(item) <= MAX_ITEM_LENGTH:
                    candidates.add(item)

    # 限制数量
    result = sorted(candidates)[:MAX_ITEMS]
    return result


def load_existing_inbox(yaml_path: Path) -> list[str]:
    """
    简单解析 personal_tasks.yaml 中已有的 inbox items 的 content 字段。
    使用简单字符串匹配而非完整 YAML 解析（避免依赖 PyYAML）。
    """
    existing = []
    if not yaml_path.exists():
        return existing

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 简单提取 inbox items 中的 content 值
        # 匹配 content: "..." 或 content: '...' 或 content: ...
        in_inbox = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("inbox:"):
                in_inbox = True
                continue
            if in_inbox and not line.startswith(" ") and not line.startswith("\t") and stripped:
                # 退出 inbox 区域
                in_inbox = False
                continue
            if in_inbox and "content:" in stripped:
                # 提取 content 值
                val = stripped.split("content:", 1)[1].strip()
                # 去除引号
                val = val.strip("\"'")
                if val:
                    existing.append(val)
    except Exception:
        pass

    return existing


def deduplicate(candidates: list[str], existing: list[str]) -> list[str]:
    """
    去重：排除已存在于 inbox 中的项目。
    使用子串匹配（因为格式可能略有不同）。
    """
    new_items = []
    existing_lower = [e.lower() for e in existing]

    for item in candidates:
        item_lower = item.lower()
        # 检查是否已存在（完全匹配或子串包含）
        is_dup = False
        for ex in existing_lower:
            if item_lower in ex or ex in item_lower:
                is_dup = True
                break
        if not is_dup:
            new_items.append(item)

    return new_items


def append_to_yaml(yaml_path: Path, new_items: list[str], session_id: str) -> None:
    """
    将新行动项追加到 personal_tasks.yaml 的 inbox.items 中。
    使用字符串操作而非 YAML 库（避免格式改动）。
    """
    if not yaml_path.exists():
        return

    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 生成新的 inbox entries
    new_entries = []
    for i, item in enumerate(new_items, 1):
        seq = str(i).zfill(3)
        entry_id = f"CAP-{today}-{seq}"
        # 转义引号
        safe_content = item.replace('"', '\\"')
        entry = (
            f'  - id: "{entry_id}"\n'
            f'    content: "{safe_content}"\n'
            f'    source: "session_hook"\n'
            f'    captured_at: "{now}"\n'
            f'    status: "pending"\n'
            f'    session_id: "{session_id}"\n'
            f'    processed_to: ""'
        )
        new_entries.append(entry)

    if not new_entries:
        return

    entries_text = "\n".join(new_entries)

    # 找到 "items: []" 并替换为带内容的列表
    if "items: []" in content:
        content = content.replace(
            "items: []",
            "items:\n" + entries_text,
            1,
        )
    elif "items:" in content:
        # items 已有内容，在 items: 下的最后一个条目后追加
        # 找到 inbox > items 区域的末尾
        lines = content.split("\n")
        insert_idx = None
        in_items = False

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "items:" or stripped.startswith("items:"):
                if in_items or "inbox" in "\n".join(lines[max(0, idx - 5):idx]):
                    in_items = True
                    continue
            if in_items:
                # 在 items 列表内
                if stripped.startswith("- id:") or stripped.startswith("- content:"):
                    insert_idx = idx
                elif not stripped.startswith("-") and not stripped.startswith(" ") and stripped and not stripped.startswith("#"):
                    # 退出 items 区域
                    break
                elif stripped.startswith("- "):
                    insert_idx = idx

        if insert_idx is not None:
            # 找到最后一个条目块的末尾
            last_entry_end = insert_idx
            for idx in range(insert_idx + 1, len(lines)):
                stripped = lines[idx].strip()
                if stripped.startswith("- id:"):
                    break
                if not stripped or stripped.startswith(" ") or stripped.startswith("#"):
                    last_entry_end = idx
                else:
                    break

            lines.insert(last_entry_end + 1, entries_text)
            content = "\n".join(lines)
        else:
            # Fallback: 在 items: 后直接追加
            content = content.replace(
                "items:\n",
                "items:\n" + entries_text + "\n",
                1,
            )

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)


def git_commit(repo_root: Path, file_path: Path, item_count: int) -> None:
    """如果在 git repo 中，自动 commit 变更。"""
    try:
        # 检查是否是 git repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return

        # Stage the file
        rel_path = file_path.relative_to(repo_root)
        subprocess.run(
            ["git", "add", str(rel_path)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Commit
        msg = f"[SPE] SessionEnd hook: captured {item_count} action item(s)"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        pass  # Git 操作失败不应阻塞退出


# ============================================================================
# 主流程
# ============================================================================


def main():
    try:
        # 1. 读取 stdin 输入
        hook_input = read_stdin_input()
        transcript_path = hook_input.get("transcript_path", "")
        session_id = hook_input.get("session_id", "unknown")

        if not transcript_path:
            print("0")  # 没有 transcript，无法提取
            return

        # 2. 解析对话记录
        messages = parse_transcript(transcript_path)
        if not messages:
            print("0")
            return

        # 3. 提取行动项候选
        candidates = extract_action_items(messages)
        if not candidates:
            print("0")
            return

        # 4. 去重
        repo_root = get_repo_root()
        yaml_path = repo_root / PERSONAL_TASKS_REL
        existing = load_existing_inbox(yaml_path)
        new_items = deduplicate(candidates, existing)

        if not new_items:
            print("0")
            return

        # 5. 写入 personal_tasks.yaml
        append_to_yaml(yaml_path, new_items, session_id)

        # 6. Git commit
        git_commit(repo_root, yaml_path, len(new_items))

        # 7. 输出捕获数量
        print(str(len(new_items)))

    except Exception as e:
        # 任何错误不应阻塞 Claude Code 退出
        print(f"0", file=sys.stdout)
        print(f"[SessionEnd Hook Error] {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
