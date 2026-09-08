# Generated initial migration for TalentSphere jobs.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("description", models.TextField()),
                ("responsibilities", models.TextField(blank=True)),
                ("skills_required", models.TextField(help_text="Comma-separated, e.g. Python, Django, React, SQL")),
                ("location", models.CharField(max_length=150)),
                ("job_type", models.CharField(choices=[("full_time", "Full-time"), ("part_time", "Part-time"), ("internship", "Internship"), ("contract", "Contract"), ("remote", "Remote")], default="full_time", max_length=20)),
                ("experience_required", models.CharField(blank=True, help_text="e.g. 2-4 years", max_length=60)),
                ("salary_min", models.PositiveIntegerField(blank=True, null=True)),
                ("salary_max", models.PositiveIntegerField(blank=True, null=True)),
                ("openings", models.PositiveIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("posted_at", models.DateTimeField(auto_now_add=True)),
                ("recruiter", models.ForeignKey(limit_choices_to={"role": "recruiter"}, on_delete=django.db.models.deletion.CASCADE, related_name="posted_jobs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-posted_at"],
            },
        ),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("applied", "Applied"), ("shortlisted", "Shortlisted"), ("rejected", "Rejected"), ("selected", "Selected")], default="applied", max_length=20)),
                ("cover_note", models.TextField(blank=True)),
                ("applied_at", models.DateTimeField(auto_now_add=True)),
                ("candidate", models.ForeignKey(limit_choices_to={"role": "candidate"}, on_delete=django.db.models.deletion.CASCADE, related_name="applications", to=settings.AUTH_USER_MODEL)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="jobs.job")),
            ],
            options={
                "ordering": ["-applied_at"],
                "unique_together": {("job", "candidate")},
            },
        ),
    ]
