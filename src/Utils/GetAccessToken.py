import threading, requests, time

from src.Utils.Logger import logger
from src.Utils.Config import config
from src.Utils.EventClass import AccessTokenPayload

ACCESS_TOKEN = ""
TOKEN_LOCK = threading.Lock()

def token_manager():
    while True:
        logger.debug("正在获取access_token...")
        try:
            # 添加超时和重试机制
            response = requests.post(
                "https://bots.qq.com/app/getAppAccessToken",
                json={"appId": str(config.Bot.appid), "clientSecret": config.Bot.appsecret},
                timeout=10
            )
            response.raise_for_status()  # 修复：添加括号调用方法
            
            token_data = AccessTokenPayload(**response.json())
            logger.debug(f"获取AccessToken成功，token: {token_data.access_token} 将于 {token_data.expires_in}s后过期")
            
            with TOKEN_LOCK:
                global ACCESS_TOKEN
                ACCESS_TOKEN = token_data.access_token
            
            # 分段睡眠，避免长时间阻塞
            sleep_time = token_data.expires_in - 30
            while sleep_time > 0:
                chunk = min(sleep_time, 300)  # 每5分钟唤醒一次
                time.sleep(chunk)
                sleep_time -= chunk
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            time.sleep(10)  # 短时间等待后重试
        except Exception as e:
            logger.error(f"意外错误: {str(e)}")
            time.sleep(30)

async def get_access_token():
    # 启动线程
    threading.Thread(target=token_manager, daemon=True, name="AccessToekn 鉴权获取线程").start()