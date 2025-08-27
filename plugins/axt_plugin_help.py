from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload

__metadata__ = {
    "name": "[官方插件]帮助插件",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取帮助菜单",
    "official": True,
}


@command(["help", "/help"])
async def help_handler(event: MessageEventPayload):
    content =      "=======AxT社区机器人=======" + "\n" + \
                   "| help | - 获取帮助菜单" + "\n" + \
                   "| ping | - 显示Ping菜单" + "\n" + \
                   "| ipinfo | - 显示IPInfo菜单" + "\n" + \
                   "| whois | - 显示Whois菜单" + "\n" + \
                   "| hotlist | - 显示每日热榜菜单" + "\n" + \
                   "| mc | - 查询Minecraft相关内容" + "\n" + \
                   "| jrrp | - 获取今日人品" + "\n" + \
                   "| remake | - 重来一世 你会变成什么" + "\n" + \
                   "| ask | - 读赛博之书 品百味人生" + "\n" + \
                   "===============" + "\n" + \
                   "官方社区群: 832275338" + "\n" + \
                   "===============" + "\n" + \
                   "AxTBot Public v 2.1"
    await event.reply(content)
