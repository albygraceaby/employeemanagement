from pathlib import Path

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import CustomUser, RecruiterProfile, CandidateProfile


class SignupForm(forms.Form):
    ROLE_CHOICES = CustomUser.Role.choices

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.HiddenInput(attrs={"id": "role"}))
    username = forms.CharField(
        min_length=4, max_length=20,
        widget=forms.TextInput(attrs={"id": "username", "autocomplete": "username"}),
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={"id": "email"}))

    # ---- THE FIX: exactly 10 digits, not 7-12 ----
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={"id": "phone", "inputmode": "numeric"}),
    )

    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "confirmPassword"}))

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        digits = "".join(ch for ch in self.cleaned_data["phone"] if ch.isdigit())
        if len(digits) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")
        return digits

    def clean(self):
        cleaned = super().clean()
        pw, cpw = cleaned.get("password"), cleaned.get("confirm_password")
        if pw and cpw and pw != cpw:
            self.add_error("confirm_password", "Passwords do not match.")
        if pw and len(pw) < 8:
            self.add_error("password", "Password must be at least 8 characters.")
        return cleaned


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"id": "identifier", "autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "loginPassword"}))


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = [
            "full_name", "email", "company_name", "designation",
            "company_website", "industry", "company_size",
            "office_location", "about_company",
        ]
        widgets = {
            "about_company": forms.Textarea(attrs={"rows": 4}),
        }


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = [
            "full_name", "email", "date_of_birth", "location",
            "highest_qualification", "university", "graduation_year",
            "experience_years", "current_company", "current_designation",
            "skills", "projects", "expected_salary", "notice_period_days",
            "linkedin_url", "github_url", "portfolio_url",
            "professional_summary", "resume",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "skills": forms.Textarea(attrs={"rows": 2, "placeholder": "Python, Django, React, SQL"}),
            "projects": forms.Textarea(attrs={"rows": 4}),
            "professional_summary": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        if not resume:
            return resume

        # Basic upload validation: maximum 5 MB.
        if hasattr(resume, "size") and resume.size > 5 * 1024 * 1024:
            raise ValidationError("Resume must be smaller than 5 MB.")

        # Only PDF and DOCX resumes are accepted.
        extension = Path(resume.name).suffix.lower()
        allowed_extensions = {".pdf", ".docx"}
        if extension not in allowed_extensions:
            raise ValidationError("Only PDF and DOCX resume files are allowed.")

        # Basic MIME validation when the browser supplies a content type.
        content_type = getattr(resume, "content_type", "")
        allowed_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        if content_type and content_type not in allowed_types:
            raise ValidationError("Invalid resume file type. Please upload a PDF or DOCX file.")

        return resume
