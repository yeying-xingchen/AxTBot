import requests, urllib3, tomli, pathlib, sys

from src.Utils.Logger import logger

async def get_latest_release(owner, repo, verify_ssl=False):
    """获取最新 release 信息"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    urllib3.disable_warnings()
    response = requests.get(
        url,
        verify=verify_ssl
    )
    if response.status_code == 200:
        release = response.json()
        return {
            "tag": release["tag_name"],
            "name": release["name"],
            "published_at": release["published_at"],
            "url": release["html_url"]
        }
    else:
        logger.debug(response.json())  # 返回错误信息
async def get_version_compatible():
    pyproject_path = pathlib.Path(__file__).parent.parent.parent / "pyproject.toml"
    # 根据 Python 版本选择解析器
    if sys.version_info >= (3, 11):
        import tomllib
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
    else:
        with pyproject_path.open("rb") as f:
            data = tomli.load(f)
    
    # 检查所有可能的版本位置
    version_paths = [
        ["project", "version"],
    ]
    for path in version_paths:
        current = data
        try:
            for key in path:
                current = current[key]
            return current
        except (KeyError, TypeError):
            continue
    
    raise ValueError("版本号未在 pyproject.toml 中找到")

async def check_update():
    latest = await get_latest_release("AxT-Team", "AxTBot")
    if latest:
        logger.debug(f"版本检查 >>> 最新版本: {latest['tag']} ({latest['name']})")
        logger.debug(f"版本检查 >>> 发布时间: {latest['published_at']}")
        url = latest['url'].replace('%2b', '+')
        logger.debug(f"版本检查 >>> 发布页面: {url}")
    else:
        logger.error("版本检查 >>> 获取最新版本失败")
        return
    now = await get_version_compatible()
    if latest["tag"].replace("v", "") > now.replace("v", "") or latest["tag"][6:] > now[6:]:  # 比对版本号
        logger.warning(f"版本检查 >>> 检测到新版本: {latest['tag']} ({latest['name']}) | 当前版本: {now}")
        url = latest['url'].replace('%2b', '+')
        logger.warning(f"版本检查 >>> 请前往更新: {url}")
    else:
        logger.info(f"版本检查 >>> 当前版本已是最新: {now}")