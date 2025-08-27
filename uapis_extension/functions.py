import aiohttp, asyncio
from aiohttp import ClientError

from src.Utils.Logger import logger

def format_hot_search(data):
    items = data.get("list", [])[:10]
    formatted = []
    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        hot = item.get("hot_value", None)
        if hot:
            formatted.append(f"{index} - {title} | {hot}")
        else:
            formatted.append(f"{index} - {title}")
    return "\n".join(formatted)


async def get_hypixel_info(command, userid):
    url = "http://localhost:30001/hypixel?" + "command=" + command + "&userId=" + userid
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return "请求出错！具体信息：" + str(e)

def translate_domain_status(status_list):
    status_translations = {
        "clientDeleteProhibited": "客户端删除禁止",
        "clientdeleteprohibited": "客户端删除禁止",
        "clientTransferProhibited": "客户端转移禁止",
        "clienttransferprohibited": "客户端转移禁止",
        "clientUpdateProhibited": "客户端更新禁止",
        "clientupdateprohibited": "客户端更新禁止",
        "serverDeleteProhibited": "服务器删除禁止",
        "serverdeleteprohibited": "服务器删除禁止",
        "serverTransferProhibited": "服务器转移禁止",
        "servertransferprohibited": "服务器转移禁止",
        "serverUpdateProhibited": "服务器更新禁止",
        "serverupdateprohibited": "服务器更新禁止",
    }

    translated_status = []
    for status in status_list:
        status_without_link = status.split(" ")[0]
        status_cn = status_translations.get(status_without_link, status_without_link)
        translated_status.append(status_cn)

    return translated_status
