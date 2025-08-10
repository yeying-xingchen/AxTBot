import smtplib
from email.mime.text import MIMEText
from email.header import Header

from src.Utils.Logger import logger
from src.Utils.Config import config

async def send_mail_notice(message):
    if not config.Notice.enable: return
    message = """管理员 您好！
本邮件由AxTBot-Public v2.1.0+00715 自动发送
如下是心跳检测的报错信息：
""" + str(message)
    msg = MIMEText(str(message), "html", "utf-8")  # 正文（html格式）
    msg["Subject"] = Header("请检查机器人运行状态 - AxTBot自动数据上报", "utf-8")      # 主题
    msg["From"] = config.Notice.sender                           # 发件人
    msg["To"] = ", ".join(config.Notice.receiver)                 # 收件人

    try:
        # 创建SSL安全连接
        server = smtplib.SMTP_SSL(config.Notice.host, config.Notice.port)
        server.login(config.Notice.sender, config.Notice.password)         # 登录邮箱
        server.sendmail(config.Notice.sender, list(config.Notice.receiver), msg.as_string())  # 发送
        logger.debug("心跳检查组件 >>> 邮件发送成功！")
    except Exception as e:
        logger.error(f"心跳检测组件 >>> 发送失败: {e}")
        raise e
    finally:
        server.quit()  # 关闭连接