from src.Utils.PluginBase import group_add
from src.Utils.Logger import logger
from src.Utils.EventClass import GroupEvent

__metadata__ = {
    "name": "测试-进群欢迎",
    "version": "1.0.0",
    "author": "Shanshui2023",
    "description": "使用装饰器实现的进群欢迎插件",
}


@group_add
async def handle_hello(event: GroupEvent) -> None:
    """处理群消息事件
    
    Args:
        event: 群消息事件对象
    """

    await event.reply("欢迎使用AxT社区机器人2.1.0！")
