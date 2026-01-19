from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip
from .models import RequestLog, BlockedIP
import logging
import requests

logger = logging.getLogger(__name__)


class IPTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to log IP addresses and block blacklisted IPs.
    Also performs geolocation lookup if available.
    """

    def process_request(self, request):
        """Process incoming request to check for blocked IPs and log request."""
        # Get the client IP address
        client_ip, is_routable = get_client_ip(request)
        
        if not client_ip:
            return None

        # Check if IP is blocked
        cache_key = f'blocked_ip_{client_ip}'
        is_blocked = cache.get(cache_key)
        
        if is_blocked is None:
            # Check database
            is_blocked = BlockedIP.objects.filter(ip_address=client_ip).exists()
            # Cache the result for 5 minutes
            cache.set(cache_key, is_blocked, 300)
        
        if is_blocked:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return HttpResponseForbidden("Access Denied: Your IP has been blocked.")

        # Log the request
        try:
            self._log_request(client_ip, request)
        except Exception as e:
            logger.error(f"Error logging request: {e}")

        return None

    def _log_request(self, ip_address, request):
        """Log the request details."""
        path = request.get_full_path()
        
        # Get geolocation data if available
        country, city = self._get_geolocation(ip_address)
        
        # Create log entry
        RequestLog.objects.create(
            ip_address=ip_address,
            path=path,
            country=country,
            city=city
        )

    def _get_geolocation(self, ip_address):
        """Get geolocation data for an IP address with caching."""
        cache_key = f'geo_{ip_address}'
        geo_data = cache.get(cache_key)
        
        if geo_data is not None:
            return geo_data
        
        # Try to get geolocation data
        country = None
        city = None
        
        try:
            # Try using django-ipgeolocation if available
            from django_ipgeolocation import IpGeolocation
            
            geo = IpGeolocation()
            location = geo.locate_ip(ip_address)
            
            if location:
                country = location.get('country_name')
                city = location.get('city')
        except ImportError:
            # Fallback: Try using ipinfo.io or GeoIP2 if available
            try:
                response = requests.get(f'https://ipinfo.io/{ip_address}/json', timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    country = data.get('country')
                    city = data.get('city')
            except Exception as e:
                logger.debug(f"Geolocation lookup failed: {e}")
        except Exception as e:
            logger.debug(f"Geolocation lookup failed: {e}")
        
        # Cache for 24 hours
        geo_data = (country, city)
        cache.set(cache_key, geo_data, 86400)
        
        return geo_data
