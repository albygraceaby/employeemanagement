# Generated initial migration for TalentSphere accounts.
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(auto_now_add=True, verbose_name="date joined")),
                ("role", models.CharField(choices=[("recruiter", "Recruiter"), ("candidate", "Candidate")], max_length=20)),
                ("phone", models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message="Phone number must be exactly 10 digits.", regex="^\\d{10}$")])),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="customuser_set", related_query_name="customuser", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="customuser_set", related_query_name="customuser", to="auth.permission", verbose_name="user permissions")),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
        ),
        migrations.CreateModel(
            name="RecruiterProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("company_name", models.CharField(max_length=150)),
                ("designation", models.CharField(blank=True, max_length=120)),
                ("company_website", models.URLField(blank=True)),
                ("industry", models.CharField(blank=True, max_length=120)),
                ("company_size", models.CharField(blank=True, choices=[("1-10", "1-10 employees"), ("11-50", "11-50 employees"), ("51-200", "51-200 employees"), ("201-500", "201-500 employees"), ("500+", "500+ employees")], max_length=30)),
                ("office_location", models.CharField(blank=True, max_length=150)),
                ("about_company", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="recruiter_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="CandidateProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=150)),
                ("highest_qualification", models.CharField(blank=True, choices=[("high_school", "High School"), ("diploma", "Diploma"), ("bachelors", "Bachelor's Degree"), ("masters", "Master's Degree"), ("phd", "PhD")], max_length=20)),
                ("university", models.CharField(blank=True, max_length=150)),
                ("graduation_year", models.PositiveIntegerField(blank=True, null=True)),
                ("experience_years", models.DecimalField(decimal_places=1, default=0, max_digits=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)])),
                ("current_company", models.CharField(blank=True, max_length=150)),
                ("current_designation", models.CharField(blank=True, max_length=120)),
                ("skills", models.TextField(help_text="Comma-separated, e.g. Python, Django, React, SQL")),
                ("projects", models.TextField(blank=True, help_text="Brief description of key projects")),
                ("expected_salary", models.PositiveIntegerField(blank=True, help_text="Annual, in your local currency", null=True)),
                ("notice_period_days", models.PositiveIntegerField(blank=True, null=True)),
                ("linkedin_url", models.URLField(blank=True)),
                ("github_url", models.URLField(blank=True)),
                ("portfolio_url", models.URLField(blank=True)),
                ("professional_summary", models.TextField(blank=True)),
                ("resume", models.FileField(blank=True, null=True, upload_to="resumes/")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="candidate_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
