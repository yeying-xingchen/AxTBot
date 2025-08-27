from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent

from uapis_extension import get_from_api, translate_domain_status

__metadata__ = {
    "name": "[官方插件]获取Whois信息",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "通过Uapis获取Whois信息",
    "official": True,
}

@command(["whois", "/whois"])
async def whois_handler(event: GroupMessageEvent) -> str:
    if event.content in ["/whois", "/whois ", "whois", "whois "]:
        content =  "=======Whois查询菜单=======" + "\n" + \
                   "/whois [域名] - 查询域名信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /whois 域名" + "\n" + \
                   "=========================="
        await event.reply(content=content)
    else:
        msg = event.content
        domain = msg.split(" ")[1]
        if msg.startswith(("/whois ","whois ")) and domain:
            info = await get_from_api(f"/api/v1/network/whois?domain={domain}&format=json")
            if info is None:
                await event.reply(content="未查询到该域名信息或暂不支持查询该格式")
                return
            else:
                info = info["whois"]
                domain = info["domain"]
                domain_status_translated = translate_domain_status(domain["status"])
                domain_status_str = "\n".join([status for status in domain_status_translated])
                dns_str = ", ".join([dns.replace(".", ",") for dns in domain["name_servers"]])
                content = "=====Whois信息=====" + "\n" + \
                        "| 注册邮箱: " + info["registrar"]["email"].replace(".", ",") + "\n" + \
                        "| 注册电话: " + info["registrar"]["phone"] + "\n" + \
                        "| 注册公司: " + info["registrar"]["name"].replace(".", ",") + "\n" + \
                        "| 注册日期: " + domain["created_date_in_time"].replace("T", " ").replace("Z", "") + "\n" + \
                        "| 更新日期: " + domain["updated_date_in_time"].replace("T", " ").replace("Z", "") + "\n" + \
                        "| 过期日期: " + domain["expiration_date_in_time"].replace("T", " ").replace("Z", "") + "\n" + \
                        "=====域名状态=====" + "\n" + \
                        domain_status_str + "\n" + \
                        "======DNS======" + "\n" + \
                        dns_str + "\n" + \
                        "==============" + "\n" + \
                        "由于QQ官方消息审核限制，域名相关的.已被替换为," + "\n" + \
                        "=============="
            await event.reply(content=content)