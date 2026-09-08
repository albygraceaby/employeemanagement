from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0002_application_interview_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="notes",
            field=models.TextField(blank=True, help_text="Recruiter's private notes about this applicant"),
        ),
        migrations.AddField(
            model_name="application",
            name="match_score",
            field=models.FloatField(blank=True, help_text="Overall AI match percentage", null=True),
        ),
        migrations.AddField(
            model_name="application",
            name="skill_match_score",
            field=models.FloatField(blank=True, help_text="Skill match percentage", null=True),
        ),
        migrations.AddField(
            model_name="application",
            name="experience_match_score",
            field=models.FloatField(blank=True, help_text="Experience match percentage", null=True),
        ),
        migrations.AddField(
            model_name="application",
            name="ai_recommendation",
            field=models.CharField(blank=True, help_text="AI-generated recommendation label", max_length=255),
        ),
        migrations.AddField(
            model_name="application",
            name="analyzed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
