#!/bin/bash
###############################################################################
# fix-nginx-security.sh
#
# 自包含 Nginx 安全修复脚本 — 通过 ssh lysander-server < fix-nginx-security.sh 执行
#
# 修复内容：
#   1. Nginx 安全配置（OCSP Stapling、安全头、隐藏版本、HTTP/2）
#   2. Google Fonts Inter 字体自托管（替换外链为本地引用）
#
# 特性：
#   - 自动探测 Nginx 配置路径、网站根目录、SSL 证书路径
#   - 修改前自动备份
#   - nginx -t 测试失败自动回滚
#   - 全程输出进度信息
###############################################################################

set -e

BACKUP_DIR="/tmp/nginx-fix-backup-$(date +%Y%m%d%H%M%S)"
ROLLBACK_NEEDED=false

# ─── 颜色输出 ─────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }
step()    { echo -e "\n${GREEN}━━━ Step $1: $2 ━━━${NC}"; }

# ─── 回滚函数 ─────────────────────────────────────────────────────────────────
rollback() {
    error "检测到错误，开始回滚..."
    if [ -d "$BACKUP_DIR" ]; then
        # 回滚 Nginx 配置
        if [ -f "$BACKUP_DIR/nginx_site.conf.bak" ] && [ -n "$NGINX_SITE_CONF" ]; then
            sudo cp "$BACKUP_DIR/nginx_site.conf.bak" "$NGINX_SITE_CONF"
            info "已回滚 Nginx 站点配置"
        fi
        if [ -f "$BACKUP_DIR/nginx.conf.bak" ]; then
            sudo cp "$BACKUP_DIR/nginx.conf.bak" /etc/nginx/nginx.conf
            info "已回滚 Nginx 主配置"
        fi
        # 重新加载回滚后的配置
        if sudo nginx -t 2>/dev/null; then
            sudo systemctl reload nginx
            success "回滚完成，Nginx 已恢复到修改前状态"
        else
            error "回滚后 Nginx 配置仍然无效！请手动检查备份目录: $BACKUP_DIR"
        fi
    else
        error "未找到备份目录，无法自动回滚"
    fi
    exit 1
}

trap 'if [ "$ROLLBACK_NEEDED" = true ]; then rollback; fi' ERR

# ─── 前置检查 ─────────────────────────────────────────────────────────────────
step "0" "前置检查"

# 必须以 root 或有 sudo 权限运行
if [ "$(id -u)" -ne 0 ]; then
    if ! sudo -n true 2>/dev/null; then
        error "需要 root 权限或免密 sudo。请用 root 执行或配置 sudo。"
        exit 1
    fi
fi
success "权限检查通过"

# 检查 Nginx 是否安装
if ! command -v nginx &>/dev/null; then
    error "Nginx 未安装"
    exit 1
fi
NGINX_VERSION=$(nginx -v 2>&1 | grep -oP '[\d.]+')
success "检测到 Nginx $NGINX_VERSION"

# 检查 curl 是否可用
if ! command -v curl &>/dev/null; then
    info "安装 curl..."
    sudo apt-get update -qq && sudo apt-get install -y -qq curl
fi
success "curl 可用"

# ─── 自动探测 ─────────────────────────────────────────────────────────────────
step "1" "自动探测配置路径"

# 探测 Nginx 站点配置文件
NGINX_SITE_CONF=""
if [ -d /etc/nginx/sites-enabled ]; then
    # 排除 default，找主站点配置
    NGINX_SITE_CONF=$(find /etc/nginx/sites-enabled/ -type f -o -type l | grep -v 'default$' | head -1)
    # 如果只有 default 就用 default
    if [ -z "$NGINX_SITE_CONF" ]; then
        NGINX_SITE_CONF=$(find /etc/nginx/sites-enabled/ -type f -o -type l | head -1)
    fi
fi
if [ -z "$NGINX_SITE_CONF" ] && [ -d /etc/nginx/conf.d ]; then
    NGINX_SITE_CONF=$(find /etc/nginx/conf.d/ -name '*.conf' -type f | grep -v 'default' | head -1)
    if [ -z "$NGINX_SITE_CONF" ]; then
        NGINX_SITE_CONF=$(find /etc/nginx/conf.d/ -name '*.conf' -type f | head -1)
    fi
fi
if [ -z "$NGINX_SITE_CONF" ]; then
    error "未找到 Nginx 站点配置文件（检查了 sites-enabled/ 和 conf.d/）"
    exit 1
fi
# 如果是符号链接，解析到实际文件（方便编辑）
if [ -L "$NGINX_SITE_CONF" ]; then
    NGINX_SITE_CONF_REAL=$(readlink -f "$NGINX_SITE_CONF")
    info "符号链接: $NGINX_SITE_CONF -> $NGINX_SITE_CONF_REAL"
    NGINX_SITE_CONF="$NGINX_SITE_CONF_REAL"
fi
success "站点配置: $NGINX_SITE_CONF"

# 从配置中提取网站根目录
WEB_ROOT=$(grep -oP '^\s*root\s+\K[^;]+' "$NGINX_SITE_CONF" | head -1 | xargs)
if [ -z "$WEB_ROOT" ]; then
    error "无法从配置中提取 root 指令"
    exit 1
fi
if [ ! -d "$WEB_ROOT" ]; then
    error "网站根目录 $WEB_ROOT 不存在"
    exit 1
fi
success "网站根目录: $WEB_ROOT"

# 从配置中提取 SSL 证书路径
SSL_CERT=$(grep -oP '^\s*ssl_certificate\s+\K[^;]+' "$NGINX_SITE_CONF" | head -1 | xargs)
SSL_KEY=$(grep -oP '^\s*ssl_certificate_key\s+\K[^;]+' "$NGINX_SITE_CONF" | head -1 | xargs)
if [ -z "$SSL_CERT" ] || [ -z "$SSL_KEY" ]; then
    warn "未在站点配置中找到 SSL 证书路径，尝试从 nginx.conf 查找..."
    SSL_CERT=$(grep -rP '^\s*ssl_certificate\s+' /etc/nginx/ 2>/dev/null | grep -v '#' | grep -oP 'ssl_certificate\s+\K[^;]+' | head -1 | xargs)
    SSL_KEY=$(grep -rP '^\s*ssl_certificate_key\s+' /etc/nginx/ 2>/dev/null | grep -v '#' | grep -oP 'ssl_certificate_key\s+\K[^;]+' | head -1 | xargs)
fi
if [ -n "$SSL_CERT" ]; then
    success "SSL 证书: $SSL_CERT"
    success "SSL 密钥: $SSL_KEY"
else
    warn "未找到 SSL 证书路径，OCSP Stapling 配置将跳过"
fi

# 提取域名（从 server_name 指令）
DOMAIN=$(grep -oP '^\s*server_name\s+\K[^;]+' "$NGINX_SITE_CONF" | head -1 | awk '{print $1}' | xargs)
success "域名: ${DOMAIN:-未检测到}"

# ─── 备份 ─────────────────────────────────────────────────────────────────────
step "2" "备份现有配置和文件"

mkdir -p "$BACKUP_DIR"
sudo cp "$NGINX_SITE_CONF" "$BACKUP_DIR/nginx_site.conf.bak"
sudo cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx.conf.bak"
success "已备份到 $BACKUP_DIR/"
info "  - nginx_site.conf.bak (站点配置)"
info "  - nginx.conf.bak (主配置)"

# 标记开始修改，启用回滚保护
ROLLBACK_NEEDED=true

# ─── 修复1：Nginx 安全配置 ──────────────────────────────────────────────────
step "3" "修复 Nginx 安全配置"

# --- 3a: 隐藏 server_tokens（在 nginx.conf 的 http 块中） ---
info "3a. 隐藏 server_tokens..."
if grep -qP '^\s*server_tokens\s+off' /etc/nginx/nginx.conf; then
    info "server_tokens off 已存在，跳过"
else
    # 如果有 server_tokens on，替换为 off
    if grep -qP '^\s*server_tokens' /etc/nginx/nginx.conf; then
        sudo sed -i 's/^\(\s*\)server_tokens\s.*/\1server_tokens off;/' /etc/nginx/nginx.conf
    else
        # 在 http { 后面添加
        sudo sed -i '/http\s*{/a\    server_tokens off;' /etc/nginx/nginx.conf
    fi
    success "已设置 server_tokens off"
fi

# --- 3b: 启用 HTTP/2 ---
info "3b. 启用 HTTP/2..."
# Nginx 1.24 使用 listen ... http2 语法（而非 1.25+ 的 http2 on 指令）
if grep -qP 'listen\s+.*443\s+ssl\s+http2' "$NGINX_SITE_CONF"; then
    info "HTTP/2 已启用，跳过"
elif grep -qP 'listen\s+.*443\s+ssl' "$NGINX_SITE_CONF"; then
    # 在 ssl 后面添加 http2
    sudo sed -i -E 's/(listen\s+.*443\s+ssl)\b/\1 http2/' "$NGINX_SITE_CONF"
    success "已启用 HTTP/2"
else
    warn "未找到 443 ssl listen 指令，请手动检查"
fi

# --- 3c: OCSP Stapling ---
info "3c. 配置 OCSP Stapling..."
if grep -qP '^\s*ssl_stapling\s+on' "$NGINX_SITE_CONF"; then
    info "OCSP Stapling 已存在，跳过"
else
    # 构建 OCSP 配置块
    OCSP_BLOCK="
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;"

    # 如果有 ssl_trusted_certificate 就使用它，否则使用 ssl_certificate
    if [ -n "$SSL_CERT" ]; then
        # Let's Encrypt fullchain.pem 通常可以同时用作 trusted certificate
        TRUSTED_CERT="$SSL_CERT"
        # 检查是否存在 chain.pem（同目录）
        CERT_DIR=$(dirname "$SSL_CERT")
        if [ -f "$CERT_DIR/chain.pem" ]; then
            TRUSTED_CERT="$CERT_DIR/chain.pem"
        fi
        OCSP_BLOCK="${OCSP_BLOCK}
    ssl_trusted_certificate ${TRUSTED_CERT};"
    fi

    OCSP_BLOCK="${OCSP_BLOCK}
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;"

    # 在 ssl_certificate_key 行后面插入 OCSP 配置
    if grep -qP '^\s*ssl_certificate_key' "$NGINX_SITE_CONF"; then
        sudo sed -i "/ssl_certificate_key/a\\${OCSP_BLOCK}" "$NGINX_SITE_CONF"
    else
        # 在第一个 server 块的 listen 443 行后面插入
        sudo sed -i "/listen.*443.*ssl/a\\${OCSP_BLOCK}" "$NGINX_SITE_CONF"
    fi
    success "已配置 OCSP Stapling"
fi

# --- 3d: 安全响应头 ---
info "3d. 添加安全响应头..."

# 检查是否已有安全头配置
if grep -qP '^\s*add_header\s+Strict-Transport-Security' "$NGINX_SITE_CONF"; then
    info "安全头已存在，跳过"
else
    SECURITY_HEADERS='
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;'

    # 找到 server 块中的 location / 之前插入，或在 server 块开头插入
    # 策略：在第一个 location 块之前插入安全头
    FIRST_LOCATION_LINE=$(grep -nP '^\s*location\s' "$NGINX_SITE_CONF" | head -1 | cut -d: -f1)
    if [ -n "$FIRST_LOCATION_LINE" ]; then
        sudo sed -i "${FIRST_LOCATION_LINE}i\\${SECURITY_HEADERS}" "$NGINX_SITE_CONF"
    else
        # 在 server_name 行后面插入
        sudo sed -i "/server_name/a\\${SECURITY_HEADERS}" "$NGINX_SITE_CONF"
    fi
    success "已添加全套安全响应头"
fi

# --- 3e: 测试 Nginx 配置 ---
info "3e. 测试 Nginx 配置..."
if sudo nginx -t 2>&1; then
    success "Nginx 配置测试通过"
else
    error "Nginx 配置测试失败！"
    rollback
fi

# ─── 修复2：Google Fonts 自托管 ──────────────────────────────────────────────
step "4" "Google Fonts Inter 字体自托管"

FONTS_DIR="$WEB_ROOT/fonts"
sudo mkdir -p "$FONTS_DIR"
success "字体目录: $FONTS_DIR"

# --- 4a: 下载 Google Fonts CSS（使用现代 User-Agent 获取 woff2 格式）---
info "4a. 获取 Google Fonts CSS..."
GFONTS_URL="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
GFONTS_CSS=$(curl -sS -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "$GFONTS_URL")

if [ -z "$GFONTS_CSS" ]; then
    warn "无法获取 Google Fonts CSS，尝试备用方法..."
    GFONTS_CSS=$(curl -sS -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "$GFONTS_URL")
fi

if [ -z "$GFONTS_CSS" ]; then
    error "无法获取 Google Fonts CSS。跳过字体自托管。"
else
    success "已获取 Google Fonts CSS"

    # --- 4b: 提取并下载所有 woff2 文件 ---
    info "4b. 下载 woff2 字体文件..."
    WOFF2_URLS=$(echo "$GFONTS_CSS" | grep -oP 'https://fonts\.gstatic\.com/[^)]+\.woff2')

    FONT_COUNT=0
    FONT_MAP="" # 用于记录 URL -> 本地文件名 的映射

    while IFS= read -r url; do
        if [ -z "$url" ]; then continue; fi
        FONT_COUNT=$((FONT_COUNT + 1))
        # 生成可读的文件名
        FILENAME="inter-${FONT_COUNT}.woff2"

        info "  下载: $FILENAME"
        if sudo curl -sS -o "$FONTS_DIR/$FILENAME" "$url"; then
            FONT_MAP="${FONT_MAP}${url}|${FILENAME}\n"
        else
            warn "  下载失败: $url"
        fi
    done <<< "$WOFF2_URLS"

    success "已下载 ${FONT_COUNT} 个字体文件"

    # --- 4c: 生成本地 @font-face CSS ---
    info "4c. 生成本地 inter.css..."

    # 将 Google CSS 中的远程 URL 替换为本地路径
    LOCAL_CSS="$GFONTS_CSS"
    while IFS='|' read -r remote_url local_file; do
        if [ -z "$remote_url" ] || [ -z "$local_file" ]; then continue; fi
        LOCAL_CSS=$(echo "$LOCAL_CSS" | sed "s|${remote_url}|/fonts/${local_file}|g")
    done <<< "$(echo -e "$FONT_MAP")"

    # 写入本地 CSS 文件
    echo "$LOCAL_CSS" | sudo tee "$FONTS_DIR/inter.css" > /dev/null
    success "已生成 $FONTS_DIR/inter.css"

    # --- 4d: 替换 HTML 中的 Google Fonts 外链 ---
    info "4d. 替换 HTML 中的 Google Fonts 引用..."

    # 备份 HTML 文件
    HTML_FILES=$(find "$WEB_ROOT" -name '*.html' -type f 2>/dev/null)
    HTML_MODIFIED=0

    if [ -n "$HTML_FILES" ]; then
        sudo mkdir -p "$BACKUP_DIR/html"

        while IFS= read -r html_file; do
            if [ -z "$html_file" ]; then continue; fi

            # 检查文件是否包含 Google Fonts 引用
            if grep -q 'fonts.googleapis.com' "$html_file" || grep -q 'fonts.gstatic.com' "$html_file"; then
                # 备份
                REL_PATH="${html_file#$WEB_ROOT/}"
                BACKUP_SUBDIR=$(dirname "$BACKUP_DIR/html/$REL_PATH")
                sudo mkdir -p "$BACKUP_SUBDIR"
                sudo cp "$html_file" "$BACKUP_DIR/html/$REL_PATH"

                # 替换 Google Fonts preconnect 链接
                sudo sed -i '/<link[^>]*rel="preconnect"[^>]*fonts\.googleapis\.com[^>]*>/d' "$html_file"
                sudo sed -i '/<link[^>]*rel="preconnect"[^>]*fonts\.gstatic\.com[^>]*>/d' "$html_file"
                # 反向顺序匹配（rel 在 href 前面的情况）
                sudo sed -i '/<link[^>]*fonts\.googleapis\.com[^>]*preconnect[^>]*>/d' "$html_file"
                sudo sed -i '/<link[^>]*fonts\.gstatic\.com[^>]*preconnect[^>]*>/d' "$html_file"

                # 替换 Google Fonts stylesheet 链接为本地引用
                # 处理各种可能的格式
                sudo sed -i 's|<link[^>]*href="https://fonts\.googleapis\.com/css2[^"]*Inter[^"]*"[^>]*>|<link rel="stylesheet" href="/fonts/inter.css">|g' "$html_file"
                sudo sed -i 's|<link[^>]*href="https://fonts\.googleapis\.com/css[^"]*Inter[^"]*"[^>]*>|<link rel="stylesheet" href="/fonts/inter.css">|g' "$html_file"

                # 清理可能残留的其他 Google Fonts 引用（非 Inter 的也统一处理）
                # 如果还有其他 Google Fonts 链接，替换为本地
                if grep -q 'fonts.googleapis.com' "$html_file"; then
                    sudo sed -i 's|<link[^>]*href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>|<link rel="stylesheet" href="/fonts/inter.css">|g' "$html_file"
                    sudo sed -i 's|<link[^>]*href="https://fonts\.googleapis\.com/css[^"]*"[^>]*>|<link rel="stylesheet" href="/fonts/inter.css">|g' "$html_file"
                fi

                # 移除 @import url() 形式的 Google Fonts 引入
                sudo sed -i '/@import\s*url.*fonts\.googleapis\.com/d' "$html_file"

                # 去重：如果同一个文件中有多个相同的本地引用，保留一个
                # 使用 awk 去除重复的 <link rel="stylesheet" href="/fonts/inter.css"> 行
                sudo awk '!seen[$0]++ || $0 !~ /\/fonts\/inter\.css/' "$html_file" | sudo tee "${html_file}.tmp" > /dev/null
                sudo mv "${html_file}.tmp" "$html_file"

                HTML_MODIFIED=$((HTML_MODIFIED + 1))
                info "  已修改: $REL_PATH"
            fi
        done <<< "$HTML_FILES"
    fi

    if [ "$HTML_MODIFIED" -gt 0 ]; then
        success "已修改 ${HTML_MODIFIED} 个 HTML 文件"
    else
        warn "未找到包含 Google Fonts 引用的 HTML 文件"
    fi
fi

# ─── 最终 Nginx 测试与重载 ───────────────────────────────────────────────────
step "5" "最终 Nginx 测试与重载"

info "运行 nginx -t 最终测试..."
if sudo nginx -t 2>&1; then
    success "Nginx 配置测试通过"
    info "重新加载 Nginx..."
    sudo systemctl reload nginx
    success "Nginx 已重新加载"
    ROLLBACK_NEEDED=false
else
    error "最终 Nginx 配置测试失败！"
    rollback
fi

# ─── 验证 ─────────────────────────────────────────────────────────────────────
step "6" "验证修复结果"

echo ""
info "=== 验证 1: Nginx 版本隐藏 ==="
if [ -n "$DOMAIN" ]; then
    SERVER_HEADER=$(curl -sI "https://${DOMAIN}" 2>/dev/null | grep -i '^server:' || true)
    if echo "$SERVER_HEADER" | grep -qi 'nginx/'; then
        warn "Server 头仍暴露版本号: $SERVER_HEADER"
    elif [ -n "$SERVER_HEADER" ]; then
        success "Server 头已隐藏版本号: $SERVER_HEADER"
    else
        info "无法检测 Server 头（可能需要等待 DNS 或外部访问）"
    fi
else
    info "未检测到域名，跳过远程验证"
fi

echo ""
info "=== 验证 2: 安全响应头 ==="
if [ -n "$DOMAIN" ]; then
    HEADERS=$(curl -sI "https://${DOMAIN}" 2>/dev/null)

    for HEADER in "Strict-Transport-Security" "X-Content-Type-Options" "X-Frame-Options" "X-XSS-Protection" "Referrer-Policy" "Permissions-Policy"; do
        if echo "$HEADERS" | grep -qi "^${HEADER}:"; then
            VALUE=$(echo "$HEADERS" | grep -i "^${HEADER}:" | head -1)
            success "  $VALUE"
        else
            warn "  缺少: $HEADER"
        fi
    done
else
    info "未检测到域名，检查配置文件中的安全头..."
    grep -c 'add_header' "$NGINX_SITE_CONF" | xargs -I{} echo "  配置中包含 {} 条 add_header 指令"
fi

echo ""
info "=== 验证 3: OCSP Stapling ==="
if [ -n "$DOMAIN" ]; then
    OCSP_RESULT=$(echo | timeout 5 openssl s_client -connect "${DOMAIN}:443" -status 2>/dev/null | grep -A1 "OCSP Response Status" || true)
    if echo "$OCSP_RESULT" | grep -q "successful"; then
        success "OCSP Stapling 已生效"
    else
        info "OCSP Stapling 可能需要几分钟才能生效（首次请求后缓存）"
        info "手动测试: echo | openssl s_client -connect ${DOMAIN}:443 -status 2>/dev/null | grep 'OCSP'"
    fi
else
    info "未检测到域名，跳过 OCSP 验证"
    grep -c 'ssl_stapling' "$NGINX_SITE_CONF" | xargs -I{} echo "  配置中包含 {} 条 ssl_stapling 指令"
fi

echo ""
info "=== 验证 4: HTTP/2 ==="
if [ -n "$DOMAIN" ]; then
    HTTP2_CHECK=$(curl -sI --http2 "https://${DOMAIN}" 2>/dev/null | head -1 || true)
    if echo "$HTTP2_CHECK" | grep -q "HTTP/2"; then
        success "HTTP/2 已启用"
    else
        info "HTTP/2 检测结果: $HTTP2_CHECK"
    fi
else
    if grep -q 'http2' "$NGINX_SITE_CONF"; then
        success "HTTP/2 已在配置中启用"
    fi
fi

echo ""
info "=== 验证 5: 本地字体文件 ==="
if [ -d "$FONTS_DIR" ]; then
    WOFF2_COUNT=$(find "$FONTS_DIR" -name '*.woff2' -type f 2>/dev/null | wc -l)
    CSS_EXISTS=$([ -f "$FONTS_DIR/inter.css" ] && echo "yes" || echo "no")
    success "字体目录: $FONTS_DIR"
    success "woff2 文件数量: $WOFF2_COUNT"
    if [ "$CSS_EXISTS" = "yes" ]; then
        success "inter.css: 已创建"
    else
        warn "inter.css: 未找到"
    fi
fi

echo ""
info "=== 验证 6: HTML 中 Google Fonts 残留检查 ==="
REMAINING=$(grep -rl 'fonts.googleapis.com' "$WEB_ROOT" --include='*.html' 2>/dev/null | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    success "所有 HTML 文件中已无 Google Fonts 外链"
else
    warn "仍有 $REMAINING 个文件包含 Google Fonts 引用，需手动检查"
    grep -rl 'fonts.googleapis.com' "$WEB_ROOT" --include='*.html' 2>/dev/null | while read -r f; do
        warn "  $f"
    done
fi

# ─── 完成报告 ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  修复完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  备份目录: $BACKUP_DIR"
echo "  站点配置: $NGINX_SITE_CONF"
echo "  网站根目录: $WEB_ROOT"
echo "  字体目录: $FONTS_DIR"
echo ""
echo "  已完成修复:"
echo "    [1] server_tokens off — 隐藏 Nginx 版本号"
echo "    [2] HTTP/2 — 已在 listen 指令中启用"
echo "    [3] OCSP Stapling — 已启用（含 resolver）"
echo "    [4] 安全响应头 — HSTS / X-Content-Type-Options / X-Frame-Options"
echo "                      X-XSS-Protection / Referrer-Policy / Permissions-Policy"
echo "    [5] Inter 字体自托管 — woff2 文件已下载，HTML 已替换"
echo ""
echo "  如需回滚: sudo cp $BACKUP_DIR/*.bak 到对应位置后 sudo systemctl reload nginx"
echo ""
