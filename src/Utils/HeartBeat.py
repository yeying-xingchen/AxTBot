import asyncio, aiohttp

from src.Utils.Config import config
from src.Utils.Logger import logger
from src.Utils.MailNotice import send_mail_notice

def heartbeat_check_start():
    asyncio.run(heartbeat_check())
async def heartbeat_check():
    head = "https://" if config.Network.ssl else "http://"
    host = config.Network.host if config.Network.host != "0.0.0.0" else "127.0.0.1"
    url = f"{head}{host}:{config.Network.port}/api/heartbeat"
    count = 0
    while True:
        await asyncio.sleep(60)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"X-HeartBeat-Check": "r u ok?"}, ssl=False) as response:
                    heartbeat = await response.json()
                    if response.status != 200 or heartbeat["heartbeat"] != "3Q":
                        logger.error("心跳检查组件 >>> 检测结果：服务器异常，请检查服务器状态")
                        count += 1
                        if count == 5:
                            msg ="请求头：X-HeartBeat-Check: r u ok?\n\n" \
                                f"请求地址：{url}\n\n" \
                                f"响应状态码：{response.status}\n\n" \
                                f"响应内容：{heartbeat}\n\n" \
                                f"返回头：{response.headers}\n\n" \
                                f"本邮件由AxTBot v2.1.0自动发送\n\n" \
                                f"主程序已经请求5次 均返回错误 请检查服务器状态"
                            await send_mail_notice(msg)
                            exit(-26)
                    else:
                        pass
        except Exception as e:
            count += 1
            logger.error(f"心跳检查组件 >>> 检测结果：服务器异常，请检查服务器状态，错误信息：{e}")
            if count == 5:
                await send_mail_notice(
                    str(e) +
                    f"本邮件由AxTBot v2.1.0自动发送\n\n" \
                    f"主程序已经请求5次 均返回错误 请检查服务器状态"
                )
            exit(-32)