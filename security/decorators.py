from functools import wraps
from django.http import JsonResponse, HttpResponse
from .rate_limiter import RateLimiter


def jwt_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, "jwt_user", None):
            return JsonResponse({"error": "Authentication required."}, status=401)
        return view(request, *args, **kwargs)

    return wrapper


def rate_limit(limit=10, window=1):
    """Decorator to enforce custom rate limit on specific view functions."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            is_allowed, count, retry_after, remaining, max_limit = RateLimiter.check_rate_limit(
                request, limit=limit, window=window
            )
            if not is_allowed:
                is_json = request.headers.get("Accept") == "application/json" or request.path_info.startswith("/api/")
                if is_json:
                    resp = JsonResponse(
                        {
                            "error": f"Request rate limit exceeded. Maximum {max_limit} requests per second allowed.",
                            "retry_after": retry_after,
                        },
                        status=429,
                    )
                else:
                    resp = HttpResponse(
                        f"429 Too Many Requests: Rate limit exceeded. Retry after {retry_after}s.",
                        status=429,
                        content_type="text/plain",
                    )
                resp["Retry-After"] = str(retry_after)
                resp["X-RateLimit-Limit"] = str(max_limit)
                resp["X-RateLimit-Remaining"] = "0"
                resp["X-RateLimit-Reset"] = str(retry_after)
                return resp

            response = view_func(request, *args, **kwargs)
            response["X-RateLimit-Limit"] = str(max_limit)
            response["X-RateLimit-Remaining"] = str(remaining)
            return response

        return _wrapped_view

    return decorator
