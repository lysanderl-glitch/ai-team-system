#!/usr/bin/env python3
"""
Credentials Manager — ai-team-system
支持读取 Obsidian Meld Encrypt (β 格式) 加密的凭证文件。

=== 使用方式 ===

  # 查看所有 Key 名（无需密码）
  python creds.py list

  # 获取单个凭证
  python creds.py get GITHUB_TOKEN
  python creds.py get GITHUB_TOKEN -p "你的密码"   ← AI 自动调用

  # 导出全部（供 AI 批量使用）
  python creds.py export
  python creds.py export -p "你的密码"

=== Obsidian 使用方式 ===
  1. 在 Obsidian 打开 credentials.md
  2. 命令面板 → "Meld Encrypt: Decrypt in-place" → 输入密码 → 可视化查看/编辑
  3. 编辑完成后 → "Meld Encrypt: Encrypt in-place" → 重新加密

=== 凭证文件格式 ===
  credentials.md 中加密的内容应为 JSON：
  {
    "GITHUB_TOKEN": "ghp_xxx",
    "NOTION_TOKEN": "ntn_xxx",
    "N8N_API_KEY": "eyJ...",
    ...
  }
"""

import os
import sys
import re
import json
import base64
import getpass
import argparse

# Meld Encrypt β 格式参数（来自插件源码 v2.4.5）
_MELD_BETA_PREFIX   = "%%\U0001f510\u03b2 "   # %%🔐β
_MELD_BETA_SUFFIX   = "%%"
_VECTOR_SIZE        = 16   # IV 长度（字节）
_SALT_SIZE          = 16   # Salt 长度（字节）
_ITERATIONS         = 210_000
_CREDENTIALS_FILE   = os.path.join(os.path.dirname(__file__), "obs", "credentials.md")


# ── 解密核心 ───────────────────────────────────────────────────────────────────

def _decrypt_meld_beta(b64_blob: str, password: str) -> str:
    """解密 Meld Encrypt β 格式的 base64 blob，返回明文字符串。"""
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    raw = base64.b64decode(b64_blob)
    iv        = raw[:_VECTOR_SIZE]
    salt      = raw[_VECTOR_SIZE:_VECTOR_SIZE + _SALT_SIZE]
    ciphertext = raw[_VECTOR_SIZE + _SALT_SIZE:]

    kdf = PBKDF2HMAC(algorithm=hashes.SHA512(), length=32, salt=salt, iterations=_ITERATIONS)
    key = kdf.derive(password.encode("utf-8"))
    plaintext = AESGCM(key).decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")


def _load_credentials(password: str) -> dict:
    """读取 credentials.md，解密并返回凭证字典。"""
    if not os.path.exists(_CREDENTIALS_FILE):
        print(f"❌ 找不到凭证文件：{_CREDENTIALS_FILE}", file=sys.stderr)
        print("   请先在 Obsidian 中创建并加密 credentials.md", file=sys.stderr)
        sys.exit(1)

    content = open(_CREDENTIALS_FILE, encoding="utf-8").read()

    # 提取 β 格式加密块
    pattern = re.escape(_MELD_BETA_PREFIX) + r"(.+?)" + re.escape(_MELD_BETA_SUFFIX)
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("❌ credentials.md 中未找到 Meld Encrypt β 加密块", file=sys.stderr)
        print("   请在 Obsidian 中使用 Meld Encrypt 加密该文件", file=sys.stderr)
        sys.exit(1)

    b64_blob = match.group(1).strip()
    try:
        plain = _decrypt_meld_beta(b64_blob, password)
    except Exception:
        print("❌ 密码错误", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(plain)
    except json.JSONDecodeError:
        print("❌ 解密成功但内容不是有效 JSON，请检查 credentials.md 的格式", file=sys.stderr)
        sys.exit(1)


def _get_password(args) -> str:
    if getattr(args, "password", None):
        return args.password
    return getpass.getpass("🔑 凭证库密码：")


def _read_key_names() -> list[str]:
    """从文件头部注释中读取 key 名称列表（无需密码）。"""
    if not os.path.exists(_CREDENTIALS_FILE):
        return []
    content = open(_CREDENTIALS_FILE, encoding="utf-8").read()
    m = re.search(r"<!-- KEYS:(.*?)-->", content, re.DOTALL)
    if not m:
        return []
    try:
        return json.loads(m.group(1).strip())
    except Exception:
        return []


# ── 命令处理 ───────────────────────────────────────────────────────────────────

def cmd_list(args):
    keys = _read_key_names()
    if not keys:
        print("_(暂无凭证，或文件不存在)_")
        return
    print("📋 已存储的 Key：")
    for k in keys:
        print(f"  • {k}")


def cmd_get(args):
    password = _get_password(args)
    data = _load_credentials(password)
    if args.key not in data:
        print(f"❌ Key `{args.key}` 不存在", file=sys.stderr)
        print(f"   可用 Key：{', '.join(sorted(data.keys()))}", file=sys.stderr)
        sys.exit(1)
    print(data[args.key])


def cmd_export(args):
    password = _get_password(args)
    data = _load_credentials(password)
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 入口 ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="凭证管理器（读取 Obsidian Meld Encrypt 加密文件）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    sub = parser.add_subparsers(dest="cmd")

    def _pw(p): p.add_argument("-p", "--password", help="密码（AI 非交互调用）", default=None)

    p_list = sub.add_parser("list",   help="列出所有 Key 名（无需密码）")
    p_get  = sub.add_parser("get",    help="获取单个凭证值"); _pw(p_get);  p_get.add_argument("key")
    p_exp  = sub.add_parser("export", help="导出全部凭证 JSON"); _pw(p_exp)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help(); sys.exit(0)

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        print("❌ 缺少依赖，请运行：pip install cryptography", file=sys.stderr)
        sys.exit(1)

    {"list": cmd_list, "get": cmd_get, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    main()
