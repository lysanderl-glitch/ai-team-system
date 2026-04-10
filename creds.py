#!/usr/bin/env python3
"""
Credentials Manager — ai-team-system
读取 Obsidian Meld Encrypt 整文件加密（.mdenc）格式的凭证文件。

=== 日常使用（在 Obsidian 里）===
  打开 obs/credentials.mdenc → 输入密码 → 正常查看/编辑
  保存后自动重新加密

=== AI 调用方式 ===
  python creds.py list                      # 查看所有 Key 名（无需密码）
  python creds.py get GITHUB_TOKEN          # 获取单个值（交互输入密码）
  python creds.py get GITHUB_TOKEN -p "密码"  # 非交互（AI 自动调用）
  python creds.py export -p "密码"           # 导出全部 JSON

=== 凭证文件内容格式（解密后应为 JSON）===
  {
    "GITHUB_TOKEN": "ghp_xxx",
    "NOTION_TOKEN": "ntn_xxx",
    ...
  }
"""

import os, sys, re, json, base64, getpass, argparse

# .mdenc 文件路径
_CREDS_FILE = os.path.join(os.path.dirname(__file__), "obs", "credentials.mdenc")

# Meld Encrypt v2.0 加密参数（class J，来自插件源码 v2.4.5）
_VECTOR_SIZE = 16   # IV 长度
_SALT_SIZE   = 16   # Salt 长度
_ITERATIONS  = 210_000
_HASH        = "SHA512"


def _decrypt_v2(encoded_data: str, password: str) -> str:
    """解密 Meld Encrypt v2.0 encodedData，返回明文。"""
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    raw        = base64.b64decode(encoded_data)
    iv         = raw[:_VECTOR_SIZE]
    salt       = raw[_VECTOR_SIZE:_VECTOR_SIZE + _SALT_SIZE]
    ciphertext = raw[_VECTOR_SIZE + _SALT_SIZE:]

    kdf = PBKDF2HMAC(algorithm=hashes.SHA512(), length=32, salt=salt, iterations=_ITERATIONS)
    key = kdf.derive(password.encode("utf-8"))
    try:
        plain = AESGCM(key).decrypt(iv, ciphertext, None)
        return plain.decode("utf-8")
    except Exception:
        print("❌ 密码错误", file=sys.stderr)
        sys.exit(1)


def _load(password: str) -> dict:
    if not os.path.exists(_CREDS_FILE):
        print(f"❌ 找不到凭证文件：{_CREDS_FILE}", file=sys.stderr)
        print("   请在 Obsidian 中打开 credentials.md，填写凭证后使用", file=sys.stderr)
        print("   'Meld Encrypt: Convert to or from an Encrypted note' 加密", file=sys.stderr)
        sys.exit(1)

    raw = open(_CREDS_FILE, encoding="utf-8").read().strip()
    try:
        file_data = json.loads(raw)
    except json.JSONDecodeError:
        print("❌ 文件格式错误，不是有效的 .mdenc 文件", file=sys.stderr)
        sys.exit(1)

    version      = file_data.get("version", "")
    encoded_data = file_data.get("encodedData", "")

    if not encoded_data:
        print("❌ 文件未加密或内容为空，请在 Obsidian 中先加密", file=sys.stderr)
        sys.exit(1)
    if version != "2.0":
        print(f"⚠️  未知版本 {version}，尝试按 v2.0 解密", file=sys.stderr)

    plain = _decrypt_v2(encoded_data, password)

    try:
        return json.loads(plain)
    except json.JSONDecodeError:
        print("❌ 解密成功但内容不是有效 JSON，请检查凭证文件格式", file=sys.stderr)
        sys.exit(1)


def _pw(args) -> str:
    return args.password if getattr(args, "password", None) else getpass.getpass("🔑 凭证库密码：")


# ── 命令 ─────────────────────────────────────────────────────────────────────

def cmd_list(args):
    if not os.path.exists(_CREDS_FILE):
        print("❌ 凭证文件不存在"); return
    raw = open(_CREDS_FILE, encoding="utf-8").read().strip()
    try:
        hint = json.loads(raw).get("hint", "")
        print(f"📋 凭证文件：{_CREDS_FILE}")
        if hint:
            print(f"   提示：{hint}")
        print("   （输入密码后可查看 Key 列表）")
        print("\n   运行 `python creds.py export -p 密码` 查看所有 Key")
    except Exception:
        print("❌ 文件读取失败")


def cmd_get(args):
    data = _load(_pw(args))
    if args.key not in data:
        print(f"❌ Key `{args.key}` 不存在", file=sys.stderr)
        print(f"   可用：{', '.join(sorted(data.keys()))}", file=sys.stderr)
        sys.exit(1)
    print(data[args.key])


def cmd_export(args):
    data = _load(_pw(args))
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ── 入口 ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="凭证管理器（Meld Encrypt .mdenc）",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=__doc__)
    sub = parser.add_subparsers(dest="cmd")

    def _addpw(p): p.add_argument("-p", "--password", default=None, help="密码（非交互）")

    sub.add_parser("list", help="查看凭证文件信息")
    p_get = sub.add_parser("get",    help="获取单个值"); _addpw(p_get); p_get.add_argument("key")
    p_exp = sub.add_parser("export", help="导出全部 JSON"); _addpw(p_exp)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help(); sys.exit(0)

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        print("❌ 缺少依赖：pip install cryptography", file=sys.stderr); sys.exit(1)

    {"list": cmd_list, "get": cmd_get, "export": cmd_export}[args.cmd](args)


if __name__ == "__main__":
    main()
