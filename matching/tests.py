from django.test import TestCase
from django.urls import reverse

from accounts.models import CandidateProfile, CustomUser
from jobs.models import Application, Job
from .services import calculate_skill_match, extract_job_skills


class SkillGapAnalysisTests(TestCase):
    def setUp(self):
        self.recruiter = CustomUser.objects.create_user(
            username="recruiter-test",
            email="recruiter@example.com",
            password="StrongPass123!",
            phone="9876543210",
            role=CustomUser.Role.RECRUITER,
        )
        self.candidate = CustomUser.objects.create_user(
            username="candidate-test",
            email="candidate@example.com",
            password="StrongPass123!",
            phone="9876543211",
            role=CustomUser.Role.CANDIDATE,
        )
        self.profile = CandidateProfile.objects.create(
            user=self.candidate,
            full_name="Candidate Test",
            email="candidate@example.com",
            skills="Python, Java, React",
        )

    def test_candidate_skills_are_cached_and_normalized(self):
        self.assertEqual(
            set(self.profile.parsed_skills),
            {"python", "java", "react"},
        )

        self.profile.skills = "Python, JS, K8s, React.js"
        self.profile.save()
        self.assertEqual(
            set(self.profile.parsed_skills),
            {"python", "javascript", "kubernetes", "react"},
        )

    def test_skill_gap_api(self):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title="Backend Engineer",
            description="Python, Java, R, PHP, React, AI, Kubernates, Docker",
            responsibilities="",
            skills_required="Python, Java, React",
            location="Hyderabad",
        )
        self.client.force_login(self.candidate)
        response = self.client.get(
            reverse("candidate_skill_gap_api", args=[job.id])
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["match_percentage"], 37.5)
        self.assertEqual(
            set(payload["missing_skills"]),
            {"r", "php", "artificial intelligence", "kubernetes", "docker"},
        )

    def test_example_skill_gap(self):
        result = calculate_skill_match(
            ["Python", "Java", "React"],
            ["Python", "Java", "R", "PHP", "React", "AI", "Kubernates", "Docker"],
        )
        self.assertEqual(result["match_percentage"], 37.5)
        self.assertEqual(
            set(result["missing_skills"]),
            {"r", "php", "react", "docker", "kubernetes", "artificial intelligence"}
            - {"react"},
        )
        self.assertEqual(
            set(result["matching_skills"]),
            {"python", "java", "react"},
        )

    def test_job_description_is_used_and_cached(self):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title="Software Engineer",
            description="Build services using Python, Java, R, PHP, React, AI, Kubernates and Docker.",
            responsibilities="Deploy with K8s.",
            skills_required="Python, Java",
            location="Hyderabad",
        )
        self.assertIn("python", job.parsed_skills)
        self.assertIn("r", job.parsed_skills)
        self.assertIn("php", job.parsed_skills)
        self.assertIn("react", job.parsed_skills)
        self.assertIn("artificial intelligence", job.parsed_skills)
        self.assertIn("kubernetes", job.parsed_skills)
        self.assertIn("docker", job.parsed_skills)

    def test_candidate_can_view_gap_after_applying(self):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title="Full Stack Engineer",
            description="Python, Java, R, PHP, React, AI, Kubernates, Docker",
            responsibilities="",
            skills_required="Python, Java, React",
            location="Hyderabad",
        )
        Application.objects.create(job=job, candidate=self.candidate)
        self.client.force_login(self.candidate)
        response = self.client.get(reverse("candidate_skill_gap", args=[job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "kubernetes")
        self.assertContains(response, "docker")
        self.assertContains(response, "php")
        self.assertContains(response, "r")

    def test_missing_skills_detailed_and_category_breakdown(self):
        result = calculate_skill_match(
            ["Python", "React"],
            ["Python", "React", "Docker", "Kubernetes", "SQL"],
        )
        self.assertEqual(result["match_percentage"], 40.0)
        self.assertEqual(result["critical_missing_count"], 3)  # Docker, Kubernetes, SQL
        self.assertIn("DevOps & Cloud", result["category_breakdown"])
        self.assertIn("Database", result["category_breakdown"])

    def test_learning_path_generator_and_roadmap(self):
        from .learning_paths import generate_learning_path, get_skill_learning_roadmap
        roadmap = get_skill_learning_roadmap("docker")
        self.assertEqual(roadmap["skill_name"], "Docker")
        self.assertEqual(roadmap["category"], "DevOps & Cloud")
        self.assertTrue(len(roadmap["milestones"]) >= 3)
        self.assertTrue(len(roadmap["resources"]) >= 1)

        lp = generate_learning_path(["docker", "sql"], target_job_title="DevOps Engineer")
        self.assertEqual(lp["missing_skill_count"], 2)
        self.assertTrue(lp["total_estimated_hours"] > 0)
        self.assertEqual(len(lp["roadmaps"]), 2)

    def test_learning_path_views_and_api(self):
        job = Job.objects.create(
            recruiter=self.recruiter,
            title="DevOps Developer",
            description="Docker, Kubernetes, AWS, Python",
            skills_required="Docker, Kubernetes, AWS, Python",
            location="Remote",
        )
        self.client.force_login(self.candidate)

        # HTML Learning Path view
        res_html = self.client.get(reverse("candidate_learning_path", args=[job.id]))
        self.assertEqual(res_html.status_code, 200)
        self.assertContains(res_html, "Personalised Learning Path")

        # Standalone skill roadmap
        res_skill = self.client.get(reverse("skill_learning_roadmap", args=["python"]))
        self.assertEqual(res_skill.status_code, 200)
        self.assertContains(res_skill, "Skill Roadmap: Python")

        # JSON Learning Path API
        res_api = self.client.get(reverse("candidate_learning_path_api", args=[job.id]))
        self.assertEqual(res_api.status_code, 200)
        json_data = res_api.json()
        self.assertEqual(json_data["job_id"], job.id)
        self.assertIn("learning_path", json_data)
        self.assertTrue(json_data["learning_path"]["missing_skill_count"] > 0)

