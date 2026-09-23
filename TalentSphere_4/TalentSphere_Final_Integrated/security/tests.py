import time
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.test.client import Client

from accounts.models import CandidateProfile, RecruiterProfile
from .jwt import decode_token, issue_token
from .rate_limiter import RateLimiter


class SecurityEnhancementTests(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.candidate = User.objects.create_user(
            username="candidate1",
            email="candidate1@example.com",
            password="StrongPass@123",
            phone="9876543210",
            role="candidate",
        )
        self.recruiter = User.objects.create_user(
            username="recruiter1",
            email="recruiter1@example.com",
            password="StrongPass@456",
            phone="9876543211",
            role="recruiter",
        )
        CandidateProfile.objects.create(
            user=self.candidate, full_name="Candidate One", email=self.candidate.email, skills="Python"
        )
        RecruiterProfile.objects.create(
            user=self.recruiter, full_name="Recruiter One", email=self.recruiter.email, company_name="TalentSphere"
        )

    def test_password_is_hashed(self):
        self.assertNotEqual(self.candidate.password, "StrongPass@123")
        self.assertTrue(self.candidate.password.startswith("pbkdf2_"))

    def test_jwt_issue_and_decode(self):
        token = issue_token(self.candidate, "access")
        self.assertEqual(decode_token(token, "access"), self.candidate)

    def test_protected_api_requires_jwt(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)
        token = issue_token(self.candidate, "access")
        response = self.client.get("/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.json())

    def test_login_failure_is_generic(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "candidate1", "password": "wrong-password"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Invalid credentials."})

    @override_settings(CORS_ALLOWED_ORIGINS={"http://localhost:3000"})
    def test_cors_allows_configured_origin_only(self):
        allowed = self.client.options(
            "/api/auth/token/", HTTP_ORIGIN="http://localhost:3000", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST"
        )
        self.assertEqual(allowed.status_code, 204)
        self.assertEqual(allowed["Access-Control-Allow-Origin"], "http://localhost:3000")

        blocked = self.client.options(
            "/api/auth/token/", HTTP_ORIGIN="https://evil.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST"
        )
        self.assertNotIn("Access-Control-Allow-Origin", blocked)

    def test_resume_is_not_public_media_url(self):
        resume = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        profile = self.candidate.candidate_profile
        profile.resume = resume
        profile.save()
        public = self.client.get(f"/media/{profile.resume.name}")
        self.assertEqual(public.status_code, 404)

        # Owner can access profile page when authenticated
        self.client.force_login(self.candidate)
        protected = self.client.get("/profile/")
        self.assertEqual(protected.status_code, 200)

    def test_security_headers_present(self):
        response = self.client.get("/")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertIn("strict-origin", response["Referrer-Policy"])

    # ------------------------------------------------------------------
    # RATE LIMITING & MULTIPLE REQUEST HANDLING TESTS
    # ------------------------------------------------------------------
    def test_rate_limit_allows_up_to_10_requests_per_second(self):
        """Verify that up to 10 requests per second are allowed per user."""
        token = issue_token(self.candidate, "access")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        for i in range(10):
            res = self.client.get("/api/auth/me/", **headers)
            self.assertEqual(res.status_code, 200, f"Request {i+1} should succeed")
            self.assertEqual(res["X-RateLimit-Limit"], "10")

    def test_rate_limit_throttles_11th_request(self):
        """Verify that the 11th request within 1 second returns HTTP 429 Too Many Requests."""
        token = issue_token(self.candidate, "access")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        # Send 10 valid requests
        for i in range(10):
            res = self.client.get("/api/auth/me/", **headers)
            self.assertEqual(res.status_code, 200)

        # 11th request must be throttled
        res_throttled = self.client.get("/api/auth/me/", **headers)
        self.assertEqual(res_throttled.status_code, 429)
        self.assertIn("Retry-After", res_throttled)
        self.assertEqual(res_throttled["X-RateLimit-Remaining"], "0")
        self.assertIn("Request rate limit exceeded", res_throttled.json()["error"])

    def test_rate_limit_isolation_between_users(self):
        """Verify that user A being throttled does not block user B."""
        token_a = issue_token(self.candidate, "access")
        token_b = issue_token(self.recruiter, "access")

        headers_a = {"HTTP_AUTHORIZATION": f"Bearer {token_a}"}
        headers_b = {"HTTP_AUTHORIZATION": f"Bearer {token_b}"}

        # User A sends 11 requests
        for _ in range(10):
            self.client.get("/api/auth/me/", **headers_a)
        res_a_11 = self.client.get("/api/auth/me/", **headers_a)
        self.assertEqual(res_a_11.status_code, 429)

        # User B should still be allowed to make requests
        res_b = self.client.get("/api/auth/me/", **headers_b)
        self.assertEqual(res_b.status_code, 200)

    def test_rate_limit_bypasses_static_assets(self):
        """Verify static asset requests are not throttled."""
        for _ in range(15):
            res = self.client.get("/static/css/style.css")
            self.assertNotEqual(res.status_code, 429)

    def test_concurrent_multiple_requests(self):
        """Test multiple simultaneous requests per second executed concurrently across threads.

        Verifies thread safety and accurate throttling of 15 concurrent requests (10 allowed, 5 throttled).
        """
        from django.test import RequestFactory

        rf = RequestFactory()

        def make_request(req_id):
            request = rf.get("/api/auth/me/")
            request.jwt_user = self.candidate
            is_allowed, count, retry_after, remaining, limit = RateLimiter.check_rate_limit(request, limit=10, window=1)
            return req_id, is_allowed

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(make_request, i) for i in range(15)]
            results = [f.result() for f in futures]

        allowed_count = sum(1 for _, is_allowed in results if is_allowed)
        throttled_count = sum(1 for _, is_allowed in results if not is_allowed)

        self.assertEqual(allowed_count, 10, f"Expected 10 allowed requests, got {allowed_count}")
        self.assertEqual(throttled_count, 5, f"Expected 5 throttled requests, got {throttled_count}")

