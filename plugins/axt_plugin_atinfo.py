import psutil
from datetime import datetime

from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent
from src.Utils.MessageState import AppState, MessageStatistics

__metadata__ = {
    "name": "[官方插件]获取框架信息",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取当前框架的消息数等信息",
    "official": True
}


@command(["atinfo", "/atinfo"])
async def get_message(event: GroupMessageEvent):
    start_time = AppState.get_start_time()
    stats_service = MessageStatistics(start_time)
    stats = await stats_service.get_stats()
    elapsed_time = datetime.now() - start_time
    days = elapsed_time.days
    hours, remainder = divmod(elapsed_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    info = await get_system_info()
    reply =   "AxTBot Public v 2.1\n" + \
              "===============" + "\n" + \
              "CPU: " + info["cpu_usage"] + "\n" + \
              "RAM: " + info["ram_usage"] + "\n" + \
              "====消息数统计====" + "\n" + \
              "群聊收/发: " + str(stats['received']['group']['total']) + "/" + str(stats['sent']['group']['total']) + "\n" + \
              "私聊收/发: " + str(stats['received']['private']['total']) + "/" + str(stats['sent']['private']['total']) + "\n" + \
              "频道收/发: " + str(stats['received']['channel']['total']) + "/" + str(stats['sent']['channel']['total']) + "\n" + \
              "频道私聊收/发: " + str(stats['received']['channel_private']['total']) + "/" + str(stats['sent']['channel_private']['total']) + "\n" + \
              "===============" + "\n" + \
              "已正常运行" + "\n" + \
              str(f"{days}天 {hours:02d}时 {minutes:02d}分 {seconds:02d}秒") + "\n" + \
              "===============" + "\n" + \
              "官方社区群: 832275338" + "\n" + \
              "==============="
    await event.reply(reply)

async def get_system_info():
    info = {}
    # 获取CPU信息
    info['cpu_usage'] = f"{psutil.cpu_percent(interval=1)}%"

    # 获取内存信息
    memory = psutil.virtual_memory()
    memory_total_gb = memory.total / (1024 ** 3)
    memory_used_gb = memory.used / (1024 ** 3)
    info['ram'] = f"{memory_used_gb:.2f}/{memory_total_gb:.2f}GB"
    info['ram_usage'] = f"{memory.percent}%"

    return info