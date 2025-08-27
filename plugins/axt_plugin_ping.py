from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload

from uapis_extension import get_from_api

__metadata__ = {
    "name": "[官方插件]Ping",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取网站到节点的延迟信息",
    "official": True,
}

@command(["ping", "/ping"])
async def ping_handler(event: MessageEventPayload):
    if event.content in ["/ping", "/ping ", "ping", "ping "]:
        content = "========Ping查询菜单========" + "\n" + \
                   "/ping [IP] [查询节点] - 查询IP地址延迟及归属地" + "\n" + \
                   "可选的查询节点有:" + "\n" + \
                   "- cn | 中国湖北十堰/电信" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ping 域名/IP cn" + "\n" + \
                   "=========================="
        await event.reply(content=content)
    else:
        msg = event.content
        host = msg.split(" ")[1]

        if msg.startswith(("/ping ","ping ")) and host:
            info = checkpoint = None
            try:
                info = await get_from_api(
                    f"/api/v1/network/ping?host={host}"
                )
                checkpoint = "中国湖北十堰/电信"
            except TypeError as e:
                await event.reply(content='未查询到该IP地址')
                return
            if info:
                content = "=====Ping信息=====" + "\n" + \
                        "主机名: " + info["host"].replace('.',',') + "\n" + \
                        "| IP: " + info["ip"] + "\n" + \
                        "| 最大延迟: " + str(info["max"]) + " ms\n" + \
                        "| 平均延迟: " + str(info["avg"]) + " ms\n" + \
                        "| 最小延迟: " + str(info["min"]) + " ms\n" + \
                        "| 归属地: " + str(info["location"]) + "\n" + \
                        "| 检测点: " + checkpoint + "\n" + \
                        "=============="

                await event.reply(content=content)
                return
            else:
                await event.reply(content='未查询到该IP地址')
                return

    pass
