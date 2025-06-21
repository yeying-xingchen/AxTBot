# AxTBot-v2


## 许可 | LICENSE

> "本代码采用AGPLv3授权。**禁止任何企业直接使用此代码于商业产品/服务**。  
> 但欢迎开发者：  
> - ✅ 学习代码思路  
> - ✅ 用独立代码实现类似功能（无论是否开源）  
> - ✅ 非商业场景下使用/修改本代码  
> 企业需商业使用？请联系作者获取例外许可。"

*注意：独立实现指未引用本项目中任何源代码，且未侵犯著作权的新创作。*

<br />

## 使用文档 | Usage
- [AxTBot-v2 | AxT Docs](https://docs.axtn.net/AxTBot-v2/)

## Hypixel查询注意事项:
Hypixel查询是基于 **[Spelako](https://github.com/Spelako)** 项目修改而来<br>
此存库**只提供用于启动PHP服务器API接口的代码**，其他代码请到原存库进行获取<br>

### API使用方法:<br>
1. 把 ``SpelakoCore`` 文件夹和 ``index.php`` 放在同目录下<br>
2. 使用 ``start.bat`` 启动即可（Linux自行编写启动脚本）
3. 默认启动在 ``0.0.0.0:30001`` ，如果端口被占用，请修改启动脚本中的端口号<br>

<br />

## 快速开始 | Quick Start

1. 下载源码

2. 创建虚拟环境(可选)

在控制台中输入如下命令创建venv虚拟环境
```bash
D:\AxTBot> py -m venv <文件夹名>
```

3. 安装依赖

如果你使用venv虚拟环境，那么在venv虚拟环境中安装依赖
```bash
D:\AxTBot> <虚拟环境文件夹>\Scripts\Activate
(venv) D:\AxTBot> pip install -r requirements.txt
```

4. 配置

将`.env.example`文件重命名为`.env` 并填入机器人相关信息

5. 运行
```bash
(venv) D:\AxTBot> py main.py
```

## 注意事项 | Attention
1. 日志并非即时更改，所以框架刚开机时日志文件为空，将在后续版本中解决该问题

2. 由于设定问题，目前每次接收消息后均会reload一次插件，可能导致不必要的性能开销，将在未来的版本中解决该问题

## 快速开发 | Develop

本节详阅[快速开发 - AxTBot-v2 | AxT Docs](https://docs.axtn.net/AxTBot-v2/Developer/)

*你没看错，新框架允许你自己开发插件供你自己机器人使用了（*

<hr>

## Mirai&CQ版本已转移到以下存库(内部号)
- https://github.com/XiaoXianHW/ATBot
- https://github.com/AxT-Team/Ebackup

## 旧版本(基于qq-botpy + Websocket所写的)
- https://github.com/AxT-Team/AxTBot/blob/AxTBot-v1