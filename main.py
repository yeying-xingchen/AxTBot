import os, threading, datetime, sys, asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise

from src.app import create_app
from src.app.routes import router as main_router
from src.app.exceptions import (
    custom_http_exception_handler,
    universal_exception_handler,
    custom_validation_exception_handler,
)

from src.Utils.Config import config  # 导入配置模块
from src.Utils.HeartBeat import heartbeat_check_start
from src.Utils.MessageState import AppState

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
APP_START_TIME = datetime.datetime.now()
AppState.set_start_time(APP_START_TIME)
app = create_app()
register_tortoise(
    app,
    config=config.Database.TORTOISE_ORM,
    generate_schemas=True,  # 自动创建表结构
    add_exception_handlers=True,  # 添加数据库异常处理
)
app.include_router(main_router)
app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, universal_exception_handler)
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)

uvicorn_config = {
    "app": "main:app",
    "host": config.Network.host,
    "port": config.Network.port,
    "log_config": None,
    "ssl_keyfile": config.Network.ssl_path + "/key.pem" if config.Network.ssl else None,
    "ssl_certfile": config.Network.ssl_path + "/cert.pem" if config.Network.ssl else None
}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.mkdir("data")
    import uvicorn
    from src.Utils.Logger import logger
    if config.Advanced.debug:
        logger.debug("Debug模式已启用，应用将以调试模式运行")
        logger.warning("请不要将此模式用于生产环境，请勿将截图提供给任何陌生人")
        
        # 调试模式特有配置
        uvicorn_config.update({
            "reload": True,
            "log_level": "debug"  # 使用debug级别的日志记录
        })
    else:
        # 非调试模式证书检查
        # 调整条件顺序：先检查SSL开关
        if config.Network.ssl:
            # 任意一个文件不存在则触发错误
            key_path = os.path.join(config.Network.ssl_path, "key.pem")
            cert_path = os.path.join(config.Network.ssl_path, "cert.pem")
            if not os.path.exists(key_path) or not os.path.exists(cert_path):
                logger.error(f"SSL证书缺失！请确保目录中存在cert.pem和key.pem: {config.Network.ssl_path} (err:-56)")
                exit(-56)
        
        # 生产模式特有配置
        uvicorn_config.update({
            "reload": False,
            "log_level": config.Logger.level.lower()  # 使用配置文件中的日志级别
        })
    if config.Network.ssl:
        logger.info("SSL已启用，应用将使用HTTPS协议")
        logger.debug(f"程序启动时间: {APP_START_TIME}")
    else:
        logger.warning("SSL未启用，应用将使用HTTP协议")
        logger.warning("请注意：HTTP协议下，开放平台无法发包至本框架，造成消息不可达，请在生产环境中启用SSL")
    logger.info("正在启动守护线程...")
    threading.Thread(target=heartbeat_check_start, daemon=True, name="心跳检查线程").start()
    uvicorn.run(
        loop="asyncio", 
        http="httptools" if sys.platform != "win32" else "auto",
        timeout_keep_alive=1,  # 空闲连接1秒关闭
        timeout_graceful_shutdown=1,  # 关闭时等待1秒
        **uvicorn_config
    )