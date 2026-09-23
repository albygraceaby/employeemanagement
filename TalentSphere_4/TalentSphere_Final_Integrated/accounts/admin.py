from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, RecruiterProfile, CandidateProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Role & Contact", {"fields": ("role", "phone")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role & Contact", {"fields": ("role", "phone", "email")}),
    )


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company_name", "email", "updated_at")
    search_fields = ("full_name", "company_name", "email")


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "experience_years", "updated_at")
    search_fields = ("full_name", "email", "skills")
