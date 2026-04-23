---

# APK_Check 工具说明文档

## 一、工具概述

`APK_Check` 是一个面向 Android APK 的静态安全检测工具。
该工具以 APK 文件为输入，通过对应用的 `AndroidManifest.xml`、DEX 字节码、字符串常量、签名信息等内容进行静态分析，再结合预定义的安全检测向量（vectors），对 APK 中可能存在的安全风险进行自动识别，并输出对应的风险等级、问题描述、命中位置以及分析报告。

本工具适合用于 APK 安全审计的**初筛阶段**。其目标不是直接给出最终漏洞结论，而是快速从 APK 中筛出高风险点，并将人工复核范围缩小到具体类、方法和调用位置，从而提高分析效率。

---

## 二、当前部署路径

当前工具部署在如下路径：

```bash id="b2qchu"
/home/cc/research/Apk_Check
```

主入口脚本为：

```bash id="8tlz5q"
apk_scanner.py
```

样例 APK 位于：

```bash id="3tcapg"
/home/cc/research/Apk_Check/test_applications
```

报告输出目录为：

```bash id="657qaf"
/home/cc/research/Apk_Check/Reports
```

这些路径及运行结果均已在当前环境中实际验证。 

---

## 三、工具工作原理

本工具的检测流程如下：

### 1. APK 解析

对输入 APK 进行静态解析，提取以下关键信息：

* 应用基础信息：包名、版本号、签名摘要等
* Manifest 信息：组件、权限、`debuggable`、`allowBackup` 等配置
* DEX 字节码信息：方法调用关系、敏感 API 调用路径
* 字符串常量：URL、Base64 编码字符串、命令字符串等

### 2. 加载检测向量

工具内置多类安全检测向量，例如：

* `debug`
* `ssl`
* `webview`
* `runtime_exec`
* `base64`
* `permissions`
* `storage`
* `dynamic_code`

实际运行中，工具已经成功加载并执行上述多类向量。 

### 3. 风险匹配

每个 vector 对应一组静态规则。
工具通过匹配 Manifest 配置、方法调用、类名、字符串和调用路径，识别 APK 中是否存在对应风险。

### 4. 结果输出

输出内容包括：

* 风险等级：`Critical / Warning / Notice / Info`
* 问题类型与向量 ID
* 问题说明
* 命中的类、方法、调用路径
* 自动生成的文本报告文件

---

## 四、当前已验证的检测能力

基于当前环境中的样例 APK，工具已完成多组实际验证，能够识别以下典型问题。

### 1. Debug 配置与调试签名检测

在 `debug-app-debug.apk` 中，工具成功识别出：

* `DEBUGGABLE`
* `HACKER_DEBUGGABLE_CERT`
* `ALLOW_BACKUP`
* `HACKER_DEBUGGABLE_CHECK`

其中不仅检测到了 `android:debuggable="true"`，还定位到了代码中用于判断调试状态的方法。

### 2. SSL 主机名校验风险检测

在 `allow-all-hostname-verifier-app-debug.apk` 中，工具成功命中：

* `SSL_CN2`

并定位到 `MainActivity->onCreate(...)` 中调用
`SSLSocketFactory->setHostnameVerifier(...)` 的代码位置，表明工具能够识别 HostnameVerifier 相关的弱 SSL 配置风险。

### 3. Base64 编码字符串与明文 URL 检测

在 `base64-app-debug.apk` 中，工具成功识别出：

* `HACKER_BASE64_STRING_DECODE`
* `SSL_URLS_NOT_IN_HTTPS`

其中不仅识别出了 Base64 编码字符串，还给出了其解码后的明文内容；同时检测到了非 HTTPS URL `http://www.google.nl`。 

### 4. 命令执行与 su 风险检测

在 `runtime-exec-app-debug.apk` 中，工具成功识别出：

* `COMMAND`
* `COMMAND_SU`
* `COMMAND_MAYBE_SYSTEM`

并定位到了 `Runtime.getRuntime().exec(...)` 的调用位置，同时提取出了 `su`、`su -c rm -rf /` 等高危命令字符串，说明工具能够发现命令执行及 root 相关危险调用。

---

## 五、工具的主要价值

本工具的主要价值体现在以下几个方面：

### 1. 适合 APK 静态安全初筛

对于未知 APK，可先使用本工具做静态检测，快速筛出可能存在问题的高风险点，而不必一开始就完全依赖手工翻代码。

### 2. 能给出具体命中位置

工具不只是输出“有问题”，还能进一步指出具体命中的类、方法与调用位置，便于后续人工复核与深入分析。 

### 3. 可用于规则化、批量化审计

由于工具基于向量规则运行，因此适合扩展为 APK 的批量初筛工具，在实验室场景下可用于对多份 APK 做统一规则扫描。

### 4. 便于输出留档

每次扫描后会自动生成文本报告，适合作为审计记录与后续分析材料。

---

## 六、工具使用方式

当前环境下，最常用的运行方式如下。

### 1. 进入项目目录

```bash id="fa996p"
cd /home/cc/research/Apk_Check
source venv/bin/activate
```

### 2. 查看帮助信息

```bash id="8zc673"
python3 apk_scanner.py -h
```

### 3. 查看所有检测向量

```bash id="3m81t2"
python3 apk_scanner.py -l
```

### 4. 扫描指定 APK

```bash id="punli1"
python3 apk_scanner.py -f APK文件路径 -v
```

例如：

```bash id="g8e9cn"
python3 apk_scanner.py -f test_applications/runtime-exec-app-debug.apk -v
```

### 5. 查看生成的报告

```bash id="d3g5go"
ls /home/cc/research/Apk_Check/Reports
```

---

## 七、当前样例演示结果概况

当前环境中已经完成验证的样例包括：

* `debug-app-debug.apk`
* `allow-all-hostname-verifier-app-debug.apk`
* `base64-app-debug.apk`
* `runtime-exec-app-debug.apk`

对应演示能力分别覆盖：

* 调试配置风险
* 弱 SSL / HostnameVerifier 风险
* Base64 可疑字符串与明文 URL
* 命令执行与 su 相关危险调用

上述样例均已成功完成扫描，并生成对应的分析报告文件。 

---

## 八、使用限制与说明

需要说明的是，本工具属于**静态检测工具**，因此其结果应理解为：

* 可疑风险点
* 静态规则命中结果
* 后续人工分析线索

它并不等价于最终漏洞证明。
部分结果可能来自第三方库代码，或者属于“高风险行为”而非“已确认漏洞”，因此仍然需要人工复核和结合上下文判断。

此外，当前运行环境中曾出现如下提示：

* `Requested API level 29 is larger than maximum we have, returning API level 28 instead.`
* `No Magic library was found on your system.`

但这些提示并未阻止样例 APK 的扫描和报告生成，说明当前工具主流程已经可以稳定运行。

---

## 九、结论

总体来看，`APK_Check` 当前已经具备较完整的 APK 静态安全初筛能力。
在现有测试中，工具已经能够稳定识别：

* Debug 配置问题
* Debug 签名问题
* 弱 SSL 配置问题
* Base64 可疑字符串
* 明文 HTTP URL
* `Runtime.exec(...)`
* `su` 及 root 相关高危命令调用

同时，它还能给出对应的命中代码位置，并自动生成报告文件。
因此，该工具适合作为实验室 APK 静态审计流程中的第一步工具，用于快速发现高风险点、辅助人工分析，并支撑后续规则扩展与批量分析工作。 

---
