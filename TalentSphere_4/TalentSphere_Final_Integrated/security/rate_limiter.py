"""Rate Limiter module enforcing per-user rate limits using a sliding window algorithm over Django cache."""
import time
from django.conf import settings
from django.core.cache import cache


def get_client_ip(request):
    """Extract client IP address from request headers or remote address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    return ip


def get_user_identifier(request):
    """Determine a unique rate-limiting key for the request.

    Prioritizes:
    1. JWT authenticated user ID
    2. Django session authenticated user ID
    3. Client IP address
    """
    jwt_user = getattr(request, "jwt_user", None)
    if jwt_user and getattr(jwt_user, "is_authenticated", True):
        return f"user:{jwt_user.id}"

    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return f"user:{user.id}"

    return f"ip:{get_client_ip(request)}"


class RateLimiter:
    """Thread-safe sliding window rate limiter."""

    @classmethod
    def check_rate_limit(cls, request, limit=None, window=1):
        """Check if request from user/IP exceeds rate limit.

        :param request: HttpRequest object
        :param limit: Max allowed requests per window (default from settings or 10)
        :param window: Time window in seconds (default 1)
        :return: tuple (is_allowed, current_count, retry_after, remaining, limit)
        """
        if limit is None:
            limit = getattr(settings, "RATE_LIMIT_PER_SECOND", 10)

        identifier = get_user_identifier(request)
        now = time.time()

        current_sec = int(now // window)
        sub_sec = (now % window) / window

        key_current = f"rate_limit:{identifier}:{current_sec}"
        key_prev = f"rate_limit:{identifier}:{current_sec - 1}"

        count_prev = cache.get(key_prev, 0)
        count_current = cache.get(key_current, 0)

        estimated_rate = count_prev * (1.0 - sub_sec) + count_current

        if estimated_rate >= limit:
            retry_after = max(1, int(window - (now % window) + 0.99))
            remaining = 0
            return False, int(estimated_rate), retry_after, remaining, limit

        # Increment count for current window
        try:
            cache.add(key_current, 0, timeout=window * 10)
            new_count = cache.incr(key_current)
        except Exception:
            new_count = count_current + 1
            cache.set(key_current, new_count, timeout=window * 10)

        remaining = max(0, limit - new_count)
        return True, new_count, 0, remaining, limit
