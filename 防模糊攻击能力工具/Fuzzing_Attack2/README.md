Fuzzing_Attack2 本地运行与防模糊攻击测试 README

> 说明：
> - 本文档 **不包含安装过程**。
> - 默认你已经具备：可用的 Nginx、已加载好的 Naxsi 模块、Python3 环境。
> - 本文档基于本机实际测试路径编写。
---
1. 本地环境约定
1.1 Fuzzing_Attack2 源码目录
```bash
~/research/防模糊攻击能力工具/Fuzzing_Attack2
```
目录中关键部分：
`naxsi_rules/`：规则文件目录
`naxsi_rules/naxsi_core.rules`：核心规则
`naxsi_rules/blocking/`：阻断相关规则
`docker/`：参考 nginx 配置
`unit-tests/`：参考测试配置与测试用例
1.2 本地后端服务
Flask 后端运行在：
```bash
127.0.0.1:8080
```
1.3 Fuzzing_Attack2 测试站点
Nginx + Fuzzing_Attack2 对外监听：
```bash
127.0.0.1:8081
```
---
2. 先准备本地测试后端
测试 Fuzzing_Attack2 前，需要一个后端服务供 Nginx 反向代理。
2.1 后端目录
```bash
mkdir -p ~/research/防模糊攻击能力工具/test-backend
cd ~/research/防模糊攻击能力工具/test-backend
```
2.2 创建 `app.py`
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def index():
    return jsonify({
        "method": request.method,
        "path": request.path,
        "args": request.args.to_dict(flat=False),
        "form": request.form.to_dict(flat=False),
        "json": request.get_json(silent=True)
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)
```
2.3 启动后端
如果之前没有虚拟环境，可以先创建：
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask requests
python3 app.py
```
正常启动后会看到：
```text
Running on http://127.0.0.1:8080
```
这个终端不要关闭。
---
3. 配置 Fuzzing_Attack2 本地测试站点
3.1 全局加载核心规则
`naxsi_core.rules` 中包含大量 `MainRule`，它们 不能放在 `server {}` 或 `location {}` 中，而应该放在 `http {}` 级别。
因此，建议通过 `/etc/nginx/conf.d/` 引入：
```bash
cat <<'EOF' | sudo tee /etc/nginx/conf.d/naxsi-main.conf
include /home/cc/research/防止模糊攻击/Fuzzing_Attack2/naxsi_rules/naxsi_core.rules;
include /home/cc/research/防止模糊攻击/Fuzzing_Attack2/naxsi_rules/blocking/*.rules;
EOF
```
3.2 创建本地测试站点
编辑：
```bash
sudo nano /etc/nginx/sites-available/naxsi-local-test
```
写入：
```nginx
server {
    listen 8081 default_server;
    server_name naxsi-local-test;

    access_log /var/log/nginx/naxsi-access.log;
    error_log  /var/log/nginx/naxsi-error.log info;

    set $naxsi_json_log 1;
    set $naxsi_extensive_log 1;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        SecRulesEnabled;
        LearningMode;

        LibInjectionSql;
        LibInjectionXss;

        DeniedUrl "/RequestDenied";

        CheckRule "$SQL >= 8" BLOCK;
        CheckRule "$RFI >= 8" BLOCK;
        CheckRule "$TRAVERSAL >= 4" BLOCK;
        CheckRule "$EVADE >= 4" BLOCK;
        CheckRule "$XSS >= 8" BLOCK;
        CheckRule "$LIBINJECTION_SQL >= 8" BLOCK;
        CheckRule "$LIBINJECTION_XSS >= 8" BLOCK;
    }

    location /RequestDenied {
        internal;
        return 403;
    }
}
```
3.3 启用站点
```bash
sudo ln -sf /etc/nginx/sites-available/naxsi-local-test /etc/nginx/sites-enabled/naxsi-local-test
```
3.4 移除旧测试站点（避免 8081 冲突）
如果之前存在旧的 `naxsi-test`，先关闭：
```bash
sudo rm -f /etc/nginx/sites-enabled/naxsi-test
```
---
4. 运行 Fuzzing_Attack2
4.1 检查 Nginx 配置
```bash
sudo nginx -t
```
正常结果：
```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```
4.2 重载 Nginx
```bash
sudo systemctl reload nginx
```
4.3 确认 8081 已监听
```bash
sudo ss -ltnp | grep 8081
```
如果看到 `nginx` 监听 `0.0.0.0:8081`，说明 Fuzzing_Attack2 测试站点已经运行。
---
5. 基础联通测试
5.1 正常请求测试
```bash
curl -i "http://127.0.0.1:8081/?q=hello"
```
5.2 预期结果
返回 `200 OK`
响应体是 Flask 返回的 JSON
示例：
```text
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
Content-Type: application/json

{"args":{"q":["hello"]},"form":{},"json":null,"method":"GET","path":"/"}
```
这说明：
Nginx + Fuzzing_Attack2 → Flask 链路正常工作。
---
6. 单条防模糊攻击测试
6.1 测试简单异常参数
```bash
curl -i "http://127.0.0.1:8081/?a=<>"
```
6.2 LearningMode 开启时的预期
如果当前配置还保留：
```nginx
LearningMode;
```
那么此时常见现象是：
请求返回 `200`
但会在日志中记录规则命中
这一步的意义不是拦截，而是确认：
Naxsi 已经识别到了异常参数。
---
7. 查看 Fuzzing_Attack2 命中日志
开一个终端：
```bash
sudo tail -f /var/log/nginx/naxsi-error.log | grep -E 'NAXSI_FMT|NAXSI_EXLOG|"id"'
```
再发送一次异常请求：
```bash
curl -i "http://127.0.0.1:8081/?a=<>"
```
7.1 实际测试中出现过的典型日志
```text
*9 {"ip":"127.0.0.1","server":"127.0.0.1","rid":"...","uri":"/","id":1303,"zone":"ARGS","var_name":"a","content":"<>"}, client: 127.0.0.1, server: naxsi-local-test, request: "GET /?a=<> HTTP/1.1", host: "127.0.0.1:8081"
```
这说明：
当前命中的是 `naxsi-local-test`
命中区域：`ARGS`
参数名：`a`
参数内容：`<>`
规则 ID：`1303`
也就是说：
Fuzzing_Attack2 已经成功识别异常参数，只是当前处于 LearningMode，所以还未拦截。
---
8. 切换到真实拦截模式
编辑站点配置：
```bash
sudo nano /etc/nginx/sites-available/naxsi-local-test
```
把：
```nginx
LearningMode;
```
改成：
```nginx
# LearningMode;
```
然后重新加载：
```bash
sudo nginx -t
sudo systemctl reload nginx
```
再次测试：
```bash
curl -i "http://127.0.0.1:8081/?a=<>"
```
8.1 预期结果
```text
HTTP/1.1 403 Forbidden
```
这一步说明：
Fuzzing_Attack2 已从“记录模式”切换到“真实拦截模式”。
---
9. 批量 fuzz 测试（防模糊攻击能力测试核心）
在 Fuzzing_Attack2 源码目录中创建脚本：
```bash
cd ~/research/防模糊攻击能力工具/Fuzzing_Attack2
```
创建 `fuzz_simple.py`：
```python
import random
import string
import requests
import time

TARGET = "http://127.0.0.1:8081/"
ALPHABET = string.ascii_letters + string.digits + "<>|'\"`(){}[];,:$#@!^&*+-_=~/\\"

def rand_text(n):
    return "".join(random.choice(ALPHABET) for _ in range(n))

blocked = 0
allowed = 0

for i in range(50):
    payload = rand_text(64)
    try:
        r = requests.get(TARGET, params={"fuzz": payload}, timeout=5)
        print(i, r.status_code, payload)
        if r.status_code == 403:
            blocked += 1
        else:
            allowed += 1
    except Exception as e:
        print(i, "ERROR", e)
    time.sleep(0.05)

print("\n=== Summary ===")
print("allowed:", allowed)
print("blocked:", blocked)
```
9.1 安装 requests（如未安装）
```bash
python3 -m pip install requests
```
9.2 运行 fuzz 测试
```bash
python3 fuzz_simple.py
```
这个脚本模拟：
大量随机字符
高符号密度
非预期参数输入
也就是“模糊攻击”测试流量。
---
10. 测试结果统计
10.1 统计 fuzz 请求返回码
```bash
grep '"GET /?fuzz=' /var/log/nginx/naxsi-access.log | awk '{print $9}' | sort | uniq -c
```
10.2 统计 fuzz 参数命中的规则 ID
```bash
grep '"var_name":"fuzz"' /var/log/nginx/naxsi-error.log | grep -o '"id":[0-9]*' | sort | uniq -c
```
10.3 结果判断
如果出现类似：
```text
50 403
```
说明：
50 条随机 fuzz 请求
全部被 Naxsi 拦截
这就可以说明：
Naxsi 具备对随机异常参数的识别与拦截能力，即具备一定的防模糊攻击能力。
---
11. 一次性执行顺序（推荐）
终端 1：运行 Flask 后端
```bash
cd ~/research/防模糊攻击能力工具/test-backend
source venv/bin/activate
python3 app.py
```
终端 2：检查并运行 Nginx / Naxsi
```bash
sudo nginx -t
sudo systemctl reload nginx
sudo ss -ltnp | grep 8081
```
终端 3：看 Naxsi 命中日志
```bash
sudo tail -f /var/log/nginx/naxsi-error.log | grep -E 'NAXSI_FMT|NAXSI_EXLOG|"id"'
```
终端 4：做单条验证与 fuzz 测试
```bash
curl -i "http://127.0.0.1:8081/?q=hello"
curl -i "http://127.0.0.1:8081/?a=<>"
python3 ~/research/防止模糊攻击/naxsi/fuzz_simple.py
```
测试后统计
```bash
grep '"GET /?fuzz=' /var/log/nginx/naxsi-access.log | awk '{print $9}' | sort | uniq -c
grep '"var_name":"fuzz"' /var/log/nginx/naxsi-error.log | grep -o '"id":[0-9]*' | sort | uniq -c
```
---
12. 可直接写进实验报告的结论
```text
在本地环境下，利用 Nginx 加载 Naxsi 模块，并通过 Flask 构建测试后端。实验中，正常请求可被正常代理转发；异常参数 a=<> 在 LearningMode 开启时能够触发 Naxsi 规则命中并记录日志，在关闭 LearningMode 后返回 403 Forbidden。进一步通过 Python 脚本生成 50 组随机特殊字符参数进行 fuzz 测试，可观察到大量 403 响应，同时 error log 中记录了 ARGS 区域的规则命中信息，说明 Naxsi 具备对随机异常输入的识别与拦截能力，具有一定的防模糊攻击效果。
```
---
13. 注意事项
`naxsi_core.rules` 必须放在 http 级别 加载，不能直接放进 `location {}`。
如果 `a=<>` 返回 200，但日志里已经看到规则命中，通常说明还开着 `LearningMode`。
如果 8081 上存在多个测试站点，可能会出现命中错误 server 的情况，应保证测试站点唯一。
建议将 Naxsi 专用日志拆分为单独文件，例如：
`/var/log/nginx/naxsi-access.log`
`/var/log/nginx/naxsi-error.log`
