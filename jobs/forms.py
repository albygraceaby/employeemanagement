from django import forms
from .models import Job, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title", "description", "responsibilities", "skills_required",
            "location", "job_type", "experience_required",
            "salary_min", "salary_max", "openings", "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "responsibilities": forms.Textarea(attrs={"rows": 3}),
            "skills_required": forms.Textarea(attrs={"rows": 2, "placeholder": "Python, Django, React, SQL"}),
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "Private notes about this applicant..."}),
        }


class ApplyForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cover_note"]
        widgets = {
            "cover_note": forms.Textarea(attrs={"rows": 5, "placeholder": "Tell the recruiter why you're a great fit (optional)..."}),
        }
        labels = {"cover_note": "Cover note"}
