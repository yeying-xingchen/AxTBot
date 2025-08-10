from src.Utils.EventClass import MessageEventPayload
from src.Utils.PluginBase import get_command_handler
from src.Utils.Logger import logger
from src.Utils.EventSenderApp import MessageStore

async def handle_event(payload: MessageEventPayload):
    """处理消息事件"""
    # 获取命令处理器（使用全局状态）
    logger.debug(f"插件管理器 >>> 处理消息: {payload.content}")
    await MessageStore.save_from_event(payload)
    # 解析命令
    parts = payload.content.strip().split(maxsplit=1)
    if not parts:
        return "错误: 空消息"
    command = parts[0].lower()
    # 获取命令处理器
    handler = await get_command_handler(command, type(payload))
    if not handler:
        return f"未知命令: {command}"
    try:
        # 调用处理函数
        await handler(payload)
        return
    except Exception as e:
        error_msg = f"执行命令 {command} 出错: {str(e)}"
        logger.error(f"插件管理器 >>> {error_msg}")
        return error_msg