import aiohttp, asyncio
from aiohttp import ClientError

from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload
from src.Utils.Logger import logger


__metadata__ = {
    "name": "[官方插件]赛博之书",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "从接口请求得到赛博之书的答案~"
}

@command(["ask", "/ask"])
async def ask_handler(event: MessageEventPayload):
    url = f"https://uapis.cn/api/v1/answerbook/ask"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url) as response:
                response.raise_for_status()
                result = (await response.json()).get("answer")
                await event.reply(result)
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            await event.reply("答案获取失败，可能是偶然错误。\n我们已将报错信息发送给管理员，您可以稍后重新尝试")
