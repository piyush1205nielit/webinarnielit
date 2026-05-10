from django.contrib import admin
from .models import Student, Certificate

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'name', 'mobile_number', 'email_id', 'course_enrolled', 'status', 'registration_date']
    list_filter = ['status', 'course_enrolled', 'preferred_centre', 'registration_date']
    search_fields = ['registration_number', 'name', 'mobile_number', 'email_id']
    readonly_fields = ['registration_number']
    list_editable = ['status']
    list_per_page = 20
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'father_name', 'date_of_birth', 'category')
        }),
        ('Contact Information', {
            'fields': ('email_id', 'mobile_number')
        }),
        ('Course Information', {
            'fields': ('course_enrolled', 'preferred_centre', 'registration_number', 'status', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('registration_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['registration_number', 'registration_date', 'updated_at']
    
    actions = ['confirm_registrations', 'complete_registrations']
    
    def confirm_registrations(self, request, queryset):
        updated = queryset.update(status='confirmed', is_approved=True)
        self.message_user(request, f'{updated} registrations confirmed.')
    confirm_registrations.short_description = 'Confirm selected registrations'
    
    def complete_registrations(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} registrations marked as completed.')
    complete_registrations.short_description = 'Mark as completed'

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'student', 'issue_date']
    search_fields = ['certificate_number', 'student__name', 'student__registration_number']
    readonly_fields = ['certificate_number', 'issue_date']