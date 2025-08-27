from fastapi import APIRouter, Request, Form, status, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from tortoise.exceptions import IntegrityError
import json, psutil, os, jwt, glob, zipfile, shutil, re
from datetime import datetime, timedelta

from src.Utils.Database import LoginForm
from src.Utils.EventClass import create_payload
from src.Utils.Processer import handle_event
from src.Utils.Config import config
from src.Utils.Logger import logger
from src.Utils.MessageState import AppState, MessageStatistics
from src.Utils.PluginBase import get_plugins_list, toggle_plugin, install_plugin, uninstall_plugin


router = APIRouter()
SECRET_KEY = config.Advanced.session_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def create_access_token(username: str) -> str:
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": username,
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 验证 JWT 令牌
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "data": {"title": "令牌已过期", "description": "请重新登录以获取新的令牌。"}}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "data": {"title": "无效的令牌", "description": "请提供有效的令牌。"}}
        )

# 获取当前用户依赖项
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"code": 401, "data": {"title": "未授权", "description": "请提供有效的令牌。"}},
            headers={"Authorization": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    return payload

if config.Network.webui:
    @router.post("/auth/login")
    async def get_login_info_post(
        request: Request,
        username: str = Form(..., alias="usernameoremail"), 
        password: str = Form(...),
    ):
        """登录接口"""
        valid = await LoginForm.get_user(username, password)
        if valid:
            # 创建 JWT 令牌
            access_token = create_access_token(username)
            
            # 返回令牌而不是设置 session
            return JSONResponse(content={
                "code": 200,
                "data": {
                    "title": "登录成功",
                    "description": "欢迎回来！",
                    "access_token": access_token,
                },
            })
        else:
            return JSONResponse(content={
                "code": 401,
                "data": {
                    "title": "登录失败",
                    "description": "用户名或密码错误，请重试。",
                }
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
            return JSONResponse(content={
                "code": 400,
                "data": {
                    "title": "密码不匹配",
                    "description": "请确保密码和确认密码一致。"
                }
            }, status_code=400)
        
        if await LoginForm.user_exists(username, email):
            return JSONResponse(content={
                "code": 400,
                "data": {
                    "title": "用户/邮箱已存在",
                    "description": "请选择其他用户名或邮箱。"
                }
            }, status_code=400)
        
        try:
            await LoginForm.create_user(username, email, password)
            return JSONResponse(content={
                "code": 200,
                "data": {
                    "title": "注册成功",
                    "description": f"用户 {username} 注册成功，请登录以继续。"
                }
            }, status_code=200)
        except IntegrityError:
            return JSONResponse(content={
                "code": 409,
                "data": {
                    "title": "用户/邮箱已存在",
                    "description": "该用户名或邮箱已存在，请选择其他用户名或邮箱。"
                }
            }, status_code=409)
        except Exception as e:
            return JSONResponse(content={
                "code": 500,
                "data": {
                    "title": "服务器错误",
                    "description": "服务器内部错误，请稍后再试。\n错误信息: " + str(e)
                }
            }, status_code=500)

    @router.get("/auth/logout")
    async def logout():
        """登出接口"""
        return JSONResponse(content={
            "code": 200,
            "data": {
                "title": "登出成功",
                "description": "您已成功登出，感谢您的使用！"
            }
        })
        
    @router.get("/auth/status")
    async def check_login_status(request: Request):
        """检查登录状态接口"""
        # 从 Authorization 头获取令牌
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(content={
                "code": 401,
                "data": {
                    "title": "未授权",
                    "description": "请提供有效的令牌。"
                }
            }
            , status_code=401)
        
        token = auth_header.split(" ")[1]
        try:
            payload = verify_token(token)
            return JSONResponse(content={
                "code": 200,
                "data": {
                    "title": "已授权",
                    "description": "您已授权，请继续。",
                    "username": payload.get("sub")
                },
            })
        except Exception:
            return payload
    @router.post("/auth/refresh")
    async def refresh_token(request: Request):
        """刷新令牌接口"""
        # 从 Authorization 头获取令牌
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(content={
                "code": 401,
                "data": {
                    "title": "未授权",
                    "description": "请提供有效的令牌。"
                }
            }, 
            status_code=401)
        token = auth_header.split(" ")[1]
        try:
            payload = verify_token(token)
            # 创建新令牌
            new_token = create_access_token(payload.get("sub"))
            return JSONResponse(content={
                "code": 200,
                "data": {
                    "title": "获取成功",
                    "description": "令牌刷新成功，前一个令牌会在申请后24小时内失效，请使用新令牌。",
                    "access_token": new_token,
                    "token_type": "bearer"
                }
            })
        except HTTPException as e:
            return JSONResponse(content={
                "code": 500,
                "data": {
                    "title": "服务器错误",
                    "description": "服务器内部错误，请稍后再试。\n错误信息: " + str(e)
                }}, 
                status_code=500)

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
    return {"op_code": 12, "d": {"event_id": payload.id, "status": 0, "message": "success"}} # 立即返回Code12

@router.get("/api/heartbeat")
async def heartbeat(request: Request):
    """心跳检测接口"""
    header = request.headers.get("X-HeartBeat-Check")
    if header == "r u ok?":
        return JSONResponse({"heartbeat": "3Q"})
    else:
        return JSONResponse({"heartbeat": "有内鬼，终止交易！"}, status_code=400)

@router.get("/bot/get_message_info")
async def get_message_info(request: Request, current_user: str = Depends(get_current_user)):
    start_time = AppState.get_start_time()
    stats_service = MessageStatistics(start_time)
    stats = await stats_service.get_stats()
    response = {"code": 200, "data": stats}
    return JSONResponse(response)

@router.get("/bot/get_system_info")
async def get_system_info(current_user: str = Depends(get_current_user)):
    info = {}
    # 获取CPU信息
    info['cpu_usage'] = f"{psutil.cpu_percent(interval=1)}%"

    # 获取内存信息
    memory = psutil.virtual_memory()
    memory_total_gb = memory.total / (1024 ** 3)
    memory_used_gb = memory.used / (1024 ** 3)
    info['ram'] = f"{memory_used_gb:.2f}/{memory_total_gb:.2f}GB"
    info['ram_usage'] = f"{memory.percent}%"
    response = {"code": 200, "data": info}
    return JSONResponse(response)

@router.get("/bot/get_plugins_list")
async def plugins_list_handler(current_user: str = Depends(get_current_user)):
    """获取插件列表接口
    
    返回插件列表信息
    """
    result = await get_plugins_list()
    return JSONResponse(result, result.get("code"))

@router.post("/bot/toggle_plugin")
async def toggle_plugin_handler(request: Request, current_user: str = Depends(get_current_user)):
    """启用/禁用插件接口
    
    返回插件操作结果
    """
    # 从请求体中获取数据
    try:
        body = await request.json()
        name = body.get("name")
        enable = body.get("enable")
    except:
        return JSONResponse({"code": 400, "data": {
            "title": "无效的请求数据",
            "description": "请提供有效的请求数据。"
        }},
        status_code=400)
    
    result = await toggle_plugin(name, enable)
    return JSONResponse(result, result.get("code"))

@router.post("/bot/install_plugin")
async def install_plugin_handler(request: Request, current_user: str = Depends(get_current_user)):
    """安装插件接口
    
    返回插件安装结果
    """
    # 从请求体中获取数据
    try:
        body = await request.json()
        url = body.get("url")
        version = body.get("version")
    except:
        return JSONResponse({"code": 400, "data": {
            "title": "无效的请求数据",
            "description": "请提供有效的请求数据。"
        }},
        status_code=400)
    result = await install_plugin(url, version)
    return JSONResponse(result, result.get("code"))

@router.post("/bot/uninstall_plugin")
async def uninstall_plugin_handler(request: Request, current_user: str = Depends(get_current_user)):
    """卸载插件接口
    
    返回插件卸载结果
    """
    # 从请求体中获取数据
    try:
        body = await request.json()
        name = body.get("name")
    except:
        return JSONResponse({"code": 400, "data": {
            "title": "无效的请求数据",
            "description": "请提供有效的请求数据。"
        }},
        status_code=400)
    
    result = await uninstall_plugin(name)
    return JSONResponse(result, result.get("code"))

# 系统设置页面接口
@router.get("/settings/get")
async def get_settings(current_user: str = Depends(get_current_user)):
    """获取设置接口
    
    返回系统设置信息
    """
    
    try:
        # 构建设置对象
        settings = {
            "botName": config.Bot.nickname,
            "autoUpdate": config.Advanced.update,
            "logLevel": config.Logger.level,
            "qqNumber": config.Bot.qq,
            "qqProtocol": "QQ官方机器人",
            "qqWsUrl": f"{config.Network.host}:{config.Network.port}{config.Network.path}",
            "enableWhitelist": False,
            "whitelistUsers": [],
            "enableBlacklist": False,
            "blacklistUsers": [],
            "enableErrorNotifications": config.Notice.enable,
            "notifyEmail": config.Notice.enable,
            "notificationEmail": config.Notice.sender,
            "maxConnections": 100,
            "cacheSize": 512,
            "dbPoolSize": 10,
            "enableDebugMode": config.Advanced.debug
        }
        
        response = {"code": 200, "data": {"settings": settings}}
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({
            "code": 500,
            "data": {
                "title": "服务器错误",
                "description": f"获取设置时发生错误: {str(e)}"
            }
        }, status_code=500)

# 数据管理页面接口
@router.get("/data/stats")
async def get_data_stats(current_user: str = Depends(get_current_user)):
    """获取数据统计接口
    
    返回数据统计信息
    """
    # 计算总数据大小
    total_size = 0
    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "data")):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    
    # 计算日志大小
    log_size = 0
    log_files = glob.glob(os.path.join(os.getcwd(), "logs", "*.log"))
    for log_file in log_files:
        if os.path.isfile(log_file):
            log_size += os.path.getsize(log_file)
    
    stats = {
        "totalSize": f"{total_size / (1024 * 1024):.2f} MB",
        "logSize": f"{log_size / (1024 * 1024):.2f} MB"
    }
    
    response = {"code": 200, "data": stats}
    return JSONResponse(response)

@router.get("/data/backups")
async def get_backups(current_user: str = Depends(get_current_user)):
    """获取备份列表接口
    
    返回备份列表信息
    """
    backup_dir = os.path.join(os.getcwd(), "data", "backups")
    backups = []
    
    if os.path.exists(backup_dir):
        for file in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file)
            if os.path.isfile(file_path) and file.endswith(".zip"):
                file_stats = os.stat(file_path)
                backups.append({
                    "name": file,
                    "size": file_stats.st_size,
                    "date": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                })
    else:
        os.makedirs(backup_dir, exist_ok=True)
    response = {"code": 200, "data": {"backups": backups}}
    return JSONResponse(response)

@router.post("/data/backup")
async def create_backup(current_user: str = Depends(get_current_user)):
    """创建备份接口
    
    创建系统备份
    """
    try:
        # 创建备份目录
        backup_dir = os.path.join(os.getcwd(), "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # 创建临时目录
        temp_dir = os.path.join(os.getcwd(), "data", "temp_backup")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 复制需要备份的文件到临时目录
        # 复制配置文件
        if os.path.exists("config.yaml"):
            shutil.copy2("config.yaml", os.path.join(temp_dir, "config.yaml"))
        
        # 复制数据目录
        data_dir = os.path.join(os.getcwd(), "data")
        for item in os.listdir(data_dir):
            if item != "backups" and item != "temp_backup":
                src = os.path.join(data_dir, item)
                dst = os.path.join(temp_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        
        # 创建备份文件名
        backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 创建ZIP文件
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加临时目录中的所有文件到ZIP
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径，以便在ZIP中保持目录结构
                    rel_path = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, rel_path)
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return JSONResponse({
            "code": 200,
            "data": {
                "title": "备份成功",
                "description": f"系统备份已成功创建: {backup_filename}"
            }
        })
    except Exception as e:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return JSONResponse({
            "code": 500,
            "data": {
                "title": "服务器错误",
                "description": f"创建备份时发生错误: {str(e)}"
            }
        }, status_code=500)

@router.post("/data/restore")
async def restore_backup(request: Request, current_user: str = Depends(get_current_user)):
    """恢复备份接口
    
    恢复系统备份
    """
    try:
        body = await request.json()
        backup_name = body.get("backupName")
        
        if not backup_name:
            return JSONResponse({
                "code": 400,
                "data": {
                    "title": "无效的请求数据",
                    "description": "请提供有效的备份文件名。"
                }
            }, status_code=400)
        
        # 检查备份文件是否存在
        backup_dir = os.path.join(os.getcwd(), "data", "backups")
        backup_path = os.path.join(backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return JSONResponse({
                "code": 404,
                "data": {
                    "title": "备份文件不存在",
                    "description": f"找不到备份文件: {backup_name}"
                }
            }, status_code=404)
        
        # 创建临时目录用于解压备份
        temp_dir = os.path.join(os.getcwd(), "data", "temp_restore")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 解压备份文件到临时目录
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # 恢复配置文件
        config_backup = os.path.join(temp_dir, "config.yaml")
        if os.path.exists(config_backup):
            shutil.copy2(config_backup, os.path.join(os.getcwd(), "config.yaml"))
        
        # 恢复数据文件
        data_dir = os.path.join(os.getcwd(), "data")
        for item in os.listdir(temp_dir):
            if item != "backups" and item != "temp_restore" and item != "config.yaml":
                src = os.path.join(temp_dir, item)
                dst = os.path.join(data_dir, item)
                
                # 如果是目录，先删除目标目录再复制
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                # 如果是文件，直接复制覆盖
                elif os.path.isfile(src):
                    shutil.copy2(src, dst)
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return JSONResponse({
            "code": 200,
            "data": {
                "title": "恢复成功",
                "description": f"系统已成功从备份 {backup_name} 恢复"
            }
        })
    except Exception as e:
        # 清理临时目录
        temp_dir = os.path.join(os.getcwd(), "data", "temp_restore")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        return JSONResponse({
            "code": 500,
            "data": {
                "title": "服务器错误",
                "description": f"恢复备份时发生错误: {str(e)}"
            }
        }, status_code=500)

@router.get("/data/backup")
async def download_backup(request: Request, current_user: str = Depends(get_current_user)):
    """下载备份接口
    
    下载指定备份文件
    """
    response = await request.json()
    name = response.get("backupName")
    
    backup_dir = os.path.join(os.getcwd(), "data", "backups")
    backup_path = os.path.join(backup_dir, name)
    
    if not os.path.exists(backup_path):
        return JSONResponse({
            "code": 404,
            "data": {
                "title": "备份文件不存在",
                "description": f"找不到备份文件: {name}"
            }
        }, status_code=404)
    
    # 返回文件响应，允许用户下载备份文件
    return FileResponse(
        path=backup_path,
        filename=name,
        media_type="application/zip"
    )

@router.delete("/data/backup")
async def delete_backup(request: Request, current_user: str = Depends(get_current_user)):
    """删除备份接口
    
    删除指定备份文件
    """
    response = await request.json()
    name = response.get("backupName")
    
    backup_dir = os.path.join(os.getcwd(), "data", "backups")
    backup_path = os.path.join(backup_dir, name)
    
    if not os.path.exists(backup_path):
        return JSONResponse({
            "code": 404,
            "data": {
                "title": "备份文件不存在",
                "description": f"找不到备份文件: {name}"
            }
        }, status_code=404)
    
    try:
        os.remove(backup_path)
        return JSONResponse({
            "code": 200,
            "data": {
                "title": "删除成功",
                "description": f"备份文件 {name} 已成功删除"
            }
        })
    except Exception as e:
        return JSONResponse({
            "code": 500,
            "data": {
                "title": "服务器错误",
                "description": f"删除备份文件时发生错误: {str(e)}"
            }
        }, status_code=500)

@router.get("/data/logs")
async def get_logs(current_user: str = Depends(get_current_user)):
    """获取日志接口
    
    获取系统日志
    """
    try:
        logs = []
        # 获取日志目录下的所有日志文件，按修改时间排序，取最新的
        log_dir = config.Logger.dir
        log_files = glob.glob(os.path.join(log_dir, "log-*.log"))
        
        if log_files:
            # 按修改时间排序，获取最新的日志文件
            latest_log_file = max(log_files, key=os.path.getmtime)
            
            if os.path.exists(latest_log_file):
                with open(latest_log_file, "r", encoding="utf-8") as f:
                    log_lines = f.readlines()
                
                # 解析日志行
                # 假设日志格式为：[2023-01-01 12:00:00] [INFO] 日志内容
                log_pattern = r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\[(\w+)\] (.+)"
                
                for line in log_lines:
                    match = re.match(log_pattern, line)
                    if match:
                        timestamp_str, level, message = match.groups()
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").isoformat()
                        logs.append({
                            "timestamp": timestamp,
                            "level": level.lower(),
                            "message": message.strip()
                        })
        
        response = {"code": 200, "data": {"logs": logs}}
        return JSONResponse(response)
    except Exception as e:
        return JSONResponse({
            "code": 500,
            "data": {
                "title": "获取失败",
                "description": f"获取日志时发生错误: {str(e)}"
            }
        }, status_code=500)
