import aiohttp
from datetime import datetime, timedelta

from src.Utils.EventClass import (
    MediaPayload,
    MessageSenderBasePayload,
    MessageSenderOverPayload,
    AutoReplyPayload,
    MediaUploadPayload,
)
from src.Utils.Logger import logger
from src.Utils.EventSenderApp import SentMessageStore

open_url = "https://api.sgroup.qq.com"


async def send_group_message(group_openid, payload: MessageSenderBasePayload) -> None:
    logger.debug(f"发送群聊消息 -> {group_openid}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_group_message(
        group_id=group_openid, message=payload.content
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/v2/groups/{group_openid}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="group",
                    status="success",
                    message_id=response_json["id"],
                )
                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="group",
                status="failed",
                error_info=str(errinfo),
            )


async def send_channel_message(channel_id, guild_id, payload: MessageSenderBasePayload):
    """发送频道消息"""
    logger.debug(f"发送频道消息 -> {channel_id}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_channel_message(
        channel_id=channel_id,
        guild_id=guild_id,
        message=payload.content,
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/channels/{channel_id}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="channel",
                    status="success",
                    message_id=response_json["id"],
                )
                logger.debug(f"发信 >>> 返回结果 -> {response_json}")
                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="channel",
                status="failed",
                error_info=errinfo,
            )


async def send_channel_dms(guild_id, payload: MessageSenderBasePayload):
    logger.debug(f"发送频道私聊消息 -> {guild_id}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_channel_private_message(
        guild_id=guild_id,
        message=payload.content,
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/dms/{guild_id}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                logger.debug(f"发信 >>> 返回结果 -> {response_json}")
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="dms",
                    status="success",
                    message_id=response_json["id"],
                )

                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="dms",
                status="failed",
                error_info=errinfo,
            )


async def send_private_message(user_id, payload: MessageSenderBasePayload):
    logger.debug(f"发送QQ私聊消息 -> {user_id}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_user_message(
        message=payload.content, user_id=user_id
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/v2/users/{user_id}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                logger.debug(f"发信 >>> 返回结果 -> {response_json}")
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="user",
                    status="success",
                    message_id=response_json["id"],
                )
                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="user",
                status="failed",
                error_info=errinfo,
            )


async def send_auto_reply(payload: AutoReplyPayload) -> None:
    """发送自动填充的消息"""
    base_payload = MessageSenderBasePayload()
    if payload.markdown:
        base_payload.markdown = payload.markdown
        base_payload.msg_type = 2
    base_payload.msg_id = payload.msg_id
    if payload.ark:
        base_payload.ark = payload.ark
        base_payload.msg_type = 3
    if payload.media:
        base_payload.media = payload.media
        base_payload.msg_type = 7
    if payload.image:
        base_payload.image = payload.image
    if payload.group_id:
        if payload.markdown or payload.ark:
            base_payload.content = " "
        elif payload.event_id:
            base_payload.event_id = payload.event_id
            base_payload.content = payload.content
        else:
            base_payload.content = "\n" + payload.content
        await send_group_message(payload.group_id, base_payload)
    elif payload.channel_id and payload.is_direct_message == False:
        base_payload.content = payload.content
        await send_channel_message(payload.channel_id, payload.guild_id, base_payload)
        pass
    elif payload.guild_id:
        base_payload.content = payload.content
        await send_channel_dms(payload.guild_id, base_payload)
    elif payload.user_id:
        base_payload.content = payload.content
        await send_private_message(payload.user_id, base_payload)
    logger.debug(base_payload.to_dict())


async def upload_file(payload: MediaUploadPayload):
    """上传文件至QQ服务器，返回文件信息

    :param payload: MediaUploadPayload 上传文件的负载
    :return dict: 文件信息 or None
    :return url: 传入原url 用于处理频道图片

    ---

    详见：
    - 群聊/私聊：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/rich-media.html
    - 频道/频私：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/post_messages.html

    Powered by AxTn Network 2023-2025
    """
    logger.debug(f"上传文件 {payload.url} 至QQ服务器")
    if payload.event.event_type == "群消息":
        url = open_url + f"/v2/groups/{payload.event.group_id}/files"
    elif payload.event.event_type == "私信":
        url = open_url + f"/v2/users/{payload.event.user_id}/files"
    elif payload.event.event_type in ["频道艾特", "私域频道", "频道私信"]:
        url = payload.url  # 频道图片上传使用原url
        return MediaPayload({"url": payload.url})

    else:
        logger.error(f"上传文件失败: 不支持的消息类型 {payload.event.event_type}")
        return None
    async with aiohttp.ClientSession() as session:
        from src.Utils.GetAccessToken import ACCESS_TOKEN
        async with session.post(
            url,
            json=payload.to_dict(),
            headers={"Authorization": f"QQBot {ACCESS_TOKEN}"},
        ) as response:
            if response.status == 200:
                file_info = await response.json()
                return MediaPayload(file_info)
            else:
                message = await response.json()
                logger.error("上传文件失败: " + str(message))
            logger.debug(str(payload.to_dict()) + "，请求URL为：" + url)
