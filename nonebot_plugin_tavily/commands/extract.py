"""Extract command: /extract <url> [--depth basic|advanced]"""

from urllib.parse import urlparse

from nonebot import logger
from arclet.alconna import Alconna, Args, Option, CommandMeta, Arparma
from nonebot_plugin_alconna import on_alconna, Match, Query

from ..client import tavily_client
from ..config import config

extract_cmd = Alconna(
    "extract",
    Args["url", str],
    Option("--depth", Args["depth_val", str], default=config.tavily_default_depth),
    meta=CommandMeta(description="提取并总结网页内容"),
)

extract_matcher = on_alconna(extract_cmd, priority=5, block=True, use_cmd_start=True)

logger.debug(f"[Tavily] Extract command registered: {extract_cmd.path}")


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


@extract_matcher.handle()
async def handle_extract(
    result: Arparma,
    url: Match[str],
    depth_val: Query[str] = Query("depth.depth_val", config.tavily_default_depth),
) -> None:
    """Handle extract command."""
    if not url.available:
        logger.warning("[Tavily] Extract: url not available")
        await extract_matcher.finish("请提供 URL")

    target_url = url.result
    depth = depth_val.result if depth_val.available else config.tavily_default_depth
    logger.debug(f"[Tavily] Extract triggered: url={target_url!r}, depth={depth}")

    # Validate URL
    if not is_valid_url(target_url):
        logger.warning(f"[Tavily] Invalid URL: {target_url}")
        await extract_matcher.finish(
            "无效的 URL，请提供以 http:// 或 https:// 开头的网址"
        )

    response = await tavily_client.extract(urls=[target_url], extract_depth=depth)
    logger.debug(
        f"[Tavily] Extract response: {len(response.get('results', []))} results"
    )

    if error := response.get("error"):
        logger.warning(f"[Tavily] Extract error: {error}")
        await extract_matcher.finish(f"提取出错: {error}")

    # Check for failed results
    failed = response.get("failed_results", [])
    if failed:
        error_msg = failed[0].get("error", "未知错误")
        logger.warning(f"[Tavily] Extract failed: {error_msg}")
        await extract_matcher.finish(f"无法提取内容: {error_msg}")

    results = response.get("results", [])
    if not results:
        await extract_matcher.finish("无法提取内容")

    content = results[0].get("raw_content", "")
    if not content:
        await extract_matcher.finish("内容为空")

    # Truncate if too long
    truncate = config.tavily_extract_truncate
    if len(content) > truncate:
        content = content[:truncate] + "\n\n...(内容已截断)"

    await extract_matcher.finish(content)
