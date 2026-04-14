
````md
# Django `Aegis_tool2` Demo（Linux 虚拟机）

本项目用于演示 `Aegis_tool2` 的基础限速能力，并测试以下三种场景：

1. 同一 IP，同一用户  
2. 不同 IP，同一用户  
3. 不同 IP，不同用户  

---

## 1. 环境准备

建议环境：

- Ubuntu / Debian
- Python 3.11
- Redis

安装依赖：

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip redis-server
sudo systemctl enable --now redis-server
redis-cli ping
````

如果返回：

```bash
PONG
```

说明 Redis 已正常启动。

---

## 2. 创建项目

```bash
mkdir Aegis_tool2-demo
cd Aegis_tool2-demo

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install -U pip setuptools wheel
pip install django django-ratelimit django-redis

django-admin startproject demo .
python manage.py startapp authdemo
```

---

## 3. 配置 `Aegis_tool2-demo/demo/settings.py`

将 `demo/settings.py` 修改为以下关键内容。

### 3.1 修改 `ALLOWED_HOSTS`

```python
ALLOWED_HOSTS = ["*"]
```

### 3.2 注册应用

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authdemo',
]
```

### 3.3 配置 Redis 缓存

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "demo",
    }
}

RATELIMIT_USE_CACHE = "default"
```

### 3.4 配置测试环境下的 IP 获取方式

用于“不同 IP”模拟测试：

```python
RATELIMIT_IP_META_KEY = lambda r: (
    r.META.get("HTTP_X_TEST_CLIENT_IP") or r.META.get("REMOTE_ADDR")
)
```

### 3.5 配置日志

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "authdemo.log",
            "formatter": "simple",
            "level": "INFO",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO",
        },
    },
    "loggers": {
        "authdemo": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        }
    },
}
```

---

## 4. 编写登录视图

将 `authdemo/views.py` 替换为：

```python
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger("authdemo")

# 测试账号
USER_DB = {
    "alice": "correct123"
}

@csrf_exempt
@require_POST
@ratelimit(key="ip", rate="20/m", method="POST", block=False)
@ratelimit(key="post:username", rate="5/m", method="POST", block=False)
def login_view(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    ip = request.META.get("HTTP_X_TEST_CLIENT_IP", request.META.get("REMOTE_ADDR", ""))
    ua = request.META.get("HTTP_USER_AGENT", "")

    if getattr(request, "limited", False):
        logger.warning("login_limited username=%s ip=%s ua=%s", username, ip, ua)
        return JsonResponse(
            {"ok": False, "msg": "too many login attempts"},
            status=429
        )

    real_password = USER_DB.get(username)
    if real_password is None or real_password != password:
        logger.info("login_failed username=%s ip=%s ua=%s", username, ip, ua)
        return JsonResponse(
            {"ok": False, "msg": "invalid credentials"},
            status=401
        )

    logger.info("login_success username=%s ip=%s ua=%s", username, ip, ua)
    return JsonResponse(
        {"ok": True, "msg": "login success"},
        status=200
    )
```

---

## 5. 配置路由

### 5.1 新建 `authdemo/urls.py`

```python
from django.urls import path
from .views import login_view

urlpatterns = [
    path("login/", login_view, name="login"),
]
```

### 5.2 修改 `demo/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("authdemo.urls")),
]
```

---

## 6. 启动项目

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

启动成功后会看到：

```bash
Starting development server at http://0.0.0.0:8000/
```

---

## 7. 测试

测试时建议新开一个终端：

```bash
cd Aegis_tool2-demo
source .venv/bin/activate
```

---

### 7.1 同一 IP，同一用户

```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "try=$i code=%{http_code}\n" \
    -X POST http://127.0.0.1:8000/login/ \
    -d "username=alice&password=wrong$i"
done
```

#### 预期结果

* 前几次返回 `401`
* 后面返回 `429`

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

---

### 7.2 不同 IP，同一用户

为了避免上一组测试影响本组结果，建议先等待 65 秒：

```bash
sleep 65
```

然后执行：

```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "ip=10.0.0.$i code=%{http_code}\n" \
    -H "X-Test-Client-IP: 10.0.0.$i" \
    -X POST http://127.0.0.1:8000/login/ \
    -d "username=alice&password=wrong$i"
done
```

#### 预期结果

* 前几次返回 `401`
* 后面返回 `429`

说明：即使来源 IP 改变，只要目标仍是同一用户名，系统仍能触发用户名维度限速。

---

### 7.3 不同 IP，不同用户

同样建议先等待 65 秒：

```bash
sleep 65
```

然后执行：

```bash
for i in $(seq 1 8); do
  curl -s -o /dev/null -w "ip=10.0.0.$i user=user$i code=%{http_code}\n" \
    -H "X-Test-Client-IP: 10.0.0.$i" \
    -X POST http://127.0.0.1:8000/login/ \
    -d "username=user$i&password=wrong$i"
done
```

#### 预期结果

* 大多数返回 `401`
* 不容易快速出现 `429`

说明：对于“不同 IP + 不同用户名”的低频分布式尝试，当前这种基础限速策略不容易单独防住。

---

### 7.4 正常登录测试

等待 65 秒后执行：

```bash
curl -i -X POST http://127.0.0.1:8000/login/ \
  -d "username=alice&password=correct123"
```

#### 预期结果

```bash
HTTP/1.1 200 OK
```

响应体：

```json
{"ok": true, "msg": "login success"}
```

---

## 8. 查看日志

```bash
tail -f authdemo.log
```

日志中可看到：

* `login_failed`
* `login_limited`
* `login_success`

---

## 9. 结果说明

本 demo 可以验证以下结论：

* 能防御“同一 IP、同一用户”的集中式爆破
* 能一定程度防御“不同 IP、同一用户”的针对性尝试
* 对“不同 IP、不同用户”的低频分布式尝试，单靠当前基础限速能力有限

---
