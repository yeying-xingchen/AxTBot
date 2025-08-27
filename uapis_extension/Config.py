from pydantic import BaseModel
import yaml, os


if not os.path.exists("./data/apiconfig.yaml"):
    with open("./data/apiconfig.yaml", "w", encoding="utf-8") as f:
        f.write("url: https://uapis.cn\n")

class ConfigBase(BaseModel):
    url: str = "https://uapis.cn"

with open("./data/apiconfig.yaml", "r", encoding="utf-8") as f:
    yaml_config = yaml.safe_load(f)
    if not yaml_config["url"].endswith("/"):
        yaml_config["url"] += "/"
apiconfig = ConfigBase(**yaml_config)
