from Core.Logger import logger
import aiohttp
from aiohttp import ClientError, ClientSSLError
import asyncio


uapi = "api.uapis.cn"
uapi_old = "uapis.cn"


async def get_ip_info(ip):
    url = f"https://{uapi}/api/v1/network/ipinfo?ip={ip}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return None


async def get_ping_info(ip):
    url = f"https://{uapi}/api/v1/network/ping?host={ip}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return None


async def get_whois_info(domain):
    url = f"https://{uapi}/api/v1/network/whois?domain={domain}&format=json"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except ClientSSLError as e:
            logger.error(f"SSL 错误：{e}")
            return {"error": "SSL 证书验证失败，请稍后再试或联系管理员。"}
        except ClientError as e:
            logger.error(f"请求错误：{e}")
            info = await response.json()['error'] if "error" in response.json() else "未返回正确值"
            return {"error": info}


async def get_icp_info(domain):
    url = f"https://{uapi}/api/v1/network/icp?domain={domain}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return None


async def get_hot_list(hot_type):
    url = f"https://{uapi}/api/v1/misc/hotboard?type={hot_type}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return None


async def get_answer_book():
    url = f"https://{uapi_old}/api/answerbook"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return (await response.json()).get("content")
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return "获取失败，请联系管理员寻求帮助"


async def get_touch_url(qqid):
    url = f"https://{uapi}/api/v1/image/motou?qq={str(qqid)}"
    return url


async def get_steamid_info(steamid):
    split_str = steamid.split(" ")
    steamid = split_str[1]  # 获取分割后的第二个子字符串
    url = f"https://{uapi}/api/v1/game/steam/summary?steamid={steamid}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        communitystate = data.get("communityvisibilitystate") if data.get("communityvisibilitystate") != 'N/A' else "未知"
                        steamID64 = data.get("steamid") if data.get("steamid") != 'N/A' else "未知"
                        steamUsername = data.get("personaname") if data.get("personaname") != 'N/A' else "未知"
                        realname = data.get("realname") if data.get("realname") != 'N/A' else "未知"
                        accountcreationdate = data.get("timecreated_str") if data.get("timecreated_str") != 'N/A' else "未知"
                        # lastlogoff = data.get("lastlogoff") if data.get("lastlogoff") != '1970-01-01 08:00:00' and data.get("lastlogoff") != 'N/A' else "未知"
                        location = data.get("loccountrycode") if data.get("loccountrycode") != 'N/A' else "未知"
                        return f"""
====Steam账户信息====
| 社区资料状态：{communitystate}
| 用户名：{steamUsername}
| 真实姓名：{realname}
| Steam ID：{steamID64}
| 账户创建日期：{accountcreationdate}
| 地理位置：{location}
=====================
"""
                    elif data.get("code") == 432:
                        return "\n未查询到该玩家信息"
                    elif data.get("code") == 443:
                        return f"\n请输入Steam ID，当前用户名/用户ID {steamid} 输入有误"
                else:
                    return f"\n查询失败，请联系管理员处理\n状态码：{response.status}"
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return "\n查询失败，请联系管理员处理"


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
        "serverupdateprohibited": "服务器更新禁止"
    }

    translated_status = []
    for status in status_list:
        status_without_link = status.split(" ")[0]
        status_cn = status_translations.get(status_without_link, status_without_link)
        translated_status.append(status_cn)

    return translated_status


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


def format_history_today(data):
    items = data.get("data", [])
    formatted = []
    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        formatted.append(f"{index}: {title}")
    return "\n".join(formatted)