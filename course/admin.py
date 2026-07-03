from django.contrib import admin
from django.utils.html import format_html

from .models import Course, Centre


# ============================================================
# Centre Admin
# ============================================================

@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):

    list_display = ("centre_name", "centre_contact", "centre_email", "created_at")
    search_fields = ("centre_name", "centre_email", "centre_contact", "centre_address")
    ordering = (
        "centre_name",
    )
    date_hierarchy = "created_at"
    list_per_page = 100


# ============================================================
# Course Admin
# ============================================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "course_name","course_type","course_status","mode","display_fees","max_seats","available_seats",
        "registration_deadline","is_featured", "is_active","image_link","video_link","syllabus_link",
    )

    list_display_links = (
        "course_name",
    )

    search_fields = ("course_name", "slug", "course_desc", "modules_info", "prerequisites", "learning_outcomes")

    list_filter = (
        "course_type", "course_status", "mode", "is_free", "is_active", "is_featured", "created_at", 
        "registration_deadline", "start_date",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_editable = ("course_status", "is_featured", "is_active")

    filter_horizontal = (
        "available_centres",
    )

    readonly_fields = ( 
        "slug", "created_at", "updated_at", "display_fees", "available_seats", "registration_available", 
        "image_preview", "image_link", "video_link", "syllabus_link"
    )

    list_per_page = 100

    fieldsets = (

        ("Course Information", {
            "fields": (
                "course_name",
                "slug",
                "course_desc",
                "course_type",
                "course_status",
                "mode",
            )
        }),

        ("Course Details", {
            "fields": (
                "course_duration",
                "course_fees",
                "display_fees",
                "is_free",
                "max_seats",
                "available_seats",
                "registration_available",
            )
        }),

        ("Dates", {
            "fields": (
                "registration_deadline",
                "start_date",
                "end_date",
                "event_date",
            )
        }),

        ("Course Media", {
            "fields": (
                "image",
                "image_preview",
                "image_link",
                "video_file",
                "video_url",
                "video_link",
                "syllabus_file",
                "syllabus_link",
            )
        }),

        ("Course Content", {
            "fields": (
                "modules_info",
                "prerequisites",
                "learning_outcomes",
            )
        }),

        ("Available Centres", {
            "fields": (
                "available_centres",
            )
        }),

        ("Visibility", {
            "fields": (
                "is_featured",
                "is_active",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
    # Image Preview
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="220" style="border-radius:8px;border:1px solid #ddd;">',obj.image.url)
        return "-"

    image_preview.short_description = "Image Preview"

    # Image Link
    def image_link(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">View Image</a>',
                obj.image.url,
            )
        return "-"

    image_link.short_description = "Image"

    # Video Link

    def video_link(self, obj):

        if obj.video_file:
            return format_html('<a href="{}" target="_blank">Uploaded Video</a>', obj.video_file.url)

        if obj.video_url:
            return format_html('<a href="{}" target="_blank">External Video</a>',obj.video_url)
        return "-"
    video_link.short_description = "Video"

    # Syllabus Link
    def syllabus_link(self, obj):
        if obj.syllabus_file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.syllabus_file.url)
        return "-"
    syllabus_link.short_description = "Syllabus"

    # Seats Available
    def available_seats(self, obj):
        return obj.get_seats_available()
    available_seats.short_description = "Seats Left"

    # Registration Status
    def registration_available(self, obj):
        if obj.is_available_for_registration():
            return format_html('<span style="color:green;font-weight:bold;">✔ Available</span>')
        return format_html('<span style="color:red;font-weight:bold;">✘ Closed</span>')
    registration_available.short_description = "Registration"