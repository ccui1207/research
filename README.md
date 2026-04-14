# 安全研究仓库

本项目专注于Web应用安全防护能力的研究与测试，包含防止暴力破解和防止模糊攻击两大方向的工具集。

## 目录结构

```
research/
├── 防暴力破解能力工具/          # 防止暴力破解攻击的工具
│   ├── Aegis_tool1/            # Node.js 限速中间件
│   └── Aegis_tool2/            # Django 限速模块
│
└── 防模糊攻击能力工具/          # 防止模糊测试/Fuzzing攻击的工具
    ├── Fuzzing_Attack1/        # Go WAF 模块 (Caddy集成)
    └── Fuzzing_Attack2/        # Nginx WAF 模块
```

## 工具说明

### 防暴力破解能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Aegis_tool1 | Node.js/Express | 请求频率限制中间件，基于IP实现限速控制，支持滑动窗口算法 |
| Aegis_tool2 | Python/Django | Django限速模块，基于装饰器模式实现，支持IP和用户双维度限速 |

### 防模糊攻击能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Fuzzing_Attack1 | Go/Caddy | Web应用防火墙模块，集成规则引擎实现请求检测与拦截 |
| Fuzzing_Attack2 | C/Nginx | Nginx安全防护模块，基于特征库识别SQL注入、XSS等攻击 |

## 快速开始

### 防暴力破解

**Aegis_tool1**

```bash
cd 防暴力破解能力工具/Aegis_tool1
npm install
# 参考source目录下的示例进行集成
```

**Aegis_tool2**

```bash
cd 防暴力破解能力工具/Aegis_tool2
# 参考README.md中的Django项目配置示例
```

### 防模糊攻击

**Fuzzing_Attack1**

```bash
cd 防模糊攻击能力工具/Fuzzing_Attack1
go mod download
# 参考example目录下的使用示例
```

**Fuzzing_Attack2**

```bash
cd 防模糊攻击能力工具/Fuzzing_Attack2
# 需要编译Nginx并加载Naxsi模块，参考README.md进行配置
```

## 测试场景

### 暴力破解测试

- 同一IP同一用户集中尝试
- 不同IP同一用户分布式尝试
- 不同IP不同用户低频分布式尝试

### 模糊攻击测试

- 随机异常字符参数 fuzzing
- SQL注入/XSS等常见Web攻击向量
- 规则学习模式与拦截模式切换

## 环境要求

- Node.js >= 16 (Aegis_tool1)
- Python 3.11+ / Django 4.x (Aegis_tool2)
- Go 1.20+ (Fuzzing_Attack1)
- Nginx + Naxsi 模块 (Fuzzing_Attack2)
