from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("jobs", "0005_integrated_notifications"),
    ]
    operations = [
        migrations.CreateModel(
            name="Interview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scheduled_date", models.DateField()),
                ("scheduled_time", models.TimeField()),
                ("mode", models.CharField(choices=[("online", "Online"), ("phone", "Phone"), ("onsite", "On-site")], default="online", max_length=10)),
                ("meeting_link_or_venue", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("rescheduled", "Rescheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="scheduled", max_length=15)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("application", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="interview", to="jobs.application")),
            ],
        ),
    ]
