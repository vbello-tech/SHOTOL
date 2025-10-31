from django.core.cache import cache
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class URLCacheService:
    """Service for caching URL shortener data."""

    # Cache key patterns
    URL_KEY = 'url:{slug}'

    @classmethod
    def get_url(cls, slug):
        """
        Get URL data from cache.

        Args:
            slug (str): Short URL slug

        Returns:
            dict or None: URL data if found
        """
        try:
            cache_key = cls.URL_KEY.format(slug=slug)
            data = cache.get(cache_key)

            if data:
                logger.info(f"Cache HIT for {slug}")
            else:
                logger.debug(f"Cache MISS for {slug}")

            return data
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    @classmethod
    def set_url(cls, slug, url_data, timeout=None):
        """
        Cache URL data.

        Args:
            slug (str): Short URL slug
            url_data (dict): URL data to cache
            timeout (int): Cache timeout in seconds
        """
        try:
            cache_key = cls.URL_KEY.format(slug=slug)
            timeout = timeout or settings.CACHE_TTL.get('url_lookup', 86400)

            cache.set(cache_key, url_data, timeout)
            logger.debug(f"Cached URL: {slug}")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    @classmethod
    def delete_url(cls, slug):
        """
        Remove URL from cache.

        Args:
            slug (str): Short URL slug
        """
        try:
            cache_key = cls.URL_KEY.format(slug=slug)
            cache.delete(cache_key)
            logger.debug(f"Deleted from cache: {slug}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
