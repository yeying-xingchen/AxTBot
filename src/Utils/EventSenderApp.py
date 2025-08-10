from tortoise.exceptions import IntegrityError
from tortoise.functions import Count

from src.Utils.Logger import logger
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
from src.Utils.EventClass import (
    GroupMessageEvent,
    PrivateMessageEvent,
    GuildMessageEvent
)

class MessageStore:
    """消息存储工具类"""
    
    @staticmethod
    async def save_group_message(
        group_id: str,
        user_id: str,
        message: str,
        message_id: str
    ) -> bool:
        """保存群消息"""
        try:
            await GroupMessage.create(
                group_id=group_id,
                user_id=user_id,
                message=message,
                message_id=message_id
            )
            return True
        except IntegrityError as e:
            # 处理消息ID重复的情况
            logger.error(f"保存群消息失败: {e}")
            return False
        except Exception as e:
            # 处理其他异常
            logger.error(f"保存群消息失败: {e}")
            return False
    
    @staticmethod
    async def save_user_message(
        user_id: str,
        message: str,
        message_id: str
    ) -> bool:
        """保存用户私聊消息"""
        try:
            await UserMessage.create(
                user_id=user_id,
                message=message,
                message_id=message_id
            )
            return True
        except IntegrityError as e:
            logger.error(f"保存私聊消息失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存私聊消息失败: {e}")
            return False
    
    @staticmethod
    async def save_channel_message(
        channel_id: str,
        guild_id: str,
        user_id: str,
        message: str,
        message_id: str
    ) -> bool:
        """保存频道公开消息"""
        try:
            await ChannelMessage.create(
                channel_id=channel_id,
                guild_id=guild_id,
                user_id=user_id,
                message=message,
                message_id=message_id
            )
            return True
        except IntegrityError as e:
            logger.error(f"保存频道消息失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存频道消息失败: {e}")
            return False
    
    @staticmethod
    async def save_channel_private_message(
        channel_id: str,
        guild_id: str,
        user_id: str,
        message: str,
        message_id: str
    ) -> bool:
        """保存频道私聊消息"""
        try:
            await ChannelPrivateMessage.create(
                channel_id=channel_id,
                guild_id=guild_id,
                user_id=user_id,
                message=message,
                message_id=message_id
            )
            return True
        except IntegrityError as e:
            logger.error(f"保存频道私聊消息失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存频道私聊消息失败: {e}")
            return False
    
    @staticmethod
    async def save_from_event(event) -> bool:
        """根据事件类型自动保存消息"""
        
        if isinstance(event, GroupMessageEvent):
            return await MessageStore.save_group_message(
                group_id=event.group_id,
                user_id=event.user_id,
                message=event.content,
                message_id=event.msg_id
            )
        
        elif isinstance(event, PrivateMessageEvent):
            return await MessageStore.save_user_message(
                user_id=event.user_id,
                message=event.content,
                message_id=event.msg_id
            )
        
        elif isinstance(event, GuildMessageEvent) and event.t == "AT_MESSAGE_CREATE":
            return await MessageStore.save_channel_message(
                channel_id=event.channel_id,
                guild_id=event.guild_id,
                user_id=event.user_id,
                message=event.content,
                message_id=event.msg_id
            )
        
        elif isinstance(event, GuildMessageEvent) and event.t == "DIRECT_MESSAGE_CREATE":
            return await MessageStore.save_channel_private_message(
                channel_id=event.channel_id,
                guild_id=event.guild_id,
                user_id=event.user_id,
                message=event.content,
                message_id=event.msg_id
            )
        
        return False
    
class SentMessageStore:
    """发送消息记录工具类"""
    
    @staticmethod
    async def log_sent_group_message(
        group_id: str,
        message: str,
        status: str = "pending",
        message_id: str = None,
        error_info: str = None
    ) -> SentGroupMessage:
        """记录发送的群消息"""
        return await SentGroupMessage.create(
            group_id=group_id,
            message=message,
            status=status,
            message_id=message_id,
            error_info=error_info
        )
    
    @staticmethod
    async def log_sent_user_message(
        user_id: str,
        message: str,
        status: str = "pending",
        message_id: str = None,
        error_info: str = None
    ) -> SentUserMessage:
        """记录发送的用户私聊消息"""
        return await SentUserMessage.create(
            user_id=user_id,
            message=message,
            status=status,
            message_id=message_id,
            error_info=error_info
        )
    
    @staticmethod
    async def log_sent_channel_message(
        channel_id: str,
        guild_id: str,
        message: str,
        status: str = "pending",
        message_id: str = None,
        error_info: str = None
    ) -> SentChannelMessage:
        """记录发送的频道公开消息"""
        return await SentChannelMessage.create(
            channel_id=channel_id,
            guild_id=guild_id,
            message=message,
            status=status,
            message_id=message_id,
            error_info=error_info
        )
    
    @staticmethod
    async def log_sent_channel_private_message(
        guild_id: str,
        message: str,
        status: str = "pending",
        message_id: str = None,
        error_info: str = None
    ) -> SentChannelPrivateMessage:
        """记录发送的频道私聊消息"""
        return await SentChannelPrivateMessage.create(
            guild_id=guild_id,
            message=message,
            status=status,
            message_id=message_id,
            error_info=error_info
        )
    
    @staticmethod
    async def update_message_status(
        record_id: int,
        message_type: str,
        status: str,
        message_id: str = None,
        error_info: str = None
    ):
        """更新消息状态"""
        model_map = {
            "group": SentGroupMessage,
            "user": SentUserMessage,
            "channel": SentChannelMessage,
            "dms": SentChannelPrivateMessage
        }
        
        if message_type not in model_map:
            raise ValueError(f"无效的消息类型: {message_type}")
        
        model = model_map[message_type]
        await model.filter(id=record_id).update(
            status=status,
            message_id=message_id,
            error_info=error_info
        )

async def get_failed_group_messages():
    """获取最近10条失败的群消息"""
    return await SentGroupMessage.filter(status="failed").order_by("-timestamp").limit(10)

async def get_failed_user_messages():
    """获取最近10条失败的用户私聊消息"""
    return await SentUserMessage.filter(status="failed").order_by("-timestamp").limit(10)

async def get_failed_channel_messages():
    """获取最近10条失败的频道消息"""
    return await SentChannelMessage.filter(status="failed").order_by("-timestamp").limit(10)

async def get_failed_channel_private_messages():
    """获取最近10条失败的频道私聊消息"""
    return await SentChannelPrivateMessage.filter(status="failed").order_by("-timestamp").limit(10)

async def group_message_stats():
    """群消息统计"""
    return await SentGroupMessage.annotate(
        count=Count("id")
    ).group_by("group_id").values("group_id", "count")

async def user_message_stats():
    """私聊消息统计"""
    return await SentUserMessage.annotate(
        count=Count("id")
    ).group_by("user_id").values("user_id", "count")

async def channel_message_stats():
    """频道消息统计"""
    return await SentChannelMessage.annotate(
        count=Count("id")
    ).group_by("channel_id").values("channel_id", "count")

async def channel_private_message_stats():
    """频道私聊消息统计"""
    return await SentChannelPrivateMessage.annotate(
        count=Count("id")
    ).group_by("guild_id").values("guild_id", "count")

async def get_message_statistics():
    """获取所有类型的收发消息统计"""
    return {
        "group": {
            "received": await GroupMessage.all().count(),
            "sent": await SentGroupMessage.all().count()
        },
        "channel": {
            "received": await ChannelMessage.all().count(),
            "sent": await SentChannelMessage.all().count()
        },
        "channel_private": {
            "received": await ChannelPrivateMessage.all().count(),
            "sent": await SentChannelPrivateMessage.all().count()
        },
        "private": {
            "received": await UserMessage.all().count(),
            "sent": await SentUserMessage.all().count()
        }
    }