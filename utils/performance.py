"""
Performance Monitoring and Metrics for Peacebot
Tracks response times, API calls, and system health.
"""

import time
import functools
from typing import Dict, Any, Optional, Callable, List
from collections import defaultdict, deque
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger_config import get_logger

logger = get_logger(__name__)


class PerformanceMetrics:
    """
    Tracks and aggregates performance metrics.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize performance metrics tracker.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        
        # Response time tracking
        self._response_times: deque = deque(maxlen=max_history)
        self._endpoint_times: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        
        # Request counting
        self._request_counts: Dict[str, int] = defaultdict(int)
        self._error_counts: Dict[str, int] = defaultdict(int)
        
        # API call tracking
        self._api_calls: Dict[str, int] = defaultdict(int)
        self._api_latencies: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        
        # Cache metrics
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Start time
        self._start_time = time.time()
        
        logger.info(f"PerformanceMetrics initialized (max_history={max_history})")
    
    def record_response_time(self, endpoint: str, duration: float) -> None:
        """
        Record response time for an endpoint.
        
        Args:
            endpoint: Endpoint name
            duration: Response time in seconds
        """
        self._response_times.append(duration)
        self._endpoint_times[endpoint].append(duration)
        self._request_counts[endpoint] += 1
        
        # Log slow requests
        if duration > 5.0:
            logger.warning(f"Slow request detected: {endpoint} took {duration:.2f}s")
    
    def record_error(self, endpoint: str) -> None:
        """
        Record an error for an endpoint.
        
        Args:
            endpoint: Endpoint name
        """
        self._error_counts[endpoint] += 1
    
    def record_api_call(self, api_name: str, duration: float) -> None:
        """
        Record API call latency.
        
        Args:
            api_name: API name (e.g., 'openai')
            duration: API call duration in seconds
        """
        self._api_calls[api_name] += 1
        self._api_latencies[api_name].append(duration)
        
        # Log slow API calls
        if duration > 10.0:
            logger.warning(f"Slow API call: {api_name} took {duration:.2f}s")
    
    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self._cache_hits += 1
    
    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self._cache_misses += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.
        
        Returns:
            Dictionary with performance stats
        """
        uptime = time.time() - self._start_time
        
        # Calculate overall response time stats
        overall_stats = self._calculate_stats(list(self._response_times))
        
        # Calculate per-endpoint stats
        endpoint_stats = {}
        for endpoint, times in self._endpoint_times.items():
            endpoint_stats[endpoint] = {
                **self._calculate_stats(list(times)),
                'requests': self._request_counts[endpoint],
                'errors': self._error_counts[endpoint],
                'error_rate': (self._error_counts[endpoint] / 
                             self._request_counts[endpoint] * 100
                             if self._request_counts[endpoint] > 0 else 0)
            }
        
        # Calculate API stats
        api_stats = {}
        for api_name, latencies in self._api_latencies.items():
            api_stats[api_name] = {
                **self._calculate_stats(list(latencies)),
                'calls': self._api_calls[api_name]
            }
        
        # Calculate cache stats
        total_cache_requests = self._cache_hits + self._cache_misses
        cache_hit_rate = (self._cache_hits / total_cache_requests * 100
                         if total_cache_requests > 0 else 0)
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_duration(uptime),
            'overall': overall_stats,
            'endpoints': endpoint_stats,
            'apis': api_stats,
            'cache': {
                'hits': self._cache_hits,
                'misses': self._cache_misses,
                'hit_rate': f"{cache_hit_rate:.2f}%"
            },
            'total_requests': sum(self._request_counts.values()),
            'total_errors': sum(self._error_counts.values())
        }
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, Any]:
        """
        Calculate statistics for a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Dictionary with min, max, avg, p50, p95, p99
        """
        if not values:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'avg': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            'count': count,
            'min': f"{min(sorted_values):.3f}s",
            'max': f"{max(sorted_values):.3f}s",
            'avg': f"{sum(sorted_values) / count:.3f}s",
            'p50': f"{sorted_values[int(count * 0.50)]:.3f}s",
            'p95': f"{sorted_values[int(count * 0.95)]:.3f}s",
            'p99': f"{sorted_values[int(count * 0.99)]:.3f}s"
        }
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.1f}m"
        elif seconds < 86400:
            return f"{seconds / 3600:.1f}h"
        else:
            return f"{seconds / 86400:.1f}d"
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._response_times.clear()
        self._endpoint_times.clear()
        self._request_counts.clear()
        self._error_counts.clear()
        self._api_calls.clear()
        self._api_latencies.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._start_time = time.time()
        logger.info("Performance metrics reset")


def measure_time(func: Optional[Callable] = None, *,
                endpoint_name: Optional[str] = None,
                metrics: Optional[PerformanceMetrics] = None):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to decorate
        endpoint_name: Custom endpoint name (uses function name if None)
        metrics: PerformanceMetrics instance
        
    Example:
        @measure_time
        def my_function():
            pass
        
        @measure_time(endpoint_name='custom_endpoint')
        def another_function():
            pass
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error_occurred = False
            
            try:
                result = f(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                raise
            finally:
                duration = time.time() - start_time
                name = endpoint_name or f.__name__
                
                if metrics:
                    metrics.record_response_time(name, duration)
                    if error_occurred:
                        metrics.record_error(name)
                
                logger.debug(f"{name} completed in {duration:.3f}s")
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


def measure_api_call(api_name: str, metrics: Optional[PerformanceMetrics] = None):
    """
    Decorator to measure API call latency.
    
    Args:
        api_name: Name of the API
        metrics: PerformanceMetrics instance
        
    Example:
        @measure_api_call('openai')
        def call_openai_api():
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                
                if metrics:
                    metrics.record_api_call(api_name, duration)
                
                logger.debug(f"{api_name} API call completed in {duration:.3f}s")
        
        return wrapper
    return decorator


class HealthChecker:
    """
    System health checker.
    """
    
    def __init__(self):
        """Initialize health checker."""
        self._checks: Dict[str, Callable] = {}
        logger.info("HealthChecker initialized")
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """
        Register a health check function.
        
        Args:
            name: Check name
            check_func: Function that returns (bool, str) - (healthy, message)
        """
        self._checks[name] = check_func
        logger.debug(f"Health check registered: {name}")
    
    def run_checks(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Dictionary with health check results
        """
        results = {}
        all_healthy = True
        
        for name, check_func in self._checks.items():
            try:
                healthy, message = check_func()
                results[name] = {
                    'healthy': healthy,
                    'message': message
                }
                if not healthy:
                    all_healthy = False
            except Exception as e:
                logger.error(f"Health check failed: {name} - {str(e)}")
                results[name] = {
                    'healthy': False,
                    'message': f"Check failed: {str(e)}"
                }
                all_healthy = False
        
        return {
            'healthy': all_healthy,
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }


class AlertManager:
    """
    Simple alert manager for performance issues.
    """
    
    def __init__(self, 
                 slow_request_threshold: float = 5.0,
                 error_rate_threshold: float = 10.0):
        """
        Initialize alert manager.
        
        Args:
            slow_request_threshold: Threshold for slow requests (seconds)
            error_rate_threshold: Threshold for error rate (percentage)
        """
        self.slow_request_threshold = slow_request_threshold
        self.error_rate_threshold = error_rate_threshold
        self._alerts: deque = deque(maxlen=100)
        logger.info(f"AlertManager initialized "
                   f"(slow_threshold={slow_request_threshold}s, "
                   f"error_threshold={error_rate_threshold}%)")
    
    def check_performance(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """
        Check performance metrics and generate alerts.
        
        Args:
            metrics: PerformanceMetrics instance
            
        Returns:
            List of alerts
        """
        alerts = []
        stats = metrics.get_stats()
        
        # Check for slow endpoints
        for endpoint, endpoint_stats in stats['endpoints'].items():
            if endpoint_stats['count'] > 0:
                avg_time = float(endpoint_stats['avg'].rstrip('s'))
                
                if avg_time > self.slow_request_threshold:
                    alert = {
                        'type': 'slow_endpoint',
                        'severity': 'warning',
                        'endpoint': endpoint,
                        'avg_time': avg_time,
                        'threshold': self.slow_request_threshold,
                        'timestamp': datetime.now().isoformat()
                    }
                    alerts.append(alert)
                    self._alerts.append(alert)
                    logger.warning(f"Slow endpoint alert: {endpoint} "
                                 f"avg={avg_time:.2f}s")
        
        # Check for high error rates
        for endpoint, endpoint_stats in stats['endpoints'].items():
            error_rate = endpoint_stats['error_rate']
            
            if error_rate > self.error_rate_threshold:
                alert = {
                    'type': 'high_error_rate',
                    'severity': 'critical',
                    'endpoint': endpoint,
                    'error_rate': error_rate,
                    'threshold': self.error_rate_threshold,
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)
                self._alerts.append(alert)
                logger.error(f"High error rate alert: {endpoint} "
                           f"rate={error_rate:.2f}%")
        
        return alerts
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return list(self._alerts)[-limit:]


# Global instances
_global_metrics: Optional[PerformanceMetrics] = None
_global_health_checker: Optional[HealthChecker] = None
_global_alert_manager: Optional[AlertManager] = None


def get_metrics() -> PerformanceMetrics:
    """Get or create global metrics instance."""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = PerformanceMetrics()
    return _global_metrics


def get_health_checker() -> HealthChecker:
    """Get or create global health checker instance."""
    global _global_health_checker
    if _global_health_checker is None:
        _global_health_checker = HealthChecker()
    return _global_health_checker


def get_alert_manager() -> AlertManager:
    """Get or create global alert manager instance."""
    global _global_alert_manager
    if _global_alert_manager is None:
        _global_alert_manager = AlertManager()
    return _global_alert_manager
