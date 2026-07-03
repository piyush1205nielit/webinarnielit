from django.contrib import admin
from django.utils.html import format_html

from .models import CertificateDesign, StudentCertificate

@admin.register(CertificateDesign)
class CertificateDesignAdmin(admin.ModelAdmin):
    list_display = (
        "certificate_title", "is_active", "logo_preview", "background_preview", "signatory_count", 
        "show_qr_code","created_at",
    )
    list_display_links = (
        "certificate_title",
    )
    list_editable = (
        "is_active",
    )
    search_fields = (
        "certificate_title", "header_title", "header_subtitle", "signature_1_name", "signature_2_name",
    )
    list_filter = (
        "is_active", "logo_position", "signatory_count", "show_qr_code", "created_at",
    )
    ordering = (
        "-is_active", "-created_at",
    )
    date_hierarchy = "created_at"
    list_per_page = 20
    readonly_fields = (
        "created_at", "updated_at", "logo_preview_large", "secondary_logo_preview", 
        "background_preview_large", "signature1_preview", "signature2_preview", "logo_link", "background_link",
    )

    fieldsets = (

        ("Header", {
            "fields": (
                "header_title",
                "header_subtitle",
            )
        }),

        ("Logos", {
            "fields": (
                "logo_position", "logo_size",
                "institute_logo",
                "logo_preview_large",
                "logo_link",
                "secondary_logo",
                "secondary_logo_preview",
            )
        }),

        ("Certificate Title", {
            "fields": (
                "certificate_title",
                "title_font_size",
                "title_color",
            )
        }),

        ("Certificate Body", {
            "fields": (
                "line_1_text",
                "line_2_student_name",
                "line_2_custom_text",
                "line_2_font_size",
                "line_2_color",
                "line_3_text",
                "line_4_show_course",
                "line_4_custom_text",
                "line_4_font_size",
                "line_4_color",
                "line_5_date_range",
                "line_5_custom_text",
                "line_5_font_size",
                "line_5_color",
            )
        }),

        ("Signatories", {
            "fields": (
                "signatory_count",
                "signature_1_position",
                "signature_1_name",
                "signature_1_designation",
                "signature_1_image",
                "signature1_preview",
                "signature_2_name",
                "signature_2_designation",
                "signature_2_image",
                "signature2_preview",
            )
        }),

        ("Footer", {
            "fields": (
                "show_certificate_number",
                "show_registration_number",
                "show_student_id",
                "show_issue_date",
                "footer_font_size",
            )
        }),

        ("Background & Border", {
            "fields": (
                "border_color",
                "border_width",
                "background_image",
                "background_preview_large",
                "background_link",
            )
        }),

        ("QR Code", {
            "fields": (
                "show_qr_code",
                "qr_code_position",
                "qr_code_size",
            )
        }),

        ("Status", {
            "fields": (
                "is_active",
                "created_at",
                "updated_at",
            )
        }),
    )

    def logo_preview(self, obj):
        if obj.institute_logo:
            return format_html('<img src="{}" width="60">', obj.institute_logo.url)
        return "-"

    logo_preview.short_description = "Logo"

    def background_preview(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" width="60">', obj.background_image.url)
        return "-"

    background_preview.short_description = "Background"

    def logo_preview_large(self, obj):
        if obj.institute_logo:
            return format_html('<img src="{}" width="200">', obj.institute_logo.url)
        return "-"

    def secondary_logo_preview(self, obj):
        if obj.secondary_logo:
            return format_html('<img src="{}" width="200">', obj.secondary_logo.url)
        return "-"

    def background_preview_large(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" width="350">', obj.background_image.url)
        return "-"

    def signature1_preview(self, obj):
        if obj.signature_1_image:
            return format_html('<img src="{}" width="200">', obj.signature_1_image.url)
        return "-"

    def signature2_preview(self, obj):
        if obj.signature_2_image:
            return format_html('<img src="{}" width="200">', obj.signature_2_image.url)
        return "-"

    def logo_link(self, obj):
        if obj.institute_logo:
            return format_html('<a href="{}" target="_blank">Open Logo</a>', obj.institute_logo.url)
        return "-"

    logo_link.short_description = "Logo URL"

    def background_link(self, obj):
        if obj.background_image:
            return format_html('<a href="{}" target="_blank">Open Background</a>', obj.background_image.url)
        return "-"

    background_link.short_description = "Background URL"

@admin.register(StudentCertificate)
class StudentCertificateAdmin(admin.ModelAdmin):

    list_display = (
        "certificate_number",
        "student",
        "course",
        "issue_date",
        "issued_by",
        "design",
        "created_at",
    )

    list_display_links = (
        "certificate_number",
    )

    search_fields = (
        "certificate_number",
        "student__name",
        "student__email_id",
        "student__mobile_number",
        "issued_by",
    )

    list_filter = (
        "issue_date",
        "design",
        "created_at",
    )

    ordering = (
        "-issue_date",
    )

    date_hierarchy = "issue_date"

    autocomplete_fields = (
        "student",
        "design",
    )

    readonly_fields = (
        "certificate_number",
        "created_at",
    )

    list_per_page = 25

    fieldsets = (

        ("Certificate", {
            "fields": (
                "student",
                "design",
                "certificate_number",
                "issue_date",
            )
        }),

        ("Additional Information", {
            "fields": (
                "issued_by",
                "remarks",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
            )
        }),

    )

    def course(self, obj):
        return obj.student.course_enrolled

    course.short_description = "Course"