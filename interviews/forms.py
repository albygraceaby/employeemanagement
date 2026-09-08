from django import forms
from jobs.models import Application
from .models import Interview


class InterviewForm(forms.ModelForm):
    application = forms.ModelChoiceField(
        queryset=Application.objects.none(),
        label="Candidate / Job",
        empty_label="Select an applicant",
    )

    class Meta:
        model = Interview
        fields = [
            "application", "scheduled_date", "scheduled_time",
            "mode", "meeting_link_or_venue", "notes",
        ]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "scheduled_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "meeting_link_or_venue": forms.TextInput(
                attrs={"placeholder": "Meeting link, phone details, or venue"}
            ),
        }

    def __init__(self, *args, recruiter=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Application.objects.select_related(
            "candidate", "job", "candidate__candidate_profile"
        )
        if recruiter is not None:
            qs = qs.filter(job__recruiter=recruiter)
        self.fields["application"].queryset = qs

    def clean_application(self):
        app = self.cleaned_data["application"]
        if hasattr(app, "interview"):
            raise forms.ValidationError("This application already has an interview. Use Update Interview instead.")
        return app


class InterviewStatusForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ["status", "scheduled_date", "scheduled_time", "mode",
                  "meeting_link_or_venue", "notes"]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "scheduled_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
