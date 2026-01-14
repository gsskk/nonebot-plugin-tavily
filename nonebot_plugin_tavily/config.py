"""Plugin configuration."""

from pydantic import BaseModel
from nonebot import get_plugin_config


class Config(BaseModel):
    """Tavily plugin configuration.

    Attributes:
        tavily_api_key: Tavily API key (required).
        tavily_default_depth: Default search depth ("basic" or "advanced").
        tavily_max_breadth: Default max breadth for crawl.
        tavily_simple_mode: Simple output mode (content only, no title/URL).
        tavily_max_results: Max number of search results to return.
        tavily_time_range: Default time range for search (day/week/month/year or empty).
        tavily_search_truncate: Truncate length for search content snippets.
        tavily_extract_truncate: Truncate length for extract content.
        tavily_crawl_truncate: Truncate length for crawl content snippets.
    """

    tavily_api_key: str = ""
    tavily_default_depth: str = "basic"
    tavily_max_breadth: int = 10
    tavily_simple_mode: bool = False
    tavily_max_results: int = 5
    tavily_time_range: str = "day"
    tavily_search_truncate: int = 200
    tavily_extract_truncate: int = 2000
    tavily_crawl_truncate: int = 150


config = get_plugin_config(Config)
