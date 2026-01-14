"""Crawl command: /crawl <url> [--instructions <text>] [--max_breadth <int>]"""

from urllib.parse import urlparse

from nonebot import logger
from arclet.alconna import Alconna, Args, Option, CommandMeta, Arparma, MultiVar
from nonebot_plugin_alconna import on_alconna, Match, Query

from ..client import tavily_client
from ..config import config

crawl_cmd = Alconna(
    "crawl",
    Args["url", str],
    Option("--instructions", Args["instr", MultiVar(str, "+")]),  # Support multi-word
    Option("--max_breadth", Args["breadth", int], default=config.tavily_max_breadth),
    meta=CommandMeta(description="按指令抓取网站数据"),
)

crawl_matcher = on_alconna(crawl_cmd, priority=5, block=True, use_cmd_start=True)

logger.debug(f"[Tavily] Crawl command registered: {crawl_cmd.path}")


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


@crawl_matcher.handle()
async def handle_crawl(
    result: Arparma,
    url: Match[str],
    instr: Query[tuple[str, ...]] = Query("instructions.instr", ()),
    breadth: Query[int] = Query("max_breadth.breadth", config.tavily_max_breadth),
) -> None:
    """Handle crawl command."""
    if not url.available:
        logger.warning("[Tavily] Crawl: url not available")
        await crawl_matcher.finish("请提供 URL")

    target_url = url.result
    # Join tuple of words for instructions
    instructions = " ".join(instr.result) if instr.available and instr.result else ""
    max_breadth = breadth.result if breadth.available else config.tavily_max_breadth

    logger.debug(
        f"[Tavily] Crawl triggered: url={target_url!r}, instructions={instructions!r}, max_breadth={max_breadth}"
    )

    # Validate URL
    if not is_valid_url(target_url):
        logger.warning(f"[Tavily] Invalid URL: {target_url}")
        await crawl_matcher.finish(
            "无效的 URL，请提供以 http:// 或 https:// 开头的网址"
        )

    response = await tavily_client.crawl(
        url=target_url,
        instructions=instructions,
        max_breadth=max_breadth,
    )
    logger.debug(f"[Tavily] Crawl response: {len(response.get('results', []))} results")

    if error := response.get("error"):
        logger.warning(f"[Tavily] Crawl error: {error}")
        await crawl_matcher.finish(f"抓取出错: {error}")

    results = response.get("results", [])
    if not results:
        await crawl_matcher.finish("未抓取到数据")

    # Format output: list crawled pages with URLs
    truncate = config.tavily_crawl_truncate
    lines = [f"共抓取 {len(results)} 个页面:"]
    for i, r in enumerate(results[:10], 1):
        page_url = r.get("url", "")
        content = r.get("raw_content", "")[:truncate]
        lines.append(f"\n{i}. {page_url}\n   {content}...")

    if len(results) > 10:
        lines.append(f"\n...(还有 {len(results) - 10} 个页面)")

    await crawl_matcher.finish("\n".join(lines))
