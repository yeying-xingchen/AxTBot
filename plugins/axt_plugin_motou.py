import re

from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent, MediaUploadPayload
from src.Utils.MessageSender import upload_file

from uapis_extension import get_from_api, apiconfig

__metadata__ = {
    "name": "[官方插件]摸摸头~",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "通过UnionOpenID或QQ号、图片获取摸头GIF",
    "official": True,
}


@command(["摸", "/摸"])
async def touch_handler(event: GroupMessageEvent):
    if event.content in ['摸','/摸','/摸 ','摸 ']:
        content = "\n=======摸一摸菜单=======" + "\n" + \
                   "/摸 [QQ号/图片] - 生成摸一摸GIF" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /摸 3889003621" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，请重试。多张图片只取第一张作为参照" + "\n" + \
                   "=========================="
        await event.reply(content=content)
    else:
        match = re.match(r"(?:/)?摸\s*(\d+)", event.content)
        if match:
            payload = MediaUploadPayload(file_type=1, event=event)
            try:
                contents = match.group(1)
            except ValueError:
                await event.reply(content="输入值有误，请输入QQ号或添加图片。")
                return
            try:
                int(contents)
                payload.url = f"{apiconfig.url}api/v1/image/motou?qq={contents}"
            except ValueError:
                payload.url = event.attachments[0].get("url")
            result = await upload_file(payload)
            if result:
                await event.reply(content=" ", media=result)
            else:
                contents = f"获取失败。\n请检查您的QQ号、UnionOpenID是否正确，或重新发起命令。若多次出现该问题，请提交至AxT社区"
                await event.reply(content=contents)
