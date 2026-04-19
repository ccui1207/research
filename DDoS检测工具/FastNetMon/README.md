# FastNetMon 实验与验证（安装版/非源码编译）

## 1. 项目目标

在 WSL2 的 Ubuntu 上安装并运行 FastNetMon Community Edition，完成：

- 配置监控网段 `/etc/networks_list`
- 启用镜像抓包（AF_PACKET）并在 `eth0` 上采集
- 通过日志与脚本触发，验证检测与响应链路可用

说明：本项目不包含 FastNetMon 源码编译，提交的是安装/配置/验证过程与材料。

## 2. 实验环境（当前机器）

- Ubuntu（WSL2）：Ubuntu 24.04.4 LTS（Release 24.04，Codename noble）
- FastNetMon：Version 1.2.9 a2d2d0d7
- 网卡：`eth0`
- IP：`172.22.207.138/20`

## 3. 安装（官方安装器）

```bash
sudo apt-get update
sudo apt-get install -y wget
wget https://install.fastnetmon.com/installer -O installer
sudo chmod +x installer
sudo ./installer -install_community_edition
fastnetmon --version
```

## 4. 配置

### 4.1 监控网段（/etc/networks_list）

查看网卡与 IP：

```bash
ip -br a
```

写入监控网段（与当前 `eth0` 地址 `172.22.207.138/20` 对应的 /20 网段一致）：

```bash
echo '172.22.192.0/20' | sudo tee /etc/networks_list
```

重启并确认服务状态：

```bash
sudo service fastnetmon restart
sudo service fastnetmon status
```

确认文件内容：

```bash
cat /etc/networks_list
```

### 4.2 镜像抓包与监听网卡（/etc/fastnetmon.conf）

检查关键项：

```bash
grep -nE '^(mirror_afpacket|interfaces)\b' /etc/fastnetmon.conf
```

目标语义：

- `mirror_afpacket = on`
- `interfaces = eth0`

修改后重启：

```bash
sudo service fastnetmon restart
```

确认 AF_PACKET 监听接口（日志里应出现 `eth0`）：

```bash
sudo tail -n 200 /var/log/fastnetmon.log | grep -aEi 'AF_PACKET will listen on'
```

## 5. 验证

### 5.1 tcpdump 验证网卡有流量

```bash
sudo timeout 10 tcpdump -i eth0 -c 30
```

### 5.2 FastNetMon 实时界面

```bash
sudo fastnetmon_client
```

### 5.3 造一点流量（验证统计会变化）

```bash
ping -c 50 8.8.8.8
curl -s https://example.com > /dev/null
```

### 5.4 触发告警事件（与阈值相关）

查看日志中的告警相关关键字（日志可能包含非文本字符，使用 `-a` 强制按文本处理）：

```bash
sudo tail -f /var/log/fastnetmon.log | grep -aEi 'attack|ban|threshold|dos|ddos'
```

造流量示例：

```bash
sudo ping -i 0.002 8.8.8.8
```

看到关键事件后按 `Ctrl+C` 停止。

## 6. 脚本触发（notify_about_attack.sh）

FastNetMon 调用脚本时会传参（典型含义）：

- `$1`：被攻击 IP（incoming）或攻击源 IP（outgoing）
- `$2`：方向 incoming/outgoing
- `$3`：强度（pps）
- `$4`：动作 ban/unban

注意：脚本里通常需要读取 stdin（常见写法是保留 `cat`），不要随意删除。

## 7. 本目录建议结构

- `README.md`：本说明
- `docs/`：可选，放更完整的过程记录（例如 Word 文档）
- `scripts/`：可选，放你修改后的脚本
- `evidence/`：可选，放脱敏后的关键日志片段（见 `evidence/README.txt`）

## 8. 脱敏要求

不提交明文密码、token、密钥；日志与配置片段请脱敏后再提交。

## 9. 靶场复现（可选）：network namespace + veth + iperf3

这一节对应“在隔离环境里模拟体量型攻击特征”，用来在日志里形成更完整的证据链（例如 `detected attack`、`incoming attack`、`Call script for ban client` 等）。**不要在真实公网/他人网络上做压测**。

### 9.1 你会得到什么拓扑（概念）

- 两个 network namespace：`ns1`、`ns2`
- 一对 `veth`：`veth0` ↔ `veth1`（一端放进 `ns1`，另一端放进 `ns2`）
- 在 `ns1/ns2` 内配置 `10.10.10.0/24` 这类地址
- 用 `iperf3` 在 `ns2 → ns1` 打 UDP 流量，让 pps/Mbps 上升
- FastNetMon 监听 `veth0`（在 host 侧或指定命名空间里，取决于你怎么挂接口），并配合阈值触发告警

> 说明：不同课堂/实验脚本对 namespace 命名、接口落在哪个 namespace、以及 FastNetMon 进程所在 network namespace 可能不同。下面给的是“最常见可复用骨架”。如果你发现 `veth0` 在 `ip -br a` 里不可见，优先以你实验脚本为准。

### 9.2 前置条件

```bash
sudo apt-get update
sudo apt-get install -y iperf3 iproute2
```

### 9.3 创建 netns + veth，并配置地址（示例）

```bash
sudo ip netns add ns1
sudo ip netns add ns2

sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth0 netns ns1
sudo ip link set veth1 netns ns2

sudo ip netns exec ns1 ip addr add 10.10.10.1/24 dev veth0
sudo ip netns exec ns2 ip addr add 10.10.10.2/24 dev veth1

sudo ip netns exec ns1 ip link set veth0 up
sudo ip netns exec ns2 ip link set veth1 up
```

确认接口存在：

```bash
sudo ip netns exec ns1 ip -br a
sudo ip netns exec ns2 ip -br a
```

### 9.4 启动 iperf3 服务端（ns1）与客户端压测（ns2）

```bash
sudo ip netns exec ns1 iperf3 -s -D
sudo ip netns exec ns2 iperf3 -c 10.10.10.1 -u -b 200M -l 1200 -t 30
```

### 9.5 让 FastNetMon 针对靶场网段与接口工作（要点）

靶场验证时，通常需要把监控网段切到靶场地址，并把 AF_PACKET 监听接口切到 `veth0`（以你当时实验为准）：

```bash
echo '10.10.10.0/24' | sudo tee /etc/networks_list
grep -nE '^(mirror_afpacket|interfaces)\b' /etc/fastnetmon.conf
```

然后编辑 `/etc/fastnetmon.conf`（例如 `sudo nano /etc/fastnetmon.conf`），确保最终生效的配置语义满足：

- `mirror_afpacket = on`
- `interfaces = veth0`

重启服务：

```bash
sudo service fastnetmon restart
sudo service fastnetmon status
```

确认监听接口与日志：

```bash
sudo tail -n 200 /var/log/fastnetmon.log | grep -aEi 'AF_PACKET will listen on|detected attack|Call script'
```

### 9.6 阈值与触发（概念）

告警是否触发取决于你在 `/etc/fastnetmon.conf` 里配置的阈值（例如 pps/Mbps）。靶场里常用做法是：**临时把阈值调低到演示水平**，再用 `iperf3` 打 UDP，让日志出现明确事件行。

### 9.7 实验结束后的恢复（强烈建议写进你的实验记录）

把环境切回 WSL 日常网络时，一般需要恢复：

```bash
echo '172.22.192.0/20' | sudo tee /etc/networks_list
```

并把 `/etc/fastnetmon.conf` 的 `interfaces` 恢复为 `eth0`（或你实际外网接口名），然后：

```bash
sudo service fastnetmon restart
```

清理 netns（按你实际创建的名为准）：

```bash
sudo ip netns del ns1
sudo ip netns del ns2
```
