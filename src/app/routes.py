from fastapi import APIRouter, Request, Form, status, BackgroundTasks
from fastapi.responses import JSONResponse
from tortoise.exceptions import IntegrityError
import json

from src.Utils.Database import LoginForm
from src.Utils.EventClass import create_payload
from src.Utils.Processer import handle_event
from src.Utils.Config import config
from src.Utils.Logger import logger


router = APIRouter()

if config.Network.webui:
    async def check_logged_in(request: Request):
        """检查用户是否已登录"""
        if "user" in request.session:
            return True  # 已登录
        return False

    @router.post("/auth/login")
    async def get_login_info_post(
        request: Request,
        username: str = Form(..., alias="usernameoremail"), 
        password: str = Form(...)
    ):
        """登录接口
        
        用于后台处理表单数据和信息验证
        """
        valid = await LoginForm.get_user(username, password)
        if valid:
            request.session["user"] = username
            return JSONResponse({
                "success": True,
                "message": "登录成功",
                "redirect": "/"
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "用户名或密码错误"
            }, status_code=401)

    @router.post("/auth/register")
    async def register_user(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
    ):
        """注册接口

        用于对当前尝试注册的用户进行处理 存入数据库

        Args:
            username (str): 用户名
            email (str): 邮箱
            password (str): 密码
            confirm_password (str): 确认密码

        Returns:
            PlainTextResponse: 注册结果

        """
        # 验证密码匹配
        if password != confirm_password:
            return JSONResponse({
                "success": False,
                "error": "两次输入的密码不匹配"
            }, status_code=400)
        
        if await LoginForm.user_exists(username, email):
            return JSONResponse({
                "success": False,
                "error": "用户名或邮箱已被注册"
            }, status_code=400)
        
        try:
            await LoginForm.create_user(username, email, password)
            return JSONResponse({
                "success": True,
                "message": f"用户 {username} 注册成功!",
                "redirect": "/login"
            })
        except IntegrityError:
            return JSONResponse({
                "success": False,
                "error": "创建用户时发生冲突"
            }, status_code=409)
        except Exception as e:
            return JSONResponse({
                "success": False,
                "error": f"服务器错误: {str(e)}"
            }, status_code=500)

    @router.get("/auth/logout")
    async def logout(request: Request):
        """登出接口
        
        清除会话并重定向到登录页面
        """
        # 清除会话
        request.session.clear()
        # 重定向到登录页面
        return JSONResponse({
            "success": True,
            "message": "登出成功",
            "redirect": "/login"
        })

@router.post(config.Network.path)
async def bot_callback(request: Request, background_tasks: BackgroundTasks):
    """处理机器人回调

    该块用于处理机器人回调请求
    """
    body = await request.body()
    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        # return JSONResponse("Invalid JSON", status_code=status.HTTP_400_BAD_REQUEST)
        return JSONResponse({"message": "Invalid JSON", "code":400}, status_code=status.HTTP_400_BAD_REQUEST)
    payload = create_payload(data)
    logger.debug("=========================传入数据=========================")
    logger.debug(str(data))
    logger.debug("=======================传入数据结束=======================")
    if payload.is_validation():
        return await payload.generate_validation_response(request)
    background_tasks.add_task(handle_event, payload) # 交付后台执行其他耗时操作
    return {"op_code": 12, "d": {"event_id": payload.msg_id, "status": 0, "message": "success"}} # 立即返回Code12

@router.get("/api/heartbeat")
async def heartbeat(request: Request):
    """心跳检测接口"""
    header = request.headers.get("X-HeartBeat-Check")
    if header == "r u ok?":
        return JSONResponse({"heartbeat": "3Q"})
    else:
        return JSONResponse({"heartbeat": "有内鬼，终止交易！"}, status_code=400)