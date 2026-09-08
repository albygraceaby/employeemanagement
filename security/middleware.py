"""Security middleware: JWT authentication for API requests, restrictive CORS, and Rate Limiting."""
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from .jwt import decode_token
from .rate_limiter import RateLimiter


class JWTAuthenticationMiddleware:
    """Populate request.jwt_user from a valid Bearer access token.

    Session authentication remains available for the existing web UI. API views
    can use the jwt_required decorator to require the Bearer token explicitly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.jwt_user = None
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            request.jwt_user = decode_token(auth[7:].strip(), expected_type="access")
        return self.get_response(request)


class CORSSecurityMiddleware:
    """Allow only configured origins and handle CORS preflight safely."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        allowed = origin in getattr(settings, "CORS_ALLOWED_ORIGINS", set())

        if request.method == "OPTIONS" and origin and allowed:
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if origin and allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-CSRFToken"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Vary"] = "Origin"
        return response


class RateLimitMiddleware:
    """Enforce per-user/IP request rate limits (default 10 requests/second)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "RATE_LIMIT_ENABLED", True):
            return self.get_response(request)

        path = request.path_info
        # Skip static and media assets to prevent asset throttling
        if path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        is_allowed, count, retry_after, remaining, limit = RateLimiter.check_rate_limit(request)

        if not is_allowed:
            is_json = request.headers.get("Accept") == "application/json" or path.startswith("/api/")
            if is_json:
                response = JsonResponse(
                    {
                        "error": f"Request rate limit exceeded. Maximum {limit} requests per second allowed.",
                        "retry_after": retry_after,
                    },
                    status=429,
                )
            else:
                response = HttpResponse(
                    f"429 Too Many Requests: Rate limit exceeded ({limit} req/s max). Please retry after {retry_after} second(s).",
                    status=429,
                    content_type="text/plain",
                )
            response["Retry-After"] = str(retry_after)
            response["X-RateLimit-Limit"] = str(limit)
            response["X-RateLimit-Remaining"] = "0"
            response["X-RateLimit-Reset"] = str(retry_after)
            return response

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(limit)
        response["X-RateLimit-Remaining"] = str(remaining)
        return response
