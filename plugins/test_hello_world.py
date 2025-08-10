from src.Utils.PluginBase import command
from src.Utils.Logger import logger
from src.Utils.EventClass import GroupMessageEvent, MessageEventPayload

__metadata__ = {
    "name": "测试-问候插件",
    "version": "1.0.0",
    "author": "Shanshui2023",
    "description": "使用装饰器实现的问候插件"
}

def initialize():  #初始化逻辑 可省略
    logger.info("问候插件初始化")

def shutdown(): # 关机 亦可省
    logger.info("问候插件资源清理")

@command("hello")
async def handle_hello(event: MessageEventPayload):
    """处理hello命令"""
    await event.reply(f"你好, {str(event.user_id)}!" if str(event.user_id) else "你好，世界!")

@command("bye", event_type=GroupMessageEvent)
async def handle_bye(event: GroupMessageEvent):
    """处理bye命令"""
    await event.reply(f"再见, {event.user_id}!" if event.user_id else "再见！")