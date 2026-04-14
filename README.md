# 安全研究仓库

本项目专注于Web应用安全防护能力的研究与测试，包含防止暴力破解和防止模糊攻击两大方向的工具集。

## 目录结构

```
research/
├── 防暴力破解能力工具/          # 防止暴力破解攻击的工具
│   ├── Aegis_tool1/            # Express.js Rate Limit - Node.js Express限速中间件
│   └── Aegis_tool2/            # Django Ratelimit - Django框架限速库
│
└── 防模糊攻击能力工具/          # 防止模糊测试/Fuzzing攻击的工具
    ├── Fuzzing_Attack1/         # Coraza Caddy - Go语言WAF的Caddy服务器集成
    └── Fuzzing_Attack2/         # Naxsi - Nginx WAF模块 (基于libinjection)
```

## 工具说明

### 防暴力破解能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Aegis_tool1 | Node.js/Express | 基于IP的请求限速中间件，支持自定义限速规则和窗口期配置 |
| Aegis_tool2 | Python/Django | Django框架的限速装饰器，支持IP和用户维度限速，可对接Redis存储 |

### 防模糊攻击能力工具

| 工具 | 技术栈 | 功能描述 |
|------|--------|----------|
| Fuzzing_Attack1 | Go/Caddy | Coraza WAF的Caddy模块，支持规则引擎和请求拦截 |
| Fuzzing_Attack2 | C/Nginx | Naxsi是Nginx的Web应用防火墙模块，基于签名库检测恶意请求 |

## 快速开始

### 防暴力破解

**Aegis_tool1 (Express.js)**

```bash
cd 防暴力破解能力工具/Aegis_tool1
npm install
# 参考source目录下的示例进行集成
```

**Aegis_tool2 (Django)**

```bash
cd 防暴力破解能力工具/Aegis_tool2
# 参考README.md中的Django项目配置示例
```

### 防模糊攻击

**Fuzzing_Attack1 (Coraza)**

```bash
cd 防模糊攻击能力工具/Fuzzing_Attack1
go mod download
# 参考example目录下的使用示例
```

**Fuzzing_Attack2 (Naxsi)**

```bash
cd 防模糊攻击能力工具/Fuzzing_Attack2
# 需要编译Nginx并加载Naxsi模块，参考README.md进行配置
```

## 技术架构概览

```
                    Web请求
                        │
          ┌─────────────┴─────────────┐
          │                           │
    ┌─────▼─────┐             ┌──────▼──────┐
    │  限速层   │             │    WAF层    │
    │ (应用层)  │             │  (网关层)   │
    └───────────┘             └─────────────┘
         │                          │
   Aegis_tool1                Fuzzing_Attack1
   Aegis_tool2                Fuzzing_Attack2
```

- **限速层**: 在应用层通过中间件/装饰器实现请求频率控制
- **WAF层**: 在网关层通过规则匹配识别并拦截恶意请求

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

## 注意事项

- 各子项目内有独立的README文档，包含详细的使用说明
- 部分工具需要额外的系统依赖（如Redis、Nginx编译等）
- 测试时请遵守法律法规，仅在授权环境下进行安全研究