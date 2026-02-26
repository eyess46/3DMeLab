from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, VerificationCode, Contactform


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the email-based User model.
    """
    list_display = ('email', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    # Hide username field completely (it's None anyway)
    exclude = ('username',)

    # Optional: readonly fields if you want to protect certain data
    readonly_fields = ('last_login', 'date_joined')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """
    Admin view for email verification codes.
    Shows status (expired/active), attempts, but NEVER shows the actual code.
    """
    list_display = (
        'user_email',
        'status_display',
        'attempts',
        'created_at',
        'is_expired_flag',
    )
    list_filter = ('created_at', 'attempts')
    search_fields = ('user__email',)
    ordering = ('-created_at',)

    # Make almost everything read-only
    readonly_fields = (
        'user',
        'created_at',
        'attempts',
        'hashed_code_preview',
        'status_display',
        'is_expired_flag',
    )

    # Prevent anyone from adding/editing codes manually
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False   # view-only — no edits allowed

    # Custom display fields
    @admin.display(description='Email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Status')
    def status_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: #dc3545;">Expired</span>')
        return format_html('<span style="color: #198754;">Active</span>')

    @admin.display(description='Expired?')
    def is_expired_flag(self, obj):
        return "Yes" if obj.is_expired() else "No"

    @admin.display(description='Code Hash (preview)')
    def hashed_code_preview(self, obj):
        if obj.code_hash:
            return obj.code_hash[:16] + "..." + obj.code_hash[-8:]
        return "—"

    # Fieldsets for clean layout
    fieldsets = (
        (None, {
            'fields': ('user', 'user_email', 'status_display', 'is_expired_flag')
        }),
        ('Security Info', {
            'fields': ('hashed_code_preview', 'attempts', 'created_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Contactform)
class ContactFormAdmin(admin.ModelAdmin):
    """
    Admin interface for contact form submissions.
    """
    list_display = ('name', 'email', 'subject', 'created_at', 'short_message')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Message preview')
    def short_message(self, obj):
        return (obj.message[:80] + '...') if len(obj.message) > 80 else obj.message