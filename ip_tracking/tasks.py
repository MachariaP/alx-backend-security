from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP
import logging

logger = logging.getLogger(__name__)


@shared_task
def detect_anomalies():
    """
    Celery task to detect suspicious IP behavior.
    Runs hourly to check for:
    1. IPs with more than 100 requests in the last hour
    2. IPs accessing sensitive paths (e.g., /admin, /login)
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Find IPs with excessive requests (>100 in the last hour)
    high_frequency_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('id'))
        .filter(request_count__gt=100)
    )
    
    for ip_data in high_frequency_ips:
        ip_address = ip_data['ip_address']
        request_count = ip_data['request_count']
        
        # Check if not already flagged recently
        recent_flag = SuspiciousIP.objects.filter(
            ip_address=ip_address,
            flagged_at__gte=one_hour_ago,
            resolved=False
        ).exists()
        
        if not recent_flag:
            SuspiciousIP.objects.create(
                ip_address=ip_address,
                reason=f'Excessive requests: {request_count} requests in the last hour'
            )
            logger.warning(f'Flagged IP {ip_address} for excessive requests: {request_count}')
    
    # Find IPs accessing sensitive paths
    sensitive_paths = ['/admin', '/login', '/api/admin', '/accounts/login']
    
    for sensitive_path in sensitive_paths:
        suspicious_accesses = (
            RequestLog.objects
            .filter(timestamp__gte=one_hour_ago, path__icontains=sensitive_path)
            .values('ip_address')
            .annotate(access_count=Count('id'))
            .filter(access_count__gt=5)  # More than 5 attempts to sensitive paths
        )
        
        for ip_data in suspicious_accesses:
            ip_address = ip_data['ip_address']
            access_count = ip_data['access_count']
            
            # Check if not already flagged recently
            recent_flag = SuspiciousIP.objects.filter(
                ip_address=ip_address,
                flagged_at__gte=one_hour_ago,
                resolved=False
            ).exists()
            
            if not recent_flag:
                SuspiciousIP.objects.create(
                    ip_address=ip_address,
                    reason=f'Suspicious access to {sensitive_path}: {access_count} attempts in the last hour'
                )
                logger.warning(
                    f'Flagged IP {ip_address} for suspicious access to {sensitive_path}: {access_count} attempts'
                )
    
    logger.info('Anomaly detection task completed')
    return {
        'high_frequency_count': len(high_frequency_ips),
        'timestamp': timezone.now().isoformat()
    }
