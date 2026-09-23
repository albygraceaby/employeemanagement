from django.db import migrations, models


def populate_candidate_skills(apps, schema_editor):
    from matching.skill_catalog import normalize_skills

    CandidateProfile = apps.get_model("accounts", "CandidateProfile")

    for profile in CandidateProfile.objects.all().iterator():
        explicit = [
            skill.strip()
            for skill in (profile.skills or "").split(",")
            if skill.strip()
        ]
        CandidateProfile.objects.filter(pk=profile.pk).update(
            parsed_skills=sorted(normalize_skills(explicit))
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_customuser_managers_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidateprofile",
            name="parsed_skills",
            field=models.JSONField(blank=True, default=list, editable=False),
        ),
        migrations.AddIndex(
            model_name="candidateprofile",
            index=models.Index(
                fields=["-updated_at"],
                name="accounts_candidate_updated_idx",
            ),
        ),
        migrations.RunPython(
            populate_candidate_skills,
            migrations.RunPython.noop,
        ),
    ]
