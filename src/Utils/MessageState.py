from datetime import datetime, timedelta
from tortoise.functions import Count

from src.Utils.EventSender import (
    GroupMessage,
    UserMessage,
    ChannelMessage,
    ChannelPrivateMessage,
    SentGroupMessage,
    SentUserMessage,
    SentChannelMessage,
    SentChannelPrivateMessage
)

class MessageStatistics:
    def __init__(self, start_time: datetime):
        self.start_time = start_time
        self._cache = None
        self._cache_time = None
    
    async def get_stats(self, use_cache=True):
        """获取统计信息，可选用缓存"""
        if use_cache and self._cache and datetime.now() - self._cache_time < timedelta(minutes=5):
            return self._cache
        
        stats = await self._calculate_stats()
        
        # 缓存结果
        self._cache = stats
        self._cache_time = datetime.now()
        return stats
    async def _calculate_stats(self):
        """获取本次启动后的消息统计"""
        return {
            "received": {
                "group": await self._get_received_group_stats(),
                "channel": await self._get_received_channel_stats(),
                "channel_private": await self._get_received_channel_private_stats(),
                "private": await self._get_received_private_stats()
            },
            "sent": {
                "group": await self._get_sent_group_stats(),
                "channel": await self._get_sent_channel_stats(),
                "channel_private": await self._get_sent_channel_private_stats(),
                "private": await self._get_sent_private_stats()
            }
        }
    
    async def _get_received_group_stats(self):
        count = await GroupMessage.filter(timestamp__gte=self.start_time).count()
        details = await GroupMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("group_id").values("group_id", "count")
        return {"total": count, "details": details}
    
    async def _get_received_channel_stats(self):
        count = await ChannelMessage.filter(timestamp__gte=self.start_time).count()
        details = await ChannelMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("channel_id").values("channel_id", "count")
        return {"total": count, "details": details}
    
    async def _get_received_channel_private_stats(self):
        count = await ChannelPrivateMessage.filter(timestamp__gte=self.start_time).count()
        details = await ChannelPrivateMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("guild_id").values("guild_id", "count")
        return {"total": count, "details": details}
    
    async def _get_received_private_stats(self):
        count = await UserMessage.filter(timestamp__gte=self.start_time).count()
        details = await UserMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("user_id").values("user_id", "count")
        return {"total": count, "details": details}
    
    async def _get_sent_group_stats(self):
        count = await SentGroupMessage.filter(timestamp__gte=self.start_time).count()
        details = await SentGroupMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("group_id").values("group_id", "count")
        return {"total": count, "details": details}
    
    async def _get_sent_channel_stats(self):
        count = await SentChannelMessage.filter(timestamp__gte=self.start_time).count()
        details = await SentChannelMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("channel_id").values("channel_id", "count")
        return {"total": count, "details": details}
    
    async def _get_sent_channel_private_stats(self):
        count = await SentChannelPrivateMessage.filter(timestamp__gte=self.start_time).count()
        details = await SentChannelPrivateMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("guild_id").values("guild_id", "count")
        return {"total": count, "details": details}
    
    async def _get_sent_private_stats(self):
        count = await SentUserMessage.filter(timestamp__gte=self.start_time).count()
        details = await SentUserMessage.filter(timestamp__gte=self.start_time).annotate(
            count=Count("id")
        ).group_by("user_id").values("user_id", "count")
        return {"total": count, "details": details}
    


class AppState:
    _start_time: datetime = None
    
    @classmethod
    def set_start_time(cls, start_time: datetime):
        cls._start_time = start_time
    
    @classmethod
    def get_start_time(cls) -> datetime:
        return cls._start_time