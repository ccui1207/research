
````md
# Express `express-rate-limit` 本地改装版 Demo（Linux 虚拟机）

本项目用于验证 `express-rate-limit` ，并测试以下三种场景：

1. 同一 IP，同一用户  
2. 不同 IP，同一用户  
3. 不同 IP，不同用户  

本 README 采用“**本地源码编译 + Express Demo 引用本地 dist 文件**”的方式进行验证。

---

## 1. 目录说明

当前有两个目录：

-  `express-rate-limit` 仓库：  
  `/home/cc/research/防止爆破攻击/express-rate-limit`

- 用于测试的 Express demo：  
  `/home/cc/test/express-rate-limit-demo`

如果你的实际路径不同，请自行替换。

---

## 2. 环境要求

建议环境：

- Ubuntu / Debian
- Node.js 18 及以上
- npm 可用

检查版本：

```bash
node -v
npm -v
````

---

## 3.  `express-rate-limit` 仓库说明

当前保留的核心文件包括：

### 根目录

* `package.json`
* `tsconfig.json`
* `pnpm-lock.yaml`
* `jest.config.json`
* `biome.json`

### 目录

* `source/`
* `test/`

### `source/` 目录中

* `index.ts`
* `rate-limit.ts`
* `memory-store.ts`
* `ip-key-generator.ts`
* `headers.ts`
* `utils.ts`
* `types.ts`
* `validations.ts`

说明：核心运行逻辑源码仍在。

---

## 4. 安装依赖并编译本地仓库

进入本地改装后的仓库目录：

```bash
cd /home/cc/research/防止爆破攻击/express-rate-limit
```

### 4.1 安装依赖（跳过 Puppeteer 下载）

由于开发依赖中可能包含 `puppeteer`，安装会比较慢，因此建议使用以下方式跳过浏览器下载和安装脚本：

```bash
rm -rf node_modules package-lock.json
PUPPETEER_SKIP_DOWNLOAD=true npm install --ignore-scripts
```

### 4.2 编译运行时代码

```bash
npm run compile
```

说明：

* `build:cjs` 会生成 `dist/index.cjs`
* `build:esm` 会生成 `dist/index.mjs`
* `build:types` 可能因为类型环境问题失败

如果 `build:types` 失败，但 `dist/index.cjs` 和 `dist/index.mjs` 已经生成，则**仍可继续进行 JS demo 测试**。

### 4.3 检查编译结果

```bash
ls dist
```

正常情况下至少应看到：

```bash
index.cjs
index.mjs
```

如果这两个文件存在，说明本地改装版的**运行时代码已可用**。

---

## 5. 创建测试 Demo

进入测试目录：

```bash
mkdir -p /home/cc/test/express-rate-limit-demo
cd /home/cc/test/express-rate-limit-demo
```

初始化项目并安装 Express：

```bash
npm init -y
npm install express
```

---

## 6. 编写测试服务

新建 `server.mjs`，内容如下：

```js
import express from 'express'
import { rateLimit } from '/home/cc/research/防止爆破攻击/express-rate-limit/dist/index.mjs'

const app = express()
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// 仅用于本地测试“不同 IP”
// 正式部署时应根据真实代理链正确设置
app.set('trust proxy', 1)

// 测试账号
const USERS = {
  alice: 'correct123',
}

// 1) 按 IP 限速：同一 IP 1 分钟最多 10 次登录请求
const loginIpLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 10,
  standardHeaders: 'draft-8',
  legacyHeaders: false,
  message: {
    ok: false,
    msg: 'too many login attempts from this IP',
  },
})

// 2) 按用户名限速：同一用户名 1 分钟最多 5 次失败尝试
const loginUserLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 5,
  standardHeaders: 'draft-8',
  legacyHeaders: false,

  // 成功登录不计入用户名爆破次数
  skipSuccessfulRequests: true,

  keyGenerator: (req) => {
    const username = String(req.body.username || '').trim().toLowerCase()
    return `login-user:${username || 'empty'}`
  },

  message: {
    ok: false,
    msg: 'too many attempts for this username',
  },
})

app.get('/', (req, res) => {
  res.json({ ok: true, msg: 'server is up' })
})

app.get('/ip', (req, res) => {
  res.json({
    ip: req.ip,
    xff: req.headers['x-forwarded-for'] || null,
  })
})

app.post('/login', loginIpLimiter, loginUserLimiter, (req, res) => {
  const username = String(req.body.username || '').trim().toLowerCase()
  const password = String(req.body.password || '')

  const realPassword = USERS[username]
  if (!realPassword || realPassword !== password) {
    return res.status(401).json({
      ok: false,
      msg: 'invalid credentials',
    })
  }

  return res.status(200).json({
    ok: true,
    msg: 'login success',
  })
})

app.listen(3000, () => {
  console.log('listening on http://0.0.0.0:3000')
})
```

---

## 7. 启动测试服务

```bash
cd /home/cc/test/express-rate-limit-demo
node server.mjs
```

正常启动后会看到：

```bash
listening on http://0.0.0.0:3000
```

---

## 8. 基础连通性测试

新开一个终端执行：

```bash
curl -i http://127.0.0.1:3000/
curl -s http://127.0.0.1:3000/ip
```

如果能返回 JSON，说明服务正常。

---

## 9. 功能测试

## 9.1 同一 IP，同一用户

```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "try=$i code=%{http_code}\n" \
    -X POST http://127.0.0.1:3000/login \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"alice\",\"password\":\"wrong$i\"}"
done
```

### 预期结果

* 前几次：`401`
* 后面：`429`

示例：

```bash
try=1 code=401
try=2 code=401
try=3 code=401
try=4 code=401
try=5 code=401
try=6 code=429
try=7 code=429
try=8 code=429
```

说明：
同一来源持续尝试同一账号时，系统可触发限速。

---

## 9.2 不同 IP，同一用户

为了避免上一组测试影响本组结果，建议先等待 65 秒：

```bash
sleep 65
```

先验证“不同 IP”模拟是否生效：

```bash
curl -s -H "X-Forwarded-For: 10.0.0.123" http://127.0.0.1:3000/ip
```

若返回结果中的 `ip` 变为 `10.0.0.123`，说明模拟成功。

然后执行测试：

```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "ip=10.0.0.$i code=%{http_code}\n" \
    -H "X-Forwarded-For: 10.0.0.$i" \
    -H 'Content-Type: application/json' \
    -X POST http://127.0.0.1:3000/login \
    -d "{\"username\":\"alice\",\"password\":\"wrong$i\"}"
done
```

### 预期结果

* 前几次：`401`
* 后面：`429`

说明：
即使攻击 IP 改变，只要目标仍为同一用户名，系统仍可通过用户名维度进行限制。

---

## 9.3 不同 IP，不同用户

同样建议先等待 65 秒：

```bash
sleep 65
```

然后执行：

```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "ip=10.0.0.$i user=user$i code=%{http_code}\n" \
    -H "X-Forwarded-For: 10.0.0.$i" \
    -H 'Content-Type: application/json' \
    -X POST http://127.0.0.1:3000/login \
    -d "{\"username\":\"user$i\",\"password\":\"wrong$i\"}"
done
```

### 预期结果

* 大多数：`401`
* 不容易快速出现 `429`

说明：
面对“不同 IP + 不同用户”的低频分布式尝试，当前这种基础限速策略不容易单独防住。

---

## 9.4 正常登录测试

等待 65 秒后执行：

```bash
curl -i -X POST http://127.0.0.1:3000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"correct123"}'
```

### 预期结果

```bash
HTTP/1.1 200 OK
```

响应体类似：

```json
{"ok": true, "msg": "login success"}
```

---

## 10. 结果分析

通过以上三组测试，可以得到以下结论：

### 能较好拦截的情况

* 同一 IP，同一用户
* 不同 IP，同一用户

### 不擅长单独拦截的情况

* 不同 IP，不同用户
* 低频分布式尝试

---

## 11. 关于 `build:types` 失败的说明

如果执行 `npm run compile` 时出现 `build:types` 失败，但 `dist/index.cjs` 和 `dist/index.mjs` 已经生成，则：

* 说明运行时代码已编译成功
* 当前仅是类型声明生成失败
* 不影响本 README 中基于 Node.js 的 JS demo 测试


---
