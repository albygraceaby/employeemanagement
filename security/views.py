import json

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .decorators import jwt_required
from .jwt import decode_token, issue_token


def _json_body(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
        return body if isinstance(body, dict) else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def _find_user(identifier):
    User = get_user_model()
    return User.objects.filter(username__iexact=identifier).first() or User.objects.filter(email__iexact=identifier).first()


@csrf_exempt
def token_view(request):
    """Issue short-lived access + long-lived refresh JWTs after password authentication."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    data = _json_body(request)
    identifier = str(data.get("username") or data.get("email") or "").strip()
    password = data.get("password")
    if not identifier or not isinstance(password, str):
        return JsonResponse({"error": "Username/email and password are required."}, status=400)

    user = _find_user(identifier)
    authenticated = authenticate(request, username=user.username if user else identifier, password=password)
    if not authenticated or not authenticated.is_active:
        # Deliberately generic: never reveal whether an account exists.
        return JsonResponse({"error": "Invalid credentials."}, status=401)

    return JsonResponse({
        "access": issue_token(authenticated, "access"),
        "refresh": issue_token(authenticated, "refresh"),
        "token_type": "Bearer",
        "expires_in": 900,
    })


@csrf_exempt
def refresh_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)
    data = _json_body(request)
    token = data.get("refresh")
    user = decode_token(token, expected_type="refresh") if isinstance(token, str) else None
    if not user:
        return JsonResponse({"error": "Invalid or expired refresh token."}, status=401)
    return JsonResponse({
        "access": issue_token(user, "access"),
        "token_type": "Bearer",
        "expires_in": 900,
    })


@jwt_required
def me_view(request):
    """Safe authenticated-user endpoint; intentionally excludes password/session data."""
    user = request.jwt_user
    return JsonResponse({
        "id": user.pk,
        "username": user.username,
        "role": user.role,
    })
