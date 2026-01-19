# IP Tracking Module

A comprehensive IP tracking, security, and analytics system for Django applications.

## Overview

This module implements IP tracking functionality including:
- Request logging with IP addresses and geolocation
- IP blacklisting for security
- Rate limiting to prevent abuse
- Anomaly detection for suspicious behavior
- Admin interface for managing tracked IPs

## Features

### 1. IP Logging Middleware

Every incoming request is automatically logged with:
- IP address
- Request path
- Timestamp
- Geolocation data (country, city)

The middleware uses `django-ipware` to reliably extract client IP addresses, even behind proxies.

### 2. IP Blacklisting

Block malicious IP addresses from accessing the application:

```bash
# Block a single IP
python manage.py block_ip 192.168.1.100 --reason "Suspicious activity"

# Block without reason
python manage.py block_ip 10.0.0.1
```

Blocked IPs receive a 403 Forbidden response immediately at the middleware level.

### 3. Geolocation

Automatic IP geolocation lookup with:
- 24-hour caching to reduce API calls
- Fallback to ipinfo.io if django-ipgeolocation is not configured
- Country and city information stored in RequestLog

### 4. Rate Limiting

Three example endpoints with different rate limits:

- **Anonymous Login** (`/ip-tracking/login/`): 5 requests/minute
- **Authenticated Action** (`/ip-tracking/action/`): 10 requests/minute (requires login)
- **Sensitive Endpoint** (`/ip-tracking/sensitive/`): 5 requests/minute

Configure rate limits in your views:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def my_view(request):
    if getattr(request, 'limited', False):
        return JsonResponse({'error': 'Too many requests'}, status=429)
    # Your view logic
```

### 5. Anomaly Detection

Celery task runs hourly to detect:
- IPs with more than 100 requests in the last hour
- IPs repeatedly accessing sensitive paths (/admin, /login)

Suspicious IPs are flagged in the `SuspiciousIP` model for review.

## Models

### RequestLog
Stores all request logs with IP and geolocation data.

**Fields:**
- `ip_address`: GenericIPAddressField
- `timestamp`: DateTimeField (indexed)
- `path`: CharField (500 max length)
- `country`: CharField (optional)
- `city`: CharField (optional)

### BlockedIP
Manages the IP blacklist.

**Fields:**
- `ip_address`: GenericIPAddressField (unique)
- `reason`: TextField (optional)
- `blocked_at`: DateTimeField

### SuspiciousIP
Flags IPs with suspicious behavior.

**Fields:**
- `ip_address`: GenericIPAddressField
- `reason`: TextField
- `flagged_at`: DateTimeField (indexed)
- `resolved`: BooleanField

## Configuration

### Settings

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_ratelimit',
    'ip_tracking',
]

MIDDLEWARE = [
    # ...
    'ip_tracking.middleware.IPTrackingMiddleware',
]

# Cache configuration (use Redis/Memcached in production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# IP Tracking configuration
IP_TRACKING_ENABLED = True
IP_TRACKING_LOG_SENSITIVE_PATHS = ['/admin', '/login', '/api/admin', '/accounts/login']
IP_TRACKING_MAX_REQUESTS_PER_HOUR = 100
IP_TRACKING_GEOLOCATION_CACHE_TIMEOUT = 86400  # 24 hours
```

### URLs

Add to your main `urls.py`:

```python
urlpatterns = [
    # ...
    path('ip-tracking/', include('ip_tracking.urls')),
]
```

## Celery Setup

To enable anomaly detection, run Celery worker and beat:

```bash
# Start Celery worker
celery -A job_scraper_project worker -l info

# Start Celery beat (scheduler)
celery -A job_scraper_project beat -l info
```

The anomaly detection task runs every hour automatically.

## Admin Interface

Access the admin interface at `/admin/` to:
- View all request logs
- Manage blocked IPs
- Review suspicious IPs
- Mark suspicious IPs as resolved

## Production Considerations

### Cache Backend

For production, use Redis or Memcached:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Privacy & Compliance

- **GDPR/CCPA**: Consider IP address anonymization
- **Data Retention**: Implement automatic deletion of old logs
- **User Disclosure**: Update privacy policy to mention IP tracking
- **Opt-out**: Consider providing opt-out mechanisms where required

### Performance

- Use Redis for caching and Celery broker
- Add database indexes on frequently queried fields (already configured)
- Consider log rotation or archival for old RequestLog entries
- Use Celery for geolocation lookups to avoid blocking requests

### Security

- Regularly review and update blocked IPs
- Monitor suspicious IP flags
- Set appropriate rate limits for your use case
- Use HTTPS to protect data in transit
- Secure your Redis/cache backend

## API Examples

### Check Rate Limit

```python
import requests

# Test anonymous endpoint
response = requests.post('http://localhost:8000/ip-tracking/login/')
print(response.json())
# {'message': 'Login endpoint'}

# After 5 requests in a minute
response = requests.post('http://localhost:8000/ip-tracking/login/')
print(response.status_code)  # 429
print(response.json())
# {'error': 'Too many requests. Please try again later.'}
```

## Testing

Run Django tests:

```bash
python manage.py test ip_tracking
```

## Troubleshooting

### Cache Backend Warnings

If you see cache backend warnings, ensure you're using Redis or Memcached in production:

```python
# Silence warnings in development only
SILENCED_SYSTEM_CHECKS = [
    'django_ratelimit.E003',
    'django_ratelimit.W001',
]
```

### Celery Not Running

Ensure Redis is running and accessible:

```bash
redis-cli ping
# Should return: PONG
```

### Geolocation Not Working

The middleware gracefully handles geolocation failures. Check:
1. Network connectivity
2. API rate limits (ipinfo.io)
3. Consider using GeoIP2 database for offline lookups

## License

This module is part of the Django Job Scraper project.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows Django best practices
- Security considerations are addressed
- Documentation is updated

