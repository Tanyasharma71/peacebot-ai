"""
Response Caching System for Peacebot
Provides intelligent caching for OpenAI API responses to reduce costs and improve performance.
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any
from functools import wraps
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger_config import get_logger

logger = get_logger(__name__)


class CacheBackend:
    """Base class for cache backends."""
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value from cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store value in cache with TTL."""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError


class InMemoryCache(CacheBackend):
    """Simple in-memory cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize in-memory cache.
        
        Args:
            max_size: Maximum number of entries to store
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        logger.info(f"InMemoryCache initialized with max_size={max_size}")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value from cache if not expired."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if entry['expires_at'] < time.time():
            del self._cache[key]
            logger.debug(f"Cache entry expired: {key}")
            return None
        
        logger.debug(f"Cache hit: {key}")
        return entry['value']
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store value in cache with TTL."""
        try:
            # Implement LRU eviction if cache is full
            if len(self._cache) >= self._max_size:
                # Remove oldest entry
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k]['created_at'])
                del self._cache[oldest_key]
                logger.debug(f"Cache full, evicted: {oldest_key}")
            
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + ttl
            }
            logger.debug(f"Cache set: {key} (TTL={ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'utilization': len(self._cache) / self._max_size * 100
        }


class RedisCache(CacheBackend):
    """Redis-based cache implementation."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 prefix: str = 'peacebot:'):
        """
        Initialize Redis cache.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            prefix: Key prefix for namespacing
        """
        try:
            import redis
            self._redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self._prefix = prefix
            # Test connection
            self._redis.ping()
            logger.info(f"RedisCache initialized: {host}:{port}/{db}")
        except ImportError:
            logger.error("Redis library not installed. Install with: pip install redis")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self._prefix}{key}"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve value from Redis cache."""
        try:
            full_key = self._make_key(key)
            value = self._redis.get(full_key)
            
            if value is None:
                return None
            
            logger.debug(f"Redis cache hit: {key}")
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store value in Redis cache with TTL."""
        try:
            full_key = self._make_key(key)
            serialized = json.dumps(value)
            self._redis.setex(full_key, ttl, serialized)
            logger.debug(f"Redis cache set: {key} (TTL={ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            full_key = self._make_key(key)
            result = self._redis.delete(full_key)
            logger.debug(f"Redis cache deleted: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries with prefix."""
        try:
            pattern = f"{self._prefix}*"
            keys = self._redis.keys(pattern)
            if keys:
                self._redis.delete(*keys)
                logger.info(f"Redis cache cleared: {len(keys)} entries removed")
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            full_key = self._make_key(key)
            return self._redis.exists(full_key) > 0
        except Exception as e:
            logger.error(f"Error checking Redis key existence: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            info = self._redis.info('memory')
            pattern = f"{self._prefix}*"
            key_count = len(self._redis.keys(pattern))
            
            return {
                'keys': key_count,
                'memory_used': info.get('used_memory_human', 'N/A'),
                'connected': True
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {'connected': False, 'error': str(e)}


class ResponseCache:
    """
    High-level response caching system for Peacebot.
    Automatically caches OpenAI API responses to reduce costs and latency.
    """
    
    def __init__(self, backend: Optional[CacheBackend] = None,
                 default_ttl: int = 3600,
                 enable_cache: bool = True):
        """
        Initialize response cache.
        
        Args:
            backend: Cache backend (InMemoryCache or RedisCache)
            default_ttl: Default time-to-live in seconds (1 hour)
            enable_cache: Enable/disable caching globally
        """
        self._backend = backend or InMemoryCache()
        self._default_ttl = default_ttl
        self._enable_cache = enable_cache
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0
        }
        logger.info(f"ResponseCache initialized (enabled={enable_cache}, ttl={default_ttl}s)")
    
    def _generate_cache_key(self, prompt: str, model: str = "default",
                           temperature: float = 0.7) -> str:
        """
        Generate cache key from prompt and parameters.
        
        Args:
            prompt: User prompt
            model: Model name
            temperature: Temperature parameter
            
        Returns:
            Cache key (SHA256 hash)
        """
        # Normalize prompt (lowercase, strip whitespace)
        normalized_prompt = prompt.lower().strip()
        
        # Create cache key from prompt + parameters
        key_data = f"{normalized_prompt}:{model}:{temperature}"
        cache_key = hashlib.sha256(key_data.encode()).hexdigest()
        
        return cache_key
    
    def get_cached_response(self, prompt: str, model: str = "default",
                           temperature: float = 0.7) -> Optional[str]:
        """
        Get cached response for prompt.
        
        Args:
            prompt: User prompt
            model: Model name
            temperature: Temperature parameter
            
        Returns:
            Cached response or None
        """
        if not self._enable_cache:
            return None
        
        try:
            cache_key = self._generate_cache_key(prompt, model, temperature)
            cached_data = self._backend.get(cache_key)
            
            if cached_data:
                self._stats['hits'] += 1
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cached_data.get('response')
            
            self._stats['misses'] += 1
            logger.debug(f"Cache miss for prompt: {prompt[:50]}...")
            return None
            
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Error getting cached response: {e}")
            return None
    
    def cache_response(self, prompt: str, response: str,
                      model: str = "default", temperature: float = 0.7,
                      ttl: Optional[int] = None) -> bool:
        """
        Cache response for prompt.
        
        Args:
            prompt: User prompt
            response: Bot response
            model: Model name
            temperature: Temperature parameter
            ttl: Time-to-live (uses default if None)
            
        Returns:
            True if cached successfully
        """
        if not self._enable_cache:
            return False
        
        try:
            cache_key = self._generate_cache_key(prompt, model, temperature)
            cache_data = {
                'response': response,
                'prompt': prompt[:100],  # Store truncated prompt for debugging
                'model': model,
                'temperature': temperature,
                'cached_at': time.time()
            }
            
            ttl = ttl or self._default_ttl
            success = self._backend.set(cache_key, cache_data, ttl)
            
            if success:
                self._stats['sets'] += 1
                logger.debug(f"Cached response for prompt: {prompt[:50]}...")
            
            return success
            
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"Error caching response: {e}")
            return False
    
    def invalidate(self, prompt: str, model: str = "default",
                  temperature: float = 0.7) -> bool:
        """
        Invalidate cached response for prompt.
        
        Args:
            prompt: User prompt
            model: Model name
            temperature: Temperature parameter
            
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = self._generate_cache_key(prompt, model, temperature)
            return self._backend.delete(cache_key)
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cached responses."""
        try:
            return self._backend.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        backend_stats = {}
        try:
            backend_stats = self._backend.get_stats()
        except Exception as e:
            logger.error(f"Error getting backend stats: {e}")
        
        return {
            'enabled': self._enable_cache,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'errors': self._stats['errors'],
            'hit_rate': f"{hit_rate:.2f}%",
            'backend': backend_stats
        }


def cached_response(ttl: int = 3600, cache_instance: Optional[ResponseCache] = None):
    """
    Decorator to cache function responses.
    
    Args:
        ttl: Time-to-live in seconds
        cache_instance: ResponseCache instance (creates new if None)
        
    Example:
        @cached_response(ttl=1800)
        def generate_response(prompt: str) -> str:
            # Expensive API call
            return response
    """
    _cache = cache_instance or ResponseCache()
    
    def decorator(func):
        @wraps(func)
        def wrapper(prompt: str, *args, **kwargs):
            # Try to get from cache
            cached = _cache.get_cached_response(prompt)
            if cached is not None:
                return cached
            
            # Generate new response
            response = func(prompt, *args, **kwargs)
            
            # Cache the response
            if response:
                _cache.cache_response(prompt, response, ttl=ttl)
            
            return response
        
        return wrapper
    return decorator


# Global cache instance
_global_cache: Optional[ResponseCache] = None


def get_cache(backend: str = 'memory', **kwargs) -> ResponseCache:
    """
    Get or create global cache instance.
    
    Args:
        backend: 'memory' or 'redis'
        **kwargs: Backend-specific arguments
        
    Returns:
        ResponseCache instance
    """
    global _global_cache
    
    if _global_cache is None:
        if backend == 'redis':
            try:
                cache_backend = RedisCache(**kwargs)
                logger.info("Using Redis cache backend")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis, falling back to memory: {e}")
                cache_backend = InMemoryCache()
        else:
            cache_backend = InMemoryCache(**kwargs)
            logger.info("Using in-memory cache backend")
        
        _global_cache = ResponseCache(backend=cache_backend)
    
    return _global_cache
