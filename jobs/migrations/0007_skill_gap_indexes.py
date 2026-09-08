from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0006_skill_gap_scalability"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["job", "status", "-applied_at"],
                name="jobs_app_job_status_applied_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="application",
            index=models.Index(
                fields=["candidate", "status", "-applied_at"],
                name="jobs_app_candidate_status_idx",
            ),
        ),
    ]
