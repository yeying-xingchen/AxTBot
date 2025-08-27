import logging, datetime, coloredlogs, colorama, os, queue, atexit
from logging.handlers import RotatingFileHandler

from src.Utils.Config import config
# --- 初始化配置 ---
os.makedirs(config.Logger.dir, exist_ok=True)
colorama.init()


# --- 常量定义 ---
LOG_FORMAT = '[%(asctime)s][%(filename)s][%(levelname)s] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_NAME = f'log-{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
LOG_FILENAME = os.path.join(
    config.Logger.dir, 
    LOG_NAME
)

# --- 自定义日志级别 ---
EVENT_LEVEL_NUM = 11
SUCCESS_LEVEL_NUM = 21

def _register_log_level(level_num, level_name):
    """注册自定义日志级别并绑定方法"""
    logging.addLevelName(level_num, level_name)
    
    def log_method(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)
    
    setattr(logging.Logger, level_name.lower(), log_method)

_register_log_level(EVENT_LEVEL_NUM, 'EVENT')
_register_log_level(SUCCESS_LEVEL_NUM, 'SUCCESS')

# --- 主日志器配置 ---
logger = logging.getLogger('AxTBot-MainLogger')

log_level = getattr(logging, config.Logger.level.upper(), logging.INFO)
logger.setLevel(log_level)

# --- 文件处理器 ---
file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)



if config.Logger.log_split:
    logger.addHandler(
        RotatingFileHandler(
            LOG_NAME, 
            maxBytes=config.Logger.max_size * 1024 * 1024,
            backupCount=config.Logger.backup_count,
        )
    )

# --- 队列处理器 ---
log_queue = queue.Queue(maxsize=1000)

class LogQueueHandler(logging.Handler):
    """线程安全的日志队列处理器"""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        
    def emit(self, record):
        try:
            self.log_queue.put_nowait(self.format(record))
        except queue.Full:
            pass  # 队列满时静默丢弃新日志

queue_handler = LogQueueHandler(log_queue)
queue_handler.setFormatter(file_formatter)
logger.addHandler(queue_handler)

# --- 控制台美化输出 ---
level_styles = {
    'critical': {'color': 'red', 'bold': True},
    'error': {'background': 'red', 'color': 'white'},
    'warning': {'color': 'yellow'},
    'info': {'color': 'white'},
    'debug': {'color': 'blue'},
    'success': {'color': 'green', 'bold': True},
    'event': {'background': 'green', 'color': 'white', 'bold': True}
}

coloredlogs.install(
    level=log_level,
    logger=logger,
    fmt=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    level_styles=level_styles,
    field_styles={
        'asctime': {'color': 'cyan'},
        'levelname': {'color': 'magenta'}
    }
)

# --- 过滤器配置 ---
class AccessLogFilter(logging.Filter):
    """过滤特定访问日志"""
    def filter(self, record):
        msg = record.getMessage()
        return not (
            '"POST /webhook HTTP/1.1"' in msg or 
            'Invalid HTTP request received.' in msg
        )

class EndpointFilter(logging.Filter):
    def __init__(self, paths: list):
        self.paths = paths
    
    def filter(self, record: logging.LogRecord) -> bool:
        # 检查日志消息中是否包含要屏蔽的路径
        return not any(path in record.getMessage() for path in self.paths)

# 配置日志过滤器
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(paths=["/bot/callback"]))
# --- 完全接管Uvicorn日志 ---
def hijack_uvicorn_loggers():
    """接管所有Uvicorn日志记录器"""
    # 禁用Uvicorn默认日志配置
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    
    if config.Logger.uvicorn:
    # 创建新的Uvicorn日志器使用我们的配置
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.handlers = logger.handlers
        uvicorn_logger.propagate = False
        
        uvicorn_error_logger = logging.getLogger("uvicorn.error")
        uvicorn_error_logger.handlers = logger.handlers
        uvicorn_error_logger.propagate = False
        
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.handlers = logger.handlers
        uvicorn_access_logger.propagate = False
        uvicorn_access_logger.addFilter(AccessLogFilter())
        
        # 设置相同的日志级别
        uvicorn_logger.setLevel(log_level)
        uvicorn_error_logger.setLevel(log_level)
        uvicorn_access_logger.setLevel(log_level)

# 立即接管Uvicorn日志
hijack_uvicorn_loggers()

# --- 资源清理方法 ---
def shutdown_logging():
    """安全关闭日志系统"""
    file_handler.close()
    logger.removeHandler(queue_handler)
    logging.shutdown()

# 注册程序退出时的清理
atexit.register(shutdown_logging)