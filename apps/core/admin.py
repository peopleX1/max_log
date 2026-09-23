from django.contrib import admin

from apps.core.models import Visitor, VisitorLogEntry


class VisitorLogEntryInline(admin.TabularInline):
    model = VisitorLogEntry
    extra = 0
    readonly_fields = ('field', 'value', 'created_at')
    can_delete = False
    ordering = ('created_at',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'phone', 'country', 'step', 'needs_action', 'ip', 'first_seen_at', 'last_seen_at')
    list_filter = ('step', 'needs_action', 'country')
    search_fields = ('visitor_id', 'phone', 'ip')
    readonly_fields = ('visitor_id', 'first_seen_at', 'last_seen_at')
    inlines = (VisitorLogEntryInline,)
