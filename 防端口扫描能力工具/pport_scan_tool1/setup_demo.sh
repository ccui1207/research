#!/usr/bin/env bash
set -euo pipefail

# ===== 你改这里 =====
OPEN_PORT=38080
PROTECTED_PORT=39090
PHONE_IP="36.112.192.129"   # 例如 1.2.3.4
# ====================

echo "[1/6] 检查依赖"
command -v iptables >/dev/null
command -v ipset >/dev/null
command -v python3 >/dev/null

echo "[2/6] 启动两个测试服务"
sudo mkdir -p /tmp/demo-open /tmp/demo-protected
echo "OPEN_PORT_OK" | sudo tee /tmp/demo-open/index.html >/dev/null
echo "PROTECTED_PORT_OK" | sudo tee /tmp/demo-protected/index.html >/dev/null

# 清理旧进程（如果有）
sudo pkill -f "http.server ${OPEN_PORT}" || true
sudo pkill -f "http.server ${PROTECTED_PORT}" || true

# 启动服务
sudo nohup python3 -m http.server "${OPEN_PORT}" --bind 0.0.0.0 --directory /tmp/demo-open >/tmp/demo-open.log 2>&1 &
sudo nohup python3 -m http.server "${PROTECTED_PORT}" --bind 0.0.0.0 --directory /tmp/demo-protected >/tmp/demo-protected.log 2>&1 &

echo "[3/6] 创建手机白名单（ipset）"
sudo ipset create mobile_allow hash:ip -exist
sudo ipset add mobile_allow "${PHONE_IP}" -exist

echo "[4/6] 对受保护端口加规则：白名单放行 + 其他丢弃"
sudo iptables -C INPUT -p tcp --dport "${PROTECTED_PORT}" -m set --match-set mobile_allow src -j ACCEPT 2>/dev/null \
  || sudo iptables -I INPUT 1 -p tcp --dport "${PROTECTED_PORT}" -m set --match-set mobile_allow src -j ACCEPT

sudo iptables -C INPUT -p tcp --dport "${PROTECTED_PORT}" -j DROP 2>/dev/null \
  || sudo iptables -I INPUT 2 -p tcp --dport "${PROTECTED_PORT}" -j DROP

echo "[5/6] 将手机IP追加到 portscan-protection 白名单（防误封）"
echo "${PHONE_IP}" | sudo tee -a /usr/local/sbin/portscan-protection-white.list >/dev/null

echo "[6/6] 显示结果"
echo "OPEN_PORT=${OPEN_PORT} (应当所有人可访问)"
echo "PROTECTED_PORT=${PROTECTED_PORT} (仅手机IP可访问)"
sudo iptables -S INPUT | grep -- "--dport ${PROTECTED_PORT}" || true
sudo ipset list mobile_allow || true

echo "完成。"