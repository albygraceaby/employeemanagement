from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("applied", "Applied"),
                    ("shortlisted", "Shortlisted"),
                    ("rejected", "Rejected"),
                    ("selected", "Selected"),
                    ("interview", "Interview"),
                ],
                default="applied",
                max_length=20,
            ),
        ),
    ]
