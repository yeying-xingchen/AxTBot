from tortoise import fields, models
from datetime import datetime

class GroupMessage(models.Model):
    """群消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    group_id = fields.CharField(max_length=255, index=True)
    user_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=255, unique=True)
    
    class Meta:
        table = "group_messages"
        app = "message"

class UserMessage(models.Model):
    """用户私聊消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    user_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=255, unique=True)
    
    class Meta:
        table = "user_messages"
        app = "message"

class ChannelMessage(models.Model):
    """频道公开消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    channel_id = fields.CharField(max_length=255, index=True)
    guild_id = fields.CharField(max_length=255, index=True)
    user_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=255, unique=True)
    
    class Meta:
        table = "channel_messages"
        app = "message"

class ChannelPrivateMessage(models.Model):
    """频道私聊消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    channel_id = fields.CharField(max_length=255, index=True)
    guild_id = fields.CharField(max_length=255, index=True)
    user_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=255, unique=True)
    
    class Meta:
        table = "channel_private_messages"
        app = "message"

class SentGroupMessage(models.Model):
    """发送的群消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    group_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=200, null=True)  # 平台返回的消息ID
    status = fields.CharField(max_length=20, default="pending")  # pending/success/failed
    error_info = fields.TextField(null=True)  # 失败时的错误信息
    
    class Meta:
        table = "sent_group_messages"
        app = "messagesent"

class SentUserMessage(models.Model):
    """发送的用户私聊消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    user_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=200, null=True)
    status = fields.CharField(max_length=20, default="pending")
    error_info = fields.TextField(null=True)
    
    class Meta:
        table = "sent_user_messages"
        app = "messagesent"

class SentChannelMessage(models.Model):
    """发送的频道公开消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    channel_id = fields.CharField(max_length=255, index=True)
    guild_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=200, null=True)
    status = fields.CharField(max_length=20, default="pending")
    error_info = fields.TextField(null=True)
    
    class Meta:
        table = "sent_channel_messages"
        app = "messagesent"

class SentChannelPrivateMessage(models.Model):
    """发送的频道私聊消息记录"""
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(default=datetime.now)
    guild_id = fields.CharField(max_length=255, index=True)
    message = fields.TextField()
    message_id = fields.CharField(max_length=200, null=True)
    status = fields.CharField(max_length=20, default="pending")
    error_info = fields.TextField(null=True)
    
    class Meta:
        table = "sent_channel_private_messages"
        app = "messagesent"