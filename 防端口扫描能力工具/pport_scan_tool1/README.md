# pport_scan_tool1（端口扫描防护与对照实验）

本项目用于在 **Linux 虚拟机 / 云主机** 上验证「开放端口 vs 基于源 IP 的访问控制」的对照效果，并可配合**自有组件 `portscan-protection`**（端口扫描防护与相关策略）做扩展实验。

`portscan-protection` 与本文档中的实验脚本同属你们侧维护的工具集；日常可将该工具**下载或同步到与本仓库并列的文件夹**（见第 5 节），再按需在目标机上安装。

本 README 采用「**本仓库脚本 + 系统 iptables/ipset + 可选部署 portscan-protection**」的方式进行验证。

---

## 1. 验证目标（三种直观现象）

1. **开放端口**：任意来源可访问；用 PC 端探测脚本可看到 **OPEN**。
2. **受保护端口**：仅白名单源 IP（例如手机蜂窝网出口 IP）可访问；其他来源表现为 **FILTERED / 超时**，PC 端脚本通常扫不出 OPEN。
3. **（可选）自有工具 `portscan-protection`**：对「扫端口过快」等行为的来源 IP 进行封禁等策略；需将管理端 IP 写入白名单，避免误封。

若你的运行环境是**无 `CAP_NET_ADMIN` 的容器**，则本机 `iptables`/`nft` 不可用，本文档中的 **iptables/ipset 演示无法生效**，请改用云主机 ECS 或特权容器。

---

## 2. 目录说明

仓库根目录主要文件：

| 文件 | 说明 |
|------|------|
| `portscan-protection.sh` | 自有防护组件入口脚本（也可仅放在并列目录中，由部署流程拷贝到目标机） |
| `setup_demo.sh` | 一键起两个 HTTP 演示端口 + `ipset` 白名单 + `iptables` 放行/丢弃规则 |
| `scan_port.sh` | Bash 端口探测（`/dev/tcp`），适合在 PC 上快速对比两端口 |
| `pc_scan.py` | Python 单次 TCP 连接探测，可指定端口列表 |
| `lab_probe_client.py` | Python 多端口轮询探测（默认 8080–8086），适合长期观察 |
| `demo_service.py` | 简易 Python HTTP 服务（可按端口、标签启动） |

若你的实际路径与下文不一致，请自行替换为本地绝对路径。

---

## 3. 环境要求

建议环境：

- **操作系统**：Ubuntu 22.04 LTS / Debian，或 **Alibaba Cloud Linux 8**（`el8`/`al8` 系）等带 `iptables` 的 Linux
- **权限**：可对防火墙下发规则的用户（`root` 或 `sudo`）
- **依赖**：`python3`、`iptables`、`ipset`；Bash 需支持 `/dev/tcp`（用于 `scan_port.sh`）

检查版本与命令：

```bash
node -v 2>/dev/null || true   # 本仓库演示不依赖 Node，可忽略
python3 -V
command -v iptables ipset curl sudo
```

在云主机上建议同时检查安全组是否放行演示端口（见第 8 节）。

---

## 4. 组件说明

### 4.1 `setup_demo.sh`

- 启动两个目录下的 `python3 -m http.server`，分别绑定 **`OPEN_PORT`** 与 **`PROTECTED_PORT`**。
- 使用 **`ipset mobile_allow`** 存放手机公网 IPv4，对 **`PROTECTED_PORT`** 执行：**白名单 ACCEPT → 其余 DROP**。
- 可选将手机 IP 追加到 **`/usr/local/sbin/portscan-protection-white.list`**（若已在目标机安装自有 `portscan-protection`，可降低误封风险）。

使用前请编辑脚本内变量：

- `OPEN_PORT`：无额外 IP 限制的对照端口  
- `PROTECTED_PORT`：仅白名单可访问  
- `PHONE_IP`：手机在 **关闭 Wi‑Fi、仅蜂窝数据** 下查到的公网 IPv4（会变，变更后需更新 `ipset` 与白名单）

### 4.2 `scan_port.sh`（PC / 任意客户端）

```text
用法: ./scan_port.sh <server_ip> <port1> <port2> ...
```

### 4.3 `pc_scan.py`

```text
用法: python3 pc_scan.py <SERVER_IP> [port1 port2 ...]
```

### 4.4 `lab_probe_client.py`

默认轮询端口 `8080–8086`，可改为与 `setup_demo.sh` 中端口一致后再测。

### 4.5 `demo_service.py`（可选）

```bash
python3 demo_service.py <PORT> <LABEL>
```

---

## 5. （可选）部署自有组件 `portscan-protection`

`portscan-protection` 为自有的防护工具；发布或归档时，可将该工具**整体下载到与本实验仓库并列的目录**（例如与 `pport_scan_tool1` 同级、放在旁边的 `portscan-protection` 文件夹），再在需要验证的机器上从该路径执行安装或拷贝。

**推荐目录布局示例：**

```text
work/
├── pport_scan_tool1/          # 本 README 对应的实验与脚本（当前概念名）
└── portscan-protection/       # 自有 portscan-protection 工具目录（你自行下载放置于此）
    └── portscan-protection.sh   # 示例：入口脚本名以你方仓库为准
```

在能操作防火墙的主机上，从**你放置并列目录后的实际路径**执行安装（路径请自行替换）：

```bash
sudo bash /path/to/portscan-protection/portscan-protection.sh -i
```

若安装脚本内含联网检查且网络不稳定，可在你们自己的发布流程中约定：离线拷贝、`curl` 超时参数、或关闭自动更新等，按内部文档执行即可。

安装完成后常用命令示例：

```bash
sudo /usr/local/sbin/portscan-protection.sh --verify
sudo /usr/local/sbin/portscan-protection.sh --set-sshport
```

---

## 6. 配置并启动对照实验

### 6.1 获取手机当前公网 IP

手机关闭 Wi‑Fi，使用蜂窝数据，在浏览器打开例如：

- `https://api.ipify.org`
- `https://ifconfig.me`

将得到的 **IPv4** 填入 `setup_demo.sh` 的 `PHONE_IP=`。

### 6.2 编辑并执行 `setup_demo.sh`

```bash
cd /path/to/pport_scan_tool1
vim setup_demo.sh   # 修改 OPEN_PORT / PROTECTED_PORT / PHONE_IP
chmod +x setup_demo.sh
./setup_demo.sh
```

### 6.3 本机确认监听（应在服务器上执行）

```bash
sudo ss -lntp | grep -E '38080|39090'   # 端口号请与脚本内一致
curl -I --max-time 3 "http://127.0.0.1:38080/"
```

若 `ss` 无输出、`curl` 为 `Connection refused`，说明 HTTP 服务未成功监听，请查看：

```bash
sudo tail -n 50 /tmp/demo-open.log
sudo tail -n 50 /tmp/demo-protected.log
```

---

## 7. 云安全组（阿里云示例）

在「入方向」为 **`OPEN_PORT`** 与 **`PROTECTED_PORT`** 各增加一条 **TCP 放行**（演示期可源 `0.0.0.0/0`，以便对比本机防火墙策略；生产环境建议收紧到固定 IP）。

仅改系统防火墙而不放开安全组时，外网一律不可达。

---

## 8. 功能测试

以下假设：

- 服务器公网 IP 为 `YOUR_SERVER_IP`
- `OPEN_PORT=38080`，`PROTECTED_PORT=39090`
- 电脑公网 IP **不在** `mobile_allow` 白名单内

### 8.1 PC 端：应对照扫出开放端口、扫不出受保护端口

在 **电脑** 上：

```bash
chmod +x scan_port.sh
./scan_port.sh YOUR_SERVER_IP 38080 39090
```

**预期（典型）：**

```text
OPEN     38080
FILTERED 39090
```

或使用 Python：

```bash
python3 pc_scan.py YOUR_SERVER_IP 38080 39090
```

### 8.2 手机浏览器：两端口均可访问（白名单为手机出口 IP）

在手机 **蜂窝网络** 下访问：

- `http://YOUR_SERVER_IP:38080/` → 应看到 `OPEN_PORT_OK` 或对应页面  
- `http://YOUR_SERVER_IP:39090/` → 应看到 `PROTECTED_PORT_OK` 或对应页面  

若第二端口仍不可达，优先检查：**手机当前公网 IP 是否已变**、是否误连 Wi‑Fi、安全组是否放行 `39090`。

### 8.3 持续轮询（可选）

将 `lab_probe_client.py` 内 `PORTS` 改为你的演示端口后：

```bash
python3 lab_probe_client.py YOUR_SERVER_IP 5 1.5
```

---

## 9. 结果分析

| 场景 | 开放端口（无 IP 限制） | 受保护端口（ipset 白名单 + DROP） |
|------|------------------------|-----------------------------------|
| 白名单外（PC） | 易探测为 OPEN | 通常 FILTERED / 超时，脚本不易报 OPEN |
| 白名单内（手机蜂窝） | 可访问 | 可访问 |

**结论摘要：**

- **源 IP 级别的 ACL** 可以有效实现「指定终端可达、其他来源不可探测为开放」的演示效果。  
- 自有 **`portscan-protection`** 侧重另一类能力：**高频多端口扫描等行为触发封禁**；与「单端口静态白名单」互补，部署时注意白名单与 SSH 端口配置。

---

## 10. 演示清理（可选）

按你的实际端口调整：

```bash
OPEN_PORT=38080
PROTECTED_PORT=39090

sudo pkill -f "http.server ${OPEN_PORT}" || true
sudo pkill -f "http.server ${PROTECTED_PORT}" || true

while sudo iptables -C INPUT -p tcp --dport "${PROTECTED_PORT}" -j DROP 2>/dev/null; do
  sudo iptables -D INPUT -p tcp --dport "${PROTECTED_PORT}" -j DROP
done
while sudo iptables -C INPUT -p tcp --dport "${PROTECTED_PORT}" -m set --match-set mobile_allow src -j ACCEPT 2>/dev/null; do
  sudo iptables -D INPUT -p tcp --dport "${PROTECTED_PORT}" -m set --match-set mobile_allow src -j ACCEPT
done

sudo ipset destroy mobile_allow 2>/dev/null || true
```

---

## 11. 常见问题

### 11.1 `curl 127.0.0.1` 为 `Connection refused`

说明本机 **没有进程监听该端口**。先执行 `./setup_demo.sh`，再用 `sudo ss -lntp` 确认；若仍失败，查看 `/tmp/demo-*.log` 是否含 `Address already in use` 或 Python 报错。

### 11.2 手机能开 `38080` 但开不了 `39090`

多为 **手机出口 IP 已变化** 与 `PHONE_IP` 不一致。重新查询手机公网 IP 后执行：

```bash
sudo ipset add mobile_allow 新IP -exist
# 可选：从集合中删除旧 IP
# sudo ipset del mobile_allow 旧IP
```

### 11.3 `portscan-protection` 的 `--verify` 显示 service 未 active

自有组件常以 **开机执行规则** 的方式工作，`not active (will start on boot)` 在部分环境下属预期；以 **`iptables rules have been configured`**（或等价提示）与 **`--verify` 其他项** 为准。

---