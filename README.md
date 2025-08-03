
# AxTBot-v2

一个基于 Python 的可扩展 Bot 框架。
📖 完整文档请访问：[AxTBot-v2 | AxT Docs](https://docs.axtn.net/AxTBot-v2/)

---

> [!CAUTION]
> ⚠️ 本项目功能开发已完成，目前已进入长周期（LTS）状态。若有新问题请提交issue。

---

## 📜 许可 | License

> 本项目采用 **AGPLv3** 协议授权。
> **禁止任何企业直接将本代码用于商业产品或服务。**
> 但欢迎以下行为：
>
> * ✅ 学习代码思路
> * ✅ 独立实现类似功能（无论是否开源）
> * ✅ 在非商业场景下使用或修改本项目
>
> 若企业希望商业使用，请联系作者获取**例外许可**。
>
> *注：独立实现指未引用本项目任何源代码，且未侵犯著作权的新创作品。*

---

## ⚡ 快速开始 | Quick Start

### 1️⃣ 下载源码

```bash
git clone https://github.com/AxT-Team/AxTBot.git
```

### 2️⃣ 创建虚拟环境（可选）

```bash
py -m venv .venv
.venv\Scripts\Activate
```

### 3️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 4️⃣ 配置环境变量

将 `.env.example` 重命名为 `.env`，并填写你的机器人配置。

### 5️⃣ 启动 Bot

```bash
py main.py
```

---

## 🔧 快速开发 | Developer Guide

> 没错！现在你可以为你的 Bot 自行开发插件 ✨

开发指南请访问：[快速开发 - AxTBot-v2 | AxT Docs](https://docs.axtn.net/AxTBot-v2/Developer/)

---

## ⚠ 注意事项 | Attention

1. 当前日志模块并非实时记录，首次启动时日志文件可能为空。该问题将在未来版本修复。
2. 目前每次接收消息都会重新加载插件，可能带来性能负担，未来版本将优化此行为。

---

## 🏷️ 其他版本迁移

* 旧版本（基于 `qq-botpy` + WebSocket）：

  * [https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1](https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1)
 
* Mirai & CQ 版（已存档的上古时期ATBot仓库）：

  * [https://github.com/XiaoXianHW/ATBot](https://github.com/XiaoXianHW/ATBot)
  * [https://github.com/AxT-Team/Ebackup](https://github.com/AxT-Team/Ebackup)

---

## [扩展] Hypixel 查询模块 （原仓库目前已关闭，暂不提供支持）

本项目中的 Hypixel 查询功能基于 [Spelako](https://github.com/Spelako) 项目进行修改。
**本仓库仅提供用于启动 PHP 服务器 API 接口的相关代码，其他功能请前往原仓库查看。**

### 🚀 启动 API 的方法：

1. 将 `SpelakoCore` 文件夹与 `index.php` 放置在同一目录中
2. 运行 `start.bat` 启动服务（Linux 用户请自行编写启动脚本）
3. 默认监听地址为 `0.0.0.0:30001`，如端口被占用请修改启动脚本中的端口设置


