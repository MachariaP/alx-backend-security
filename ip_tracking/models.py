from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """Model to log IP addresses and request metadata."""
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    path = models.CharField(max_length=500)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.path} at {self.timestamp}"


class BlockedIP(models.Model):
    """Model to store blacklisted IP addresses."""
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        ordering = ['-blocked_at']

    def __str__(self):
        return f"Blocked: {self.ip_address}"


class SuspiciousIP(models.Model):
    """Model to flag suspicious IP addresses."""
    ip_address = models.GenericIPAddressField()
    reason = models.TextField()
    flagged_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Suspicious IP"
        verbose_name_plural = "Suspicious IPs"
        ordering = ['-flagged_at']
        indexes = [
            models.Index(fields=['ip_address', '-flagged_at']),
        ]

    def __str__(self):
        return f"Suspicious: {self.ip_address} - {self.reason}"
