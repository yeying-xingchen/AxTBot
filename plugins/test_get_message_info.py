from src.Utils.PluginBase import command
from src.Utils.Logger import logger
from src.Utils.EventClass import GroupMessageEvent
from src.Utils.MessageState import AppState, MessageStatistics

__metadata__ = {
    "name": "测试-消息获取、检索插件",
    "version": "1.0.0",
    "author": "Shanshui2023",
    "description": "获取当前框架的消息数等信息"
}


@command("get_message_1")
async def get_message(event: GroupMessageEvent) -> str:

    # 初始化统计服务
    start_time = AppState.get_start_time()
    stats_service = MessageStatistics(start_time)
    
    stats = await stats_service.get_stats()

    logger.info("本次启动后消息统计:")
    logger.info(f"群聊消息: 接收 {stats['received']['group']['total']} 条 | 发送 {stats['sent']['group']['total']} 条")
    logger.info(f"频道消息: 接收 {stats['received']['channel']['total']} 条 | 发送 {stats['sent']['channel']['total']} 条")
    logger.info(f"频道私聊: 接收 {stats['received']['channel_private']['total']} 条 | 发送 {stats['sent']['channel_private']['total']} 条")
    logger.info(f"私聊消息: 接收 {stats['received']['private']['total']} 条 | 发送 {stats['sent']['private']['total']} 条")

    for detail in stats['received']['group']['details']:
        logger.info(f"群 {detail['group_id']}: 接收 {detail['count']} 条消息")










from src.Utils.PluginBase import command
from src.Utils.Logger import logger
from src.Utils.EventClass import GroupMessageEvent
from src.Utils.EventSenderApp import (
    group_message_stats,
    user_message_stats,
    channel_message_stats,
    channel_private_message_stats,
    get_failed_user_messages,
    get_failed_channel_messages,
    get_failed_channel_private_messages,
    get_failed_group_messages
)

__metadata__ = {
    "name": "测试-消息获取、检索插件",
    "version": "1.0.0",
    "author": "Shanshui2023",
    "description": "获取当前框架的消息数等信息"
}

@command("get_message_2")
async def get_message(event: GroupMessageEvent) -> str:
    content = f"统计 群消息数: {await group_message_stats()}\n" \
              f"用户消息数: {await user_message_stats()}\n" \
              f"频道消息数: {await channel_message_stats()}\n" \
              f"频道私信消息数: {await channel_private_message_stats()}\n" \
              f"失败的群消息数: {await get_failed_group_messages()}\n" \
              f"失败的用户消息数: {await get_failed_user_messages()}\n" \
              f"失败的频道消息数: {await get_failed_channel_messages()}\n" \
              f"失败的频道私信消息数: {await get_failed_channel_private_messages()}"
    await event.reply(content)










from src.Utils.PluginBase import command
from src.Utils.Logger import logger
from src.Utils.EventClass import GroupMessageEvent
from src.Utils.EventSenderApp import (
    get_message_statistics
)

__metadata__ = {
    "name": "测试-消息获取、检索插件",
    "version": "1.0.0",
    "author": "Shanshui2023",
    "description": "获取当前框架的消息数等信息"
}


@command("get_message_3")
async def get_message(event: GroupMessageEvent) -> str:

    stats = await get_message_statistics()

    content = f"\n群消息统计:" \
              f"\n接收: {stats['group']['received']} 条" \
              f"\n发送: {stats['group']['sent']} 条" \
               "\n频道消息统计:" \
              f"\n接收: {stats['channel']['received']} 条" \
              f"\n发送: {stats['channel']['sent']} 条" \
               "\n频道私聊统计:" \
              f"\n接收: {stats['channel_private']['received']} 条" \
              f"\n发送: {stats['channel_private']['sent']} 条" \
               "\n私聊消息统计:" \
              f"\n接收: {stats['private']['received']} 条" \
              f"\n发送: {stats['private']['sent']} 条"
    await event.reply(content)