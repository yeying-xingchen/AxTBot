import os, sys, yaml, questionary
from pathlib import Path
from pydantic import ValidationError

from src.Utils.ConfigClass import ConfigBase

def validate_required(input_text):
    """验证输入非空且长度合法"""
    if len(input_text.strip()) == 0:
        return "⚠️ 错误：内容不能为空！"
    return True  # 验证通过

def generate_config_wizard() -> ConfigBase:
    """交互式配置向导"""
    print("\n🔧 欢迎使用配置向导，我们将引导您创建配置文件")
    
    # 收集配置信息
    config_data = {
        "Bot": {
            "qq": questionary.text(
                "[必填]请输入开放平台提供的机器人QQ号:",
                validate=validate_required,
            ).ask(),
            "nickname": questionary.text(
                "[可选]请输入机器人昵称:",
                validate=validate_required,
            ).ask(),
            "appid": questionary.text(
                "[必填]请输入开放平台提供的机器人AppID:",
                validate=validate_required,
            ).ask(),
            "token": questionary.text(
                "[必填]请输入开放平台提供的机器人Token:",
                validate=validate_required,
            ).ask(),
            "appsecret": questionary.text(
                "[必填]请输入开放平台提供的机器人AppSecret:",
                validate=validate_required,
            ).ask()
        },
        "Network": {
            "host": "0.0.0.0",
            "port": questionary.select(
                "[可选]请输入Webhook监听的端口号 (80, 443, 8080, 8443):", 
                choices=["80", "443", "8080", "8443"],
                default="8080",
            ).ask(),
            "path": questionary.text(
                "[可选]请输入Webhook路径:", 
                validate=validate_required,
                default="/webhook",
            ).ask(),
            "ssl": False,
            "ssl_path": "data",
            "webui": questionary.confirm(
                "[可选]是否启用WebUI?",
                default=False
            ).ask(),
        },
        "Logger": {
            "level": questionary.select(
                "[可选]选择日志级别:",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default="INFO",
            ).ask(),
            "dir": "logs",
            "uvicorn": False,
            "log_split": False,
            "max_size": 10,
            "backup_count": 3
        },
        "Notice": {
            "enable": questionary.confirm(
                "[可选]是否启用邮件通知? 启用后请至配置文件中配置收发件信息",
                default=False
            ).ask(),
            "host": "发件地址",
            "port": 666,
            "password": "密码",
            "sender": "发件邮箱",
            "receiver": []
        },
        "Plugins": {
            "dir": "plugins"
        },
        "Advanced": {
            "debug": False,
            "update": True,
            "session_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        },
        "Database": {
            "connections": {"default": "sqlite://data/web_user.db","message": "sqlite://data/message.db","messagesent": "sqlite://data/message_sent.db"},
            "apps": {
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
        }
    }
    
    # 转换数据类型
    config_data['Bot']['qq'] = int(config_data['Bot']['qq'])
    config_data['Bot']['appid'] = int(config_data['Bot']['appid'])
    config_data['Network']['port'] = int(config_data['Network']['port'])
    
    # 创建配置对象
    try:
        return ConfigBase(**config_data)
    except ValidationError as e:
        print(f"❌ 配置验证失败: {e}")
        sys.exit(1)

def save_config(config: ConfigBase, path: Path):
    """保存配置到文件"""
    config_dict = config.model_dump()
    
    # 添加注释
    yaml_content = "# AxTBot-Public v2.1 日志自动生成\n\n# 请注意：更多配置信息请前往 https://docs.axtn.net/AxTBot-v2.1/config/global.html 明确详细规定"
    
    # 生成带注释的YAML
    for section, fields in config_dict.items():
        field_info = ConfigBase.model_fields[section]
        desc = field_info.description or section
        
        yaml_content += f"# {desc}\n"
        yaml_content += yaml.dump({section: fields}, default_flow_style=False, sort_keys=False)
        yaml_content += "\n"
    
    # 保存文件
    with open(path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"✅ 配置文件已生成: {path}\n请阅读以下文档：https://docs.axtn.net/axtbot/v2.1/config/global.html 了解配置项含义")

def load_config(config_path: Path) -> ConfigBase:
    """加载配置，如果不存在则引导创建"""
    # 情况1: 配置文件不存在
    if not config_path.exists():
        print(f"⚠️ 配置文件 {config_path} 不存在")
        
        if questionary.confirm("是否现在创建配置文件?", default=True).ask():
            config = generate_config_wizard()
            save_config(config, config_path)
            return config
        else:
            print("❌ 配置文件是必需的，应用无法启动")
            sys.exit(1)
    
    # 情况2: 配置文件为空
    if os.path.getsize(config_path) == 0:
        print(f"⚠️ 配置文件 {config_path} 为空")
        print(f"⚠️ 请注意：配置文件生成向导会覆盖原配置文件，请确保已保存好原配置文件！")
        
        if questionary.confirm("是否重新生成配置文件?", default=True).ask():
            config = generate_config_wizard()
            save_config(config, config_path)
            return config
        else:
            print("❌ 配置文件无效，应用无法启动")
            sys.exit(1)
    
    # 情况3: 正常加载配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return ConfigBase(**config_data)
    except (yaml.YAMLError, ValidationError) as e:
        print(f"❌ 配置文件解析错误: {e}")
        print(f"⚠️ 请注意：配置文件生成向导会覆盖原配置文件，请确保已保存好原配置文件！")
        
        if questionary.confirm("是否尝试修复配置文件?", default=True).ask():
            config = generate_config_wizard()
            save_config(config, config_path)
            return config
        else:
            print("❌ 配置文件无效，应用无法启动")
            sys.exit(1)