#!/usr/bin/env python3
"""
Encrypted Credentials Manager — ai-team-system
AES-256-GCM encryption, PBKDF2-SHA256 key derivation (600k iterations)

Usage:
  python creds.py init                          # 初始化新的凭证库
  python creds.py add KEY VALUE                 # 添加/更新凭证
  python creds.py get KEY                       # 获取单个凭证值
  python creds.py list                          # 列出所有 Key 名
  python creds.py export                        # 导出全部（JSON 格式，供 AI 使用）
  python creds.py delete KEY                    # 删除凭证
  python creds.py add KEY VALUE -p PASSWORD     # 非交互模式（脚本/AI 调用）
  python creds.py get KEY -p PASSWORD           # 非交互模式
  python creds.py export -p PASSWORD            # 非交互模式
"""

import os
import sys
import json
import base64
import getpass
import argparse
import re
import secrets as secrets_mod

STORE_FILE = os.path.join(os.path.dirname(__file__), "credentials.enc.md")

# ── 加密 / 解密 ────────────────────────────────────────────────────────────────

def _derive_key(password: str, salt: bytes) -> bytes:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    return kdf.derive(password.encode("utf-8"))


def _encrypt(data: dict, password: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    salt  = secrets_mod.token_bytes(16)
    nonce = secrets_mod.token_bytes(12)
    key   = _derive_key(password, salt)
    ct    = AESGCM(key).encrypt(nonce, json.dumps(data, ensure_ascii=False).encode(), None)
    payload = {
        "v": 1,
        "salt":  base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct":    base64.b64encode(ct).decode(),
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


def _decrypt(encoded: str, password: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    try:
        payload = json.loads(base64.b64decode(encoded).decode())
        salt  = base64.b64decode(payload["salt"])
        nonce = base64.b64decode(payload["nonce"])
        ct    = base64.b64decode(payload["ct"])
        key   = _derive_key(password, salt)
        plain = AESGCM(key).decrypt(nonce, ct, None)
        return json.loads(plain.decode())
    except Exception:
        print("❌ 密码错误或文件已损坏", file=sys.stderr)
        sys.exit(1)

# ── 文件读写 ───────────────────────────────────────────────────────────────────

_BLOCK_RE = re.compile(r"```encrypted\n(.*?)\n```", re.DOTALL)


def _read_store() -> tuple[str, list[str]]:
    """返回 (加密块内容 or '', 所有 key 名列表)"""
    if not os.path.exists(STORE_FILE):
        return "", []
    content = open(STORE_FILE, encoding="utf-8").read()
    m = _BLOCK_RE.search(content)
    enc_block = m.group(1).strip() if m else ""

    keys_m = re.search(r"<!-- KEYS:(.*?)-->", content, re.DOTALL)
    keys = json.loads(keys_m.group(1).strip()) if keys_m else []
    return enc_block, keys


def _write_store(data: dict, password: str) -> None:
    enc = _encrypt(data, password)
    keys = sorted(data.keys())
    content = f"""# 🔐 加密凭证库 — ai-team-system

> **安全说明**：此文件内容经 AES-256-GCM 加密，密钥由 PBKDF2-SHA256（60万次迭代）派生。
> 密文在没有密码的情况下无法读取。此文件已加入 `.gitignore`，不会上传 GitHub。

## 已存储的凭证 Key（仅展示名称）

<!-- KEYS:{json.dumps(keys, ensure_ascii=False)} -->

{chr(10).join(f"- `{k}`" for k in keys) if keys else "_(暂无凭证)_"}

## 加密数据块

```encrypted
{enc}
```

---
*使用 `python creds.py --help` 查看操作说明*
"""
    open(STORE_FILE, "w", encoding="utf-8").write(content)
    print(f"✅ 凭证库已更新（共 {len(keys)} 条记录）")

# ── 命令处理 ───────────────────────────────────────────────────────────────────

def _get_password(args) -> str:
    if hasattr(args, 'password') and args.password:
        return args.password
    return getpass.getpass("🔑 请输入凭证库密码：")


def cmd_init(args):
    if os.path.exists(STORE_FILE):
        print("⚠️  凭证库已存在，跳过初始化")
        return
    password = _get_password(args)
    if not (hasattr(args, 'password') and args.password):
        confirm = getpass.getpass("🔑 再次确认密码：")
        if password != confirm:
            print("❌ 两次密码不一致", file=sys.stderr); sys.exit(1)
    _write_store({}, password)
    print("🎉 凭证库初始化完成！")


def cmd_add(args):
    enc, keys = _read_store()
    if not enc:
        print("❌ 凭证库不存在，请先运行 `python creds.py init`", file=sys.stderr); sys.exit(1)
    password = _get_password(args)
    data = _decrypt(enc, password)
    data[args.key] = args.value
    _write_store(data, password)
    print(f"✅ 已保存 `{args.key}`")


def cmd_get(args):
    enc, _ = _read_store()
    if not enc:
        print("❌ 凭证库不存在", file=sys.stderr); sys.exit(1)
    password = _get_password(args)
    data = _decrypt(enc, password)
    if args.key not in data:
        print(f"❌ Key `{args.key}` 不存在", file=sys.stderr); sys.exit(1)
    print(data[args.key])


def cmd_list(args):
    enc, keys = _read_store()
    if not enc:
        print("❌ 凭证库不存在", file=sys.stderr); sys.exit(1)
    if not keys:
        print("_(暂无凭证)_")
        return
    print("📋 已存储的 Key：")
    for k in keys:
        print(f"  • {k}")


def cmd_export(args):
    enc, _ = _read_store()
    if not enc:
        print("❌ 凭证库不存在", file=sys.stderr); sys.exit(1)
    password = _get_password(args)
    data = _decrypt(enc, password)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_delete(args):
    enc, _ = _read_store()
    if not enc:
        print("❌ 凭证库不存在", file=sys.stderr); sys.exit(1)
    password = _get_password(args)
    data = _decrypt(enc, password)
    if args.key not in data:
        print(f"❌ Key `{args.key}` 不存在", file=sys.stderr); sys.exit(1)
    del data[args.key]
    _write_store(data, password)
    print(f"🗑️  已删除 `{args.key}`")

# ── 入口 ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="加密凭证管理器")
    sub = parser.add_subparsers(dest="cmd")

    def _add_pw(p): p.add_argument("-p", "--password", help="密码（非交互模式）", default=None)

    p_init = sub.add_parser("init",   help="初始化凭证库"); _add_pw(p_init)
    p_add  = sub.add_parser("add",    help="添加/更新凭证"); _add_pw(p_add)
    p_add.add_argument("key"); p_add.add_argument("value")
    p_get  = sub.add_parser("get",    help="获取单个凭证"); _add_pw(p_get)
    p_get.add_argument("key")
    p_list = sub.add_parser("list",   help="列出所有 Key 名"); _add_pw(p_list)
    p_exp  = sub.add_parser("export", help="导出全部凭证（JSON）"); _add_pw(p_exp)
    p_del  = sub.add_parser("delete", help="删除凭证"); _add_pw(p_del)
    p_del.add_argument("key")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help(); sys.exit(0)

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        print("❌ 缺少依赖，请运行：pip install cryptography", file=sys.stderr)
        sys.exit(1)

    {"init": cmd_init, "add": cmd_add, "get": cmd_get,
     "list": cmd_list, "export": cmd_export, "delete": cmd_delete}[args.cmd](args)


if __name__ == "__main__":
    main()
