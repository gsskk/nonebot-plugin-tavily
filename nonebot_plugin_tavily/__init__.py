"""NoneBot plugin for Tavily Search API."""

from nonebot import require, logger
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

# 确保依赖的插件已加载 - 必须在导入 commands 模块之前！
require("nonebot_plugin_alconna")

from .commands import crawl, extract, search
from .config import Config

__version__ = "0.1.0"

__plugin_meta__ = PluginMetadata(
    name="Tavily Search",
    description="基于 Tavily API 的 NoneBot2 插件，提供联网搜索、内容提取和智能抓取功能",
    usage=(
        "/search <query> [--depth basic|advanced] - 联网搜索\n"
        "/extract <url> - 提取网页内容\n"
        "/crawl <url> [--instructions <text>] [--max_breadth <int>] - 智能抓取"
    ),
    type="application",
    homepage="https://github.com/gsskk/nonebot-plugin-tavily",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

logger.info(f"[Tavily] Plugin loaded: v{__version__}")

# Re-export for convenience
__all__ = ["__version__", "__plugin_meta__", "search", "extract", "crawl"]
