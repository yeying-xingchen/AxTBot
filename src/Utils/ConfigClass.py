from pydantic import BaseModel, field_validator
from typing import Optional

class QQ_BOT_BaseInfo(BaseModel):
    qq: int
    appid: int
    token: str
    appsecret: str

class NetworkConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    path: Optional[str] = "/webhook"
    ssl: bool = False
    ssl_path: str = None if ssl else "data"  # 如果不启用SSL，则不需要路径 
    webui: bool = False

    @field_validator('port')
    def validate_port(cls, v):
        if v not in [80, 443, 8080, 8443]:
            raise ValueError("配置项错误：Webhook端口号必须是80, 443, 8080或8443\n详见：https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/event-emit.html#webhook%E6%96%B9%E5%BC%8F")
        return v

class LoggerConfig(BaseModel):
    level: str = "INFO" 
    dir: str = "logs"
    uvicorn: bool = False
    log_split: bool = False
    max_size: int = 10
    backup_count: int = 3

class NoticeConfig(BaseModel):
    enable: bool = False
    host: str = "smtp.xxxx.com"
    port: int = 666
    sender: str
    password: str
    receiver: list

class PluginConfig(BaseModel):
    dir: str = "plugins"

class AdvancedConfig(BaseModel):
    debug: bool = False
    update: bool = True
    session_secret: str = "xxxxxxxxxxxxxxxxxxxxxxxx"

    @field_validator('debug')
    def validate_debug(cls, v):
        if not isinstance(v, bool):
            raise ValueError("配置项错误：Debug模式必须是布尔值")
        return v

class DatabaseConfig(BaseModel):
    """数据库配置"""
    connections: dict = {
        "default": "sqlite://data/web_user.db",
        "message": "sqlite://data/message.db",
        "messagesent": "sqlite://data/message_sent.db"
        }
    apps: dict = {
        "models": {
            "models": ["src.Utils.Database", "aerich.models"],
            "default_connection": "default",
        },
        "message": {
            "models": ["src.Utils.EventSender"],
            "default_connection": "message",
        },
        "messagesent": {
            "models": ["src.Utils.EventSender"],
            "default_connection": "messagesent",
        }
    }
    @property
    def TORTOISE_ORM(self):
        """返回Tortoise ORM配置"""
        return {
            "connections": self.connections,
            "apps": self.apps
        }

class ConfigBase(BaseModel):
    Bot: QQ_BOT_BaseInfo
    Network: NetworkConfig
    Logger: LoggerConfig
    Notice: NoticeConfig
    Plugins: PluginConfig
    Advanced: AdvancedConfig
    Database: DatabaseConfig