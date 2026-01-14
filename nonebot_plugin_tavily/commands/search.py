"""Search command: /search <query> [--depth basic|advanced]"""

from nonebot import logger, Bot
from nonebot.adapters import Event
from arclet.alconna import Alconna, Args, Option, CommandMeta, Arparma, MultiVar
from nonebot_plugin_alconna import on_alconna, Match, Query

from ..client import tavily_client
from ..config import config

search_cmd = Alconna(
    "search",
    Args["query", MultiVar(str, "+")],  # Support multi-word queries
    Option("--depth", Args["depth_val", str], default=config.tavily_default_depth),
    meta=CommandMeta(description="联网搜索，返回实时结果"),
)

search_matcher = on_alconna(search_cmd, priority=5, block=True, use_cmd_start=True)

logger.debug(f"[Tavily] Search command registered: {search_cmd.path}")


@search_matcher.handle()
async def handle_search(
    bot: Bot,
    event: Event,
    result: Arparma,
    query: Match[tuple[str, ...]],
    depth_val: Query[str] = Query("depth.depth_val", config.tavily_default_depth),
) -> None:
    """Handle search command."""
    # Debug logging for event content vs parsed query
    raw_msg = event.get_plaintext()
    logger.debug(f"[Tavily] Search Handler - Raw Event Message: {raw_msg!r}")

    if not query.available:
        logger.warning("[Tavily] Search: query not available")
        await search_matcher.finish("请提供搜索关键词")

    q = " ".join(query.result)  # Join multiple words
    depth = depth_val.result if depth_val.available else config.tavily_default_depth

    logger.debug(
        f"[Tavily] Search triggered: parsed_query={q!r}, depth={depth}, simple={config.tavily_simple_mode}"
    )

    response = await tavily_client.search(query=q, search_depth=depth)
    logger.debug(
        f"[Tavily] Search response: {len(response.get('results', []))} results"
    )

    if error := response.get("error"):
        logger.warning(f"[Tavily] Search error: {error}")
        await search_matcher.finish(f"搜索出错: {error}")

    results = response.get("results", [])
    if not results:
        await search_matcher.finish("无结果")

    truncate = config.tavily_search_truncate

    if config.tavily_simple_mode:
        # Simple mode: content only
        lines = [r.get("content", "")[:truncate] for r in results if r.get("content")]
        await search_matcher.finish("\n\n".join(lines))
    else:
        # Full mode: title, content, URL
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "无标题")
            content = r.get("content", "")[:truncate]
            url = r.get("url", "")
            lines.append(f"{i}. **{title}**\n   {content}...\n   {url}")
        await search_matcher.finish("\n\n".join(lines))
