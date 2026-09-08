from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [("jobs", "0004_alter_job_skills_required")]
    operations = [
        migrations.AddField(model_name="application", name="interview_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="application", name="interview_mode", field=models.CharField(blank=True, help_text="Online, Phone, or On-site", max_length=30)),
        migrations.AddField(model_name="application", name="interview_link", field=models.URLField(blank=True)),
        migrations.AddField(model_name="application", name="interview_location", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="application", name="interview_notes", field=models.TextField(blank=True)),
        migrations.AddField(model_name="application", name="last_notified_status", field=models.CharField(blank=True, max_length=20)),
    ]
