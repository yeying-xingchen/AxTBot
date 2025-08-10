import threading, requests, time


from src.Utils.Logger import logger
from src.Utils.Config import config
from src.Utils.EventClass import AccessTokenPayload, OpenAPIErrorPayload

ACCESS_TOKEN: str = ""

async def get_access_token():
    threading.Thread(target=access_token, daemon=True,name="AccessToekn 鉴权获取线程").start()


def access_token():
    """获取access_token"""
    while True:
        logger.debug("正在获取access_token...")
        response = requests.post("https://bots.qq.com/app/getAppAccessToken", 
                      json={"appId": str(config.Bot.appid), "clientSecret": config.Bot.appsecret}
                    )
        response.raise_for_status
        code = response.status_code
        response = response.json()
        if code != 200:
            response = OpenAPIErrorPayload(**response)
            logger.error(f"获取access_token失败,错误码:{response.code}；原因:{response.message}")
            logger.debug("当前输出内容：" + str({"appId": str(config.Bot.appid),"clientSecret": config.Bot.appsecret}))
            time.sleep(60)
        else:
            response_json = AccessTokenPayload(**response)
            logger.debug(f"获取AccessToken成功，token: {response_json.access_token} 将于 {response_json.expires_in} s后过期")
            global ACCESS_TOKEN
            ACCESS_TOKEN = response_json.access_token
            time.sleep(response_json.expires_in - 30)