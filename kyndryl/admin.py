from django.contrib import admin
from django.utils.html import format_html
from .models import KyndrylRegistration


@admin.register(KyndrylRegistration)
class KyndrylRegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "registration_number",
        "name",
        "mobile_number",
        "email_id",
        "gender",
        "category",
        "highest_qualification",
        "current_employment_status",
        "beneficiary_belonging",
        "registration_date",
        "photo_link",
        "aadhaar_link",
        "certificate_link",
    )

    list_display_links = (
        "registration_number",
        "name",
    )

    search_fields = (
        "registration_number",
        "name",
        "father_name",
        "mother_name",
        "email_id",
        "mobile_number",
        "aadhar_number",
        "city",
        "state",
        "pin_code",
    )

    list_filter = (
        "gender",
        "category",
        "highest_qualification",
        "current_employment_status",
        "beneficiary_belonging",
        "expertise_in_cloud_computing",
        "state",
        "registration_date",
    )

    readonly_fields = (
        "registration_number",
        "registration_date",
        "updated_at",
        "photo_preview",
        "photo_link",
        "aadhaar_link",
        "certificate_link",
    )

    ordering = ("-registration_date",)

    date_hierarchy = "registration_date"

    list_per_page = 25

    fieldsets = (

        ("Registration Details", {
            "fields": (
                "registration_number",
                "registration_date",
                "updated_at",
            )
        }),

        ("Personal Information", {
            "fields": (
                "name",
                "gender",
                "date_of_birth",
                "category",
                "father_name",
                "father_occupation",
                "mother_name",
                "mother_occupation",
            )
        }),

        ("Contact Information", {
            "fields": (
                "mobile_number",
                "email_id",
                "aadhar_number",
                "address",
                "city",
                "state",
                "pin_code",
            )
        }),

        ("Education & Employment", {
            "fields": (
                "highest_qualification",
                "highest_qualification_certificate_name",
                "current_employment_status",
                "expertise_in_cloud_computing",
                "beneficiary_belonging",
            )
        }),

        ("Uploaded Documents", {
            "fields": (
                "photo",
                "photo_preview",
                "photo_link",
                "aadhaar_card",
                "aadhaar_link",
                "highest_qualification_certificate",
                "certificate_link",
            )
        }),
    )

    # ----------------------------
    # Photo Preview
    # ----------------------------

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="150" style="border-radius:8px;border:1px solid #ddd;" />',
                obj.photo.url
            )
        return "-"

    photo_preview.short_description = "Photo Preview"

    # ----------------------------
    # Photo URL
    # ----------------------------

    def photo_link(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank">View Photo</a>',
                obj.photo.url
            )
        return "-"

    photo_link.short_description = "Photo"

    # ----------------------------
    # Aadhaar URL
    # ----------------------------

    def aadhaar_link(self, obj):
        if obj.aadhaar_card:
            return format_html(
                '<a href="{}" target="_blank">Open Aadhaar</a>',
                obj.aadhaar_card.url
            )
        return "-"

    aadhaar_link.short_description = "Aadhaar"

    # ----------------------------
    # Certificate URL
    # ----------------------------

    def certificate_link(self, obj):
        if obj.highest_qualification_certificate:
            return format_html(
                '<a href="{}" target="_blank">Open Certificate</a>',
                obj.highest_qualification_certificate.url
            )
        return "-"

    certificate_link.short_description = "Certificate"