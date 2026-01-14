"""Tavily API async client wrapper."""

from nonebot import logger
from tavily import AsyncTavilyClient

from .config import config


class TavilyClientWrapper:
    """Async wrapper for Tavily API using AsyncTavilyClient."""

    def __init__(self) -> None:
        self.api_key = config.tavily_api_key
        self._client: AsyncTavilyClient | None = None
        if self.api_key:
            self._client = AsyncTavilyClient(api_key=self.api_key)
            logger.info("[Tavily] Client initialized with API key")
        else:
            logger.warning("[Tavily] No API key configured, client disabled")

    @property
    def client(self) -> AsyncTavilyClient | None:
        """Lazy client accessor."""
        return self._client

    async def search(
        self,
        query: str,
        search_depth: str | None = None,
        max_results: int | None = None,
        time_range: str | None = None,
        **kwargs,
    ) -> dict:
        """
        Perform a web search.

        Args:
            query: Search query string.
            search_depth: "basic" or "advanced". Defaults to config value.
            max_results: Maximum number of results. Defaults to config value.
            time_range: Time range filter (day/week/month/year). Defaults to config value.
            **kwargs: Additional parameters passed to Tavily API.

        Returns:
            Search results dict with 'results' key.
        """
        if not self._client:
            return {"results": [], "error": "Tavily API key not configured"}

        depth = search_depth or config.tavily_default_depth
        results_count = (
            max_results if max_results is not None else config.tavily_max_results
        )
        range_val = time_range if time_range is not None else config.tavily_time_range
        logger.debug(
            f"[Tavily] API search: query={query!r}, depth={depth}, max_results={results_count}, time_range={range_val or 'none'}"
        )

        # Build search params
        search_kwargs = {
            "query": query,
            "search_depth": depth,
            "max_results": results_count,
            **kwargs,
        }
        if range_val:
            search_kwargs["time_range"] = range_val

        try:
            result = await self._client.search(**search_kwargs)
            logger.debug(
                f"[Tavily] API search success: {len(result.get('results', []))} results"
            )
            return result
        except Exception as e:
            logger.error(f"[Tavily] API search failed: {e}")
            return {"results": [], "error": str(e)}

    async def extract(
        self, urls: list[str], extract_depth: str | None = None, **kwargs
    ) -> dict:
        """
        Extract content from URLs.

        Args:
            urls: List of URLs to extract content from.
            extract_depth: "basic" or "advanced". Defaults to config value.
            **kwargs: Additional parameters (include_images, etc.)

        Returns:
            Extraction results dict with 'results' and 'failed_results' keys.
        """
        if not self._client:
            return {"results": [], "error": "Tavily API key not configured"}

        depth = extract_depth or config.tavily_default_depth
        logger.debug(f"[Tavily] API extract: urls={urls}, extract_depth={depth}")

        try:
            result = await self._client.extract(
                urls=urls, extract_depth=depth, **kwargs
            )
            logger.debug(
                f"[Tavily] API extract success: {len(result.get('results', []))} results"
            )
            return result
        except Exception as e:
            logger.error(f"[Tavily] API extract failed: {e}")
            return {"results": [], "error": str(e)}

    async def crawl(
        self,
        url: str,
        instructions: str = "",
        max_breadth: int | None = None,
        max_depth: int = 1,
        limit: int = 50,
        **kwargs,
    ) -> dict:
        """
        Crawl a website starting from the given URL.

        Args:
            url: Starting URL for the crawl.
            instructions: Natural language instructions to guide the crawl.
            max_breadth: Maximum number of links to follow at each level.
                         Defaults to config value.
            max_depth: Maximum depth of the crawl (default 1).
            limit: Maximum total pages to crawl (default 50).
            **kwargs: Additional parameters (extract_depth, format, etc.)

        Returns:
            Crawl results dict with 'base_url' and 'results' keys.
        """
        if not self._client:
            return {"results": [], "error": "Tavily API key not configured"}

        breadth = max_breadth if max_breadth is not None else config.tavily_max_breadth
        logger.debug(
            f"[Tavily] API crawl: url={url!r}, instructions={instructions!r}, max_breadth={breadth}"
        )

        try:
            result = await self._client.crawl(
                url=url,
                instructions=instructions or None,
                max_breadth=breadth,
                max_depth=max_depth,
                limit=limit,
                **kwargs,
            )
            logger.debug(
                f"[Tavily] API crawl success: {len(result.get('results', []))} results"
            )
            return result
        except Exception as e:
            logger.error(f"[Tavily] API crawl failed: {e}")
            return {"results": [], "error": str(e)}


# Global client instance
tavily_client = TavilyClientWrapper()
