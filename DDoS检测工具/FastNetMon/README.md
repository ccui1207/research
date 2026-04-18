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
