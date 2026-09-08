from django.db import migrations, models


def populate_job_skills(apps, schema_editor):
    from matching.skill_catalog import extract_skills, normalize_skills

    Job = apps.get_model("jobs", "Job")
    for job in Job.objects.all().iterator():
        text = " ".join([
            job.title or "",
            job.description or "",
            job.responsibilities or "",
            job.skills_required or "",
        ])
        explicit = [
            skill.strip()
            for skill in (job.skills_required or "").split(",")
            if skill.strip()
        ]
        skills = sorted(normalize_skills(explicit + extract_skills(text)))
        Job.objects.filter(pk=job.pk).update(parsed_skills=skills)


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0005_integrated_notifications"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="parsed_skills",
            field=models.JSONField(blank=True, default=list, editable=False),
        ),
        migrations.AddIndex(
            model_name="job",
            index=models.Index(
                fields=["is_active", "-posted_at"],
                name="jobs_job_active_posted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="job",
            index=models.Index(
                fields=["recruiter", "-posted_at"],
                name="jobs_job_recruiter_posted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["candidate", "-applied_at"],
                name="jobs_app_candidate_applied_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["job", "-applied_at"],
                name="jobs_app_job_applied_idx",
            ),
        ),
        migrations.RunPython(populate_job_skills, migrations.RunPython.noop),
    ]
