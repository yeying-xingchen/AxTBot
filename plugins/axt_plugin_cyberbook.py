from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent

from uapis_extension import post_for_api


__metadata__ = {
    "name": "[官方插件]赛博之书",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "从接口请求得到赛博之书的答案~",
    "official": True,
}

@command(["ask", "/ask"])
async def ask_handler(event: GroupMessageEvent):
    try:
        response = await post_for_api("/api/v1/answerbook/ask")
    except Exception as e:
        await event.reply("答案获取失败，可能是偶然错误。\n我们已将报错信息发送给管理员，您可以稍后重新尝试")
        raise
    returns = response["answer"] if "answer" in response else "赛博之书沉默了..."
    await event.reply(returns)
