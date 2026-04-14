Fuzzing_Attack1 本地运行与防模糊攻击测试 README
1. 说明
本文档记录 在本地源码目录中重新生成 `build/caddy`，并完成 Fuzzing_Attack1 防模糊攻击能力测试 的完整过程。
本文档只包含：
运行流程
配置文件准备
正常请求测试
异常参数测试
模糊攻击（fuzz）测试
日志查看与结果判断
不包含安装过程。默认你已经具备以下条件：
`go` 已可用，且为较新版本
`xcaddy` 已可用
`coraza-caddy` 源码已在本地
Python3 可用
---
2. 本次测试目录约定
Coraza 源码目录
```bash
~/research/防止模糊攻击/coraza-caddy
```
测试后端目录
```bash
~/research/防止模糊攻击/test-backend
```
端口约定
Flask 后端：`127.0.0.1:8080`
Coraza-Caddy：`127.0.0.1:8082`
说明：
这里使用 `8082` 是为了避免与前面其他本地服务（如 Nginx/Naxsi 的 `8081`）冲突。
---
3. 生成新的 Caddy 可执行文件
进入源码目录：
```bash
cd ~/research/防止模糊攻击/Fuzzing_Attack1
```
确保当前终端使用的是正确的 Go 与 xcaddy：
```bash
export PATH=/usr/local/go/bin:$PATH
export PATH="$PATH:$(go env GOPATH)/bin"
hash -r

which go
go version
which xcaddy
xcaddy version
```
在源码目录中生成新的带 Coraza 插件的 Caddy 二进制：
```bash
/usr/local/go/bin/go run mage.go buildCaddy
```
生成成功后，产物位于：
```bash
./build/caddy
```
检查是否生成成功：
```bash
ls -l ./build/caddy
./build/caddy list-modules | grep -i coraza
```
如果 `./build/caddy` 存在，说明生成成功。
---
4. 创建测试配置文件 Caddyfile.test
在 Coraza 源码目录下创建测试用配置文件：
```bash
cat > ./Caddyfile.test <<'EOF'
{
    auto_https off
    order coraza_waf first
}

:8082 {
    coraza_waf {
        directives `
            SecRuleEngine On

            SecAuditEngine RelevantOnly
            SecAuditLog /tmp/coraza_audit.log
            SecAuditLogParts ABCFHZ

            SecRequestBodyAccess On

            SecRule ARGS:a "@contains <" \
                "id:1101,phase:2,deny,log,status:403,msg:'angle bracket in parameter a'"

            SecRule ARGS:fuzz "[<>{}|'\"()\[\];,@#$%^&*+=~\\/]" \
                "id:1102,phase:2,deny,log,status:403,msg:'suspicious fuzz characters in parameter fuzz'"
        `
    }

    reverse_proxy 127.0.0.1:8080
}
EOF
```
检查文件：
```bash
ls -l ./Caddyfile.test
cat ./Caddyfile.test
```
配置说明
`order coraza_waf first`：让 Coraza WAF 在请求处理链中优先执行。
`SecRuleEngine On`：开启规则引擎。
`SecAuditEngine RelevantOnly`：只记录相关事务。
`SecAuditLog /tmp/coraza_audit.log`：审计日志输出文件。
`SecRule ARGS:a ...`：当参数 `a` 中出现 `<` 时，直接拦截。
`SecRule ARGS:fuzz ...`：当参数 `fuzz` 中出现大量特殊字符时，直接拦截。
`reverse_proxy 127.0.0.1:8080`：将正常请求代理给 Flask 后端。
---
5. 检查配置文件语法
在 Coraza 源码目录下执行：
```bash
./build/caddy adapt --config ./Caddyfile.test --adapter caddyfile
```
如果输出 JSON 且没有 `Error:`，说明配置语法正确。
---
6. 准备并运行测试后端（Flask）
进入测试后端目录：
```bash
mkdir -p ~/research/防止模糊攻击/test-backend
cd ~/research/防止模糊攻击/test-backend
```
创建 `app.py`：
```bash
cat > app.py <<'EOF'
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
EOF
```
启动虚拟环境并运行：
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask requests
python3 app.py
```
正常应看到：
```text
Running on http://127.0.0.1:8080
```
这个终端保持开启。
---
7. 运行 Coraza-Caddy
另开一个终端，进入源码目录：
```bash
cd ~/research/防止模糊攻击/coraza-caddy
```
启动 Coraza-Caddy：
```bash
./build/caddy run --config ./Caddyfile.test --adapter caddyfile
```
这个终端也保持开启。
确认端口监听：
```bash
sudo ss -ltnp | grep 8082
```
如果看到 `8082` 被 Caddy 监听，说明 Coraza 已开始运行。
---
8. 基础联通测试
另开一个终端执行：
```bash
curl -i "http://127.0.0.1:8082/?q=hello"
```
预期结果
返回 `200 OK`
响应体是 Flask 返回的 JSON
示例：
```text
HTTP/1.1 200 OK
Content-Type: application/json
...

{"args":{"q":["hello"]},"form":{},"json":null,"method":"GET","path":"/"}
```
这说明：
Coraza + Caddy -> Flask 链路已经打通。
---
9. 单条异常参数测试
测试 1：参数 `a=<>`
```bash
curl -i "http://127.0.0.1:8082/?a=<>"
```
预期结果
```text
HTTP/1.1 403 Forbidden
```
这说明：
`SecRule ARGS:a` 规则命中
Coraza 可以对简单异常输入进行检测并拦截
---
测试 2：特殊字符 fuzz 参数
```bash
curl -i "http://127.0.0.1:8082/?fuzz=%3C%3E%7C%27%22%28%29%5B%5D%3B%2C"
```
预期结果
```text
HTTP/1.1 403 Forbidden
```
这说明：
`SecRule ARGS:fuzz` 规则命中
Coraza 能够对高符号密度、非预期字符组合进行识别与拦截
---
10. 查看 Coraza 审计日志
另开一个终端：
```bash
tail -f /tmp/coraza_audit.log
```
当规则命中时，预期可看到类似内容：
```text
Coraza: Access denied (phase 2)
[id "1102"]
[msg "suspicious fuzz characters in parameter fuzz"]
[uri "/?fuzz=..."]
```
日志中重点关注：
`Access denied (phase 2)`
`id "1101"` 或 `id "1102"`
`msg` 字段
`uri` 字段
这说明：
请求确实是被 Coraza 规则拦截
可以准确定位到命中的规则与触发内容
---
11. 批量模糊攻击测试（fuzz）
在 Coraza 源码目录中创建 `fuzz_simple.py`：
```bash
cat > ./fuzz_simple.py <<'EOF'
import random
import string
import requests
import time

TARGET = "http://127.0.0.1:8082/"
ALPHABET = string.ascii_letters + string.digits + "<>|'\"`(){}[];,:%$#@!^&*+-_=~/\\"

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
EOF
```
运行脚本：
```bash
python3 ./fuzz_simple.py
```
预期结果
最后会输出：
```text
=== Summary ===
allowed: X
blocked: Y
```
如果 `blocked` 明显大于 0，说明系统能对随机异常输入进行有效拦截。
---
12. 结果统计
统计规则 `1102` 的命中次数
```bash
grep 'id "1102"' /tmp/coraza_audit.log | wc -l
```
查看最近的 fuzz 命中记录
```bash
grep 'suspicious fuzz characters in parameter fuzz' /tmp/coraza_audit.log | tail -n 20
```
结果解释
命中次数越多，说明 fuzz 请求越多触发了规则
如果大量 fuzz 请求返回 `403`，并且日志中有对应规则命中，说明 Coraza 具备较强的防模糊攻击能力
---
13. 推荐的完整执行顺序
终端 1：运行后端
```bash
cd ~/research/防止模糊攻击/test-backend
source venv/bin/activate
python3 app.py
```
终端 2：运行 Coraza
```bash
cd ~/research/防止模糊攻击/coraza-caddy
./build/caddy adapt --config ./Caddyfile.test --adapter caddyfile
./build/caddy run --config ./Caddyfile.test --adapter caddyfile
```
终端 3：看日志
```bash
tail -f /tmp/coraza_audit.log
```
终端 4：执行测试
```bash
curl -i "http://127.0.0.1:8082/?q=hello"
curl -i "http://127.0.0.1:8082/?a=<>"
curl -i "http://127.0.0.1:8082/?fuzz=%3C%3E%7C%27%22%28%29%5B%5D%3B%2C"
python3 ~/research/防止模糊攻击/coraza-caddy/fuzz_simple.py
```
终端 5：统计结果
```bash
grep 'id "1102"' /tmp/coraza_audit.log | wc -l
grep 'suspicious fuzz characters in parameter fuzz' /tmp/coraza_audit.log | tail -n 20
```
---
14. 测试结论模板
可以将本次测试总结为：
```text
在本地源码目录中重新生成带 Coraza 插件的 Caddy 二进制后，基于自定义规则完成了 Coraza-Caddy 的运行与防模糊攻击测试。测试结果表明，正常请求能够被正确反向代理至 Flask 后端，而异常参数 a=<> 与含大量特殊字符的 fuzz 参数均返回 403 Forbidden。审计日志 /tmp/coraza_audit.log 中记录了规则 ID 1101、1102 对应的拦截信息，说明该方案能够识别并拦截随机异常输入，具备一定的防模糊攻击能力。
```
---
15. 注意事项
`./build/caddy` 是本地重新生成后的运行文件，不是系统默认 Caddy。
`Caddyfile.test` 必须放在当前源码目录中，且测试命令中的路径要一致。
`8082` 端口仅用于 Coraza 测试，避免与其他本地服务冲突。
`/tmp/coraza_audit.log` 如果历史内容过多，可先清空后再测试：
```bash
> /tmp/coraza_audit.log
```
如果需要重复测试，建议先确认 Flask 与 Caddy 两个终端都在正常运行。
