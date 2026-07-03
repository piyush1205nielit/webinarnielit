from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Announcement, CarouselImage


# ==========================================================
# Announcement Admin
# ==========================================================

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "short_content",
        "order",
        "is_active",
        "expiry_status",
        "expires_at",
        "created_at",
    )

    list_display_links = (
        "short_content",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = (
        "content",
    )

    list_filter = (
        "is_active",
        "created_at",
        "expires_at",
    )

    ordering = (
        "order",
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    fieldsets = (
        ("Announcement", {
            "fields": (
                "content",
            )
        }),

        ("Display Settings", {
            "fields": (
                "order",
                "is_active",
                "expires_at",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
            )
        }),
    )

    readonly_fields = (
        "created_at",
    )

    def short_content(self, obj):
        if len(obj.content) > 80:
            return obj.content[:80] + "..."
        return obj.content

    short_content.short_description = "Announcement"

    def expiry_status(self, obj):
        if not obj.expires_at:
            return format_html(
                '<span style="color:#2563eb;font-weight:bold;">No Expiry</span>'
            )

        if obj.expires_at < timezone.now():
            return format_html(
                '<span style="color:red;font-weight:bold;">Expired</span>'
            )

        return format_html(
            '<span style="color:green;font-weight:bold;">Active</span>'
        )

    expiry_status.short_description = "Status"


# ==========================================================
# Carousel Image Admin
# ==========================================================

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):

    list_display = (
        "image_preview",
        "order",
        "is_active",
        "image_link",
        "created_at",
    )

    list_display_links = (
        "image_preview",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "order",
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 20

    readonly_fields = (
        "created_at",
        "image_preview_large",
        "image_link",
    )

    fieldsets = (
        ("Carousel Image", {
            "fields": (
                "image",
                "image_preview_large",
                "image_link",
            )
        }),

        ("Display Settings", {
            "fields": (
                "order",
                "is_active",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
            )
        }),
    )

    # -----------------------------
    # Small preview for list page
    # -----------------------------

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;border:1px solid #ddd;">',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Preview"

    # -----------------------------
    # Large preview for detail page
    # -----------------------------

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="350" style="border-radius:8px;border:1px solid #ddd;">',
                obj.image.url,
            )
        return "-"

    image_preview_large.short_description = "Image Preview"

    # -----------------------------
    # Image URL
    # -----------------------------

    def image_link(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank">Open Image</a>',
                obj.image.url,
            )
        return "-"

    image_link.short_description = "Image URL"