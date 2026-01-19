from django.contrib import admin
from .models import RequestLog, BlockedIP, SuspiciousIP


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'path', 'country', 'city', 'timestamp')
    list_filter = ('timestamp', 'country', 'city')
    search_fields = ('ip_address', 'path', 'country', 'city')
    date_hierarchy = 'timestamp'
    readonly_fields = ('ip_address', 'timestamp', 'path', 'country', 'city')


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'blocked_at')
    list_filter = ('blocked_at',)
    search_fields = ('ip_address', 'reason')
    date_hierarchy = 'blocked_at'


@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'reason', 'resolved', 'flagged_at')
    list_filter = ('resolved', 'flagged_at')
    search_fields = ('ip_address', 'reason')
    date_hierarchy = 'flagged_at'
    list_editable = ('resolved',)

