from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload

from uapis_extension import get_from_api

__metadata__ = {
    "name": "[官方插件]获取IP地址信息",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取IP地址信息",
    "official": True,
}

@command(["ipinfo", "/ipinfo"])
async def ipinfo_handler(event: MessageEventPayload):
    if event.content.split(" ")[1]:
        host = event.content.split(" ")[1]
        info = await get_from_api(f"api/v1/network/ipinfo?ip={host}")
        if info is None:
            await event.reply('未查询到该IP信息')
        else:
            contents = "=====IP信息=====" + "\n" + \
                    "IP: " + info["ip"] + "\n" + \
                    "| 开始 IP: " + info["beginip"] + "\n" + \
                    "| 结束 IP: " + info["endip"] + "\n" + \
                    "| 归属地: " + info["region"] + "\n" + \
                    "| 纬度: " + str(info["latitude"]) + "\n" + \
                    "| 经度: " + str(info["longitude"]) + "\n" + \
                    "| ISP: " + str(info["isp"]) + "\n" + \
                    "| LLC: " + info["llc"] + "\n" + \
                    "| ASN: " + str(info["asn"]) + "\n" + \
                    "=============="
            await event.reply(contents)
    else:
        contents = "=======IPInfo查询菜单=======" + "\n" + \
                   "/ipinfo [IP] - 查询IP详细信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ipinfo 1.1.1.1" + "\n" + \
                   "=========================="
        await event.reply(contents)