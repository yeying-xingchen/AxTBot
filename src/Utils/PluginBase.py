import sys, os, importlib.util
from typing import Dict, Callable, Optional
from pathlib import Path

from src.Utils.Logger import logger
from src.Utils.Config import config


# 全局命令注册表
COMMAND_REGISTRY: Dict[str, Dict] = {}
PLUGIN_DIR: Optional[str] = None

def command(names, event_type: type = None):
    """命令注册装饰器（支持多个命令名）"""
    def decorator(func):
        # 确保 names 是列表类型
        name_list = [names] if isinstance(names, str) else names
        
        for name in name_list:
            if name in COMMAND_REGISTRY:
                logger.error(f"⚠️ 命令冲突: '{name}' 已存在")
            else:
                # 为每个命令名注册相同的处理函数和事件类型
                COMMAND_REGISTRY[name] = {
                    'handler': func,
                    'event_type': event_type
                }
        return func
    return decorator

async def get_command_handler(cmd: str, event_class: type) -> Optional[Callable]:
    """获取命令处理函数（添加事件类型检查）"""
    if cmd not in COMMAND_REGISTRY:
        return None
    
    handler_info = COMMAND_REGISTRY[cmd]
    handler = handler_info['handler']
    supported_event = handler_info['event_type']
    
    # 检查事件类型是否匹配
    if supported_event is None or issubclass(event_class, supported_event):
        return handler
    
    return None  # 事件类型不匹配

async def initialize_plugins():
    """初始化插件系统（只执行一次）"""
    global PLUGIN_DIR
    
    if PLUGIN_DIR is not None:
        return  # 已经初始化过
    
    # 获取插件目录路径

    plugin_dir = Path(config.Plugins.dir)
    PLUGIN_DIR = str(plugin_dir)
    
    # 确保插件目录存在
    os.makedirs(plugin_dir, exist_ok=True)
    
    # 加载所有插件
    logger.debug(f"插件管理器 >>> 从 {plugin_dir} 目录加载插件")
    
    for file in plugin_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
            
        plugin_name = file.stem
        logger.info(f"插件管理器 >>>   - 发现插件: {plugin_name}")
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(plugin_name, file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            # 调用初始化函数（如果有）
            if hasattr(module, "initialize"):
                module.initialize()
                logger.info(f"插件管理器 >>>     插件初始化完成")
        except Exception as e:
            logger.info(f"插件管理器 >>>     加载失败: {str(e)}")
    logger.info(f"插件管理器 >>>     所有插件加载结束")

async def shutdown_plugins():
    """关闭插件系统"""
    logger.info("插件管理器 >>> 关闭插件系统")
    # 调用所有插件的shutdown函数
    for module in sys.modules.values():
        if hasattr(module, "shutdown"):
            try:
                if module.__name__ == "logging":
                    continue
                module.shutdown()
                logger.info(f"插件管理器 >>>   - 已关闭: {module.__name__}")
            except Exception as e:
                logger.error(f"插件管理器 >>>   - 关闭失败: {module.__name__} - {str(e)}")
    # 清理命令注册表
    COMMAND_REGISTRY.clear()