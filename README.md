# Web 应用安全防护能力研究工具集

本项目专注于 Web 应用与网络入口安全防护能力的研究、验证与演示，围绕常见攻击与扫描行为提供可复现的防护工具和实验脚本。

当前工具集覆盖以下五个方向：

- 防暴力破解能力
- 防模糊攻击能力
- 抗拒绝服务攻击能力
- 防漏洞扫描能力
- 防端口扫描能力

> 说明：本仓库内容仅用于授权测试、教学演示和防护能力验证，请在自有或明确授权的实验环境中使用。

## 目录结构

```text
research/
├── 抗拒绝服务攻击工具/                  # DDoS / 流量洪泛 / L7 挑战防护工具
│   ├── DDoSWatch/                      # 基于 FastNetMon 的检测、封禁与 nft 规则下发验证
│   ├── Restyshield/                    # OpenResty + Lua 应用层反 DDoS 挑战脚本
│   └── XDP-Shield/                     # Linux XDP/eBPF 高性能包过滤与阈值缓解
│
├── 防暴力破解能力工具/                  # 防止暴力破解攻击的工具
│   ├── Aegis_tool1/                    # Node.js 限速中间件
│   ├── Aegis_tool2/                    # Django 限速模块
│   └── 演示视频/                       # 演示材料
│
├── 防模糊攻击能力工具/                  # 防止模糊测试 / Fuzzing 攻击的工具
│   ├── Fuzzing_Attack1/                # Go WAF 模块（Caddy 集成）
│   ├── Fuzzing_Attack2/                # Nginx WAF 模块
│   └── 演示视频/                       # 演示材料
│
├── 防漏洞扫描能力工具/                  # 漏洞扫描识别与入口防护对照实验
│   ├── Anti-vulnerability scanning tool1/
│   ├── Anti-vulnerability scanning tool2/
│   └── 演示视频/                       # 演示材料
│
└── 防端口扫描能力工具/                  # 端口扫描防护与访问控制实验
    ├── pport_scan_tool1/
    ├── pport_scan_tool2/
    └── 演示视频/                       # 演示材料
```

## 工具说明

### 抗拒绝服务攻击工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| DDoSWatch | FastNetMon / nftables / tcpreplay | 通过 PCAP 回放验证流量检测、Ban list、处置脚本调用与 nft 规则下发链路 |
| Restyshield | OpenResty / Lua | 在 Nginx/OpenResty 入口执行 Lua 脚本，实现 L7 限流、挑战页、Cookie 校验与白名单配置 |
| XDP-Shield | Linux XDP / eBPF | 在网卡 XDP 入口进行协议、端口与阈值过滤，适用于高吞吐、低延迟的洪泛流量缓解实验 |

### 防暴力破解能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Aegis_tool1 | Node.js / Express | 请求频率限制中间件，基于 IP 实现限速控制，支持滑动窗口算法 |
| Aegis_tool2 | Python / Django | Django 限速模块，基于装饰器模式实现，支持 IP 和用户双维度限速 |

### 防模糊攻击能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Fuzzing_Attack1 | Go / Caddy | Web 应用防火墙模块，集成规则引擎实现请求检测与拦截 |
| Fuzzing_Attack2 | C / Nginx | Nginx 安全防护模块，基于特征库识别 SQL 注入、XSS 等攻击 |

### 防漏洞扫描能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Anti-vulnerability scanning tool1 | Python 标准库 / HTTP WAF Proxy | 通过“直连漏洞服务”和“入口代理防护”对照，验证反射型 XSS 扫描命中与 403 拦截效果 |
| Anti-vulnerability scanning tool2 | Python 标准库 / HTTP WAF Proxy | 通过“直连漏洞服务”和“入口代理防护”对照，验证反射型 XSS 扫描命中与 403 拦截效果 |

### 防端口扫描能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| pport_scan_tool1 | Bash / Python / iptables / ipset | 通过开放端口与受保护端口对照，验证基于源 IP 白名单、访问控制和可选端口扫描防护策略的效果 |
| pport_scan_tool2 | Bash / Python / iptables / ipset | 通过开放端口与受保护端口对照，验证基于源 IP 白名单、访问控制和可选端口扫描防护策略的效果 |
## 快速开始

各子工具目录均包含独立 `README.md`，建议进入对应目录查看完整部署、配置和验证步骤。

### 抗拒绝服务攻击

**DDoSWatch**

```bash
cd 抗拒绝服务攻击工具/DDoSWatch
# 参考 README.md 使用 veth + tcpreplay 回放 PCAP，验证检测、封禁与 nft 规则下发链路
```

**Restyshield**

```bash
cd 抗拒绝服务攻击工具/Restyshield
# 将 anti_ddos_challenge.lua 放入 OpenResty 可加载目录，并在 nginx.conf 中配置 access_by_lua_file
```

**XDP-Shield**

```bash
cd 抗拒绝服务攻击工具/XDP-Shield
chmod +x install.sh
./install.sh --libxdp
# 参考 README.md 配置 XDP 过滤规则与 veth 回放实验
```

### 防暴力破解

**Aegis_tool1**

```bash
cd 防暴力破解能力工具/Aegis_tool1
npm install
# 参考 source 目录下的示例进行集成
```

**Aegis_tool2**

```bash
cd 防暴力破解能力工具/Aegis_tool2
# 参考 README.md 中的 Django 项目配置示例
```

### 防模糊攻击

**Fuzzing_Attack1**

```bash
cd 防模糊攻击能力工具/Fuzzing_Attack1
go mod download
# 参考 example 目录下的使用示例
```

**Fuzzing_Attack2**

```bash
cd 防模糊攻击能力工具/Fuzzing_Attack2
# 需要编译 Nginx 并加载 Naxsi 模块，参考 README.md 进行配置
```

### 防漏洞扫描

**Anti-vulnerability scanning tool1**

```bash
cd "防漏洞扫描能力工具/Anti-vulnerability scanning tool1"
python3 -V
python3 democtl.py start-vuln
python3 scanner/scan.py --base-url http://127.0.0.1:5000
python3 democtl.py start-waf
# 再次运行扫描脚本，对比入口防护后的拦截效果
```

### 防端口扫描

**pport_scan_tool1**

```bash
cd 防端口扫描能力工具/pport_scan_tool1
python3 -V
# 按需修改 setup_demo.sh 中的 OPEN_PORT、PROTECTED_PORT、PHONE_IP
chmod +x setup_demo.sh
sudo ./setup_demo.sh
# 使用 scan_port.sh 或 pc_scan.py 对比开放端口与受保护端口
```

## 测试场景

### 抗拒绝服务攻击测试

- PCAP 回放触发流量检测、封禁名单和防火墙规则下发
- 应用层高频请求触发 OpenResty/Lua 挑战页、Cookie 校验或限流逻辑
- 基于协议、端口和 PPS 阈值的 XDP/eBPF 包过滤与丢弃统计

### 暴力破解测试

- 同一 IP 同一用户集中尝试
- 不同 IP 同一用户分布式尝试
- 不同 IP 不同用户低频分布式尝试

### 模糊攻击测试

- 随机异常字符参数 fuzzing
- SQL 注入、XSS 等常见 Web 攻击向量
- 规则学习模式与拦截模式切换

### 漏洞扫描测试

- 直连漏洞服务时扫描脚本命中反射型 XSS
- 开启入口防护代理后典型 payload 被规则拦截并返回 403
- 对比扫描结果中的 `[VULN]` 与 `[PASS]` 输出

### 端口扫描测试

- 开放端口与受保护端口的可访问性对照
- 白名单源 IP 可访问，非白名单源表现为超时或过滤
- 可选接入 `portscan-protection` 验证快速端口探测后的封禁策略

## 环境要求

- Node.js >= 16（Aegis_tool1）
- Python 3.11+ / Django 4.x（Aegis_tool2）
- Go 1.20+（Fuzzing_Attack1）
- Nginx + Naxsi 模块（Fuzzing_Attack2）
- OpenResty + Lua（Restyshield）
- Linux + sudo + FastNetMon / nftables / tcpreplay / tcpdump（DDoSWatch）
- Linux + XDP/eBPF 构建环境：clang、llvm、libelf、libconfig、bpftool、libxdp/libbpf、make（XDP-Shield）
- Python 3.8+（Anti-vulnerability scanning tool1，标准库演示）
- Linux + sudo + iptables / ipset（pport_scan_tool1）

## 使用建议

- 优先阅读各子目录下的 `README.md`，按对应实验环境执行。
- 涉及防火墙、XDP、nftables、iptables/ipset 的实验建议在虚拟机、云主机或隔离实验网络中进行。
- 执行流量回放、端口探测或漏洞扫描前，请确认目标属于自有或已授权范围。
