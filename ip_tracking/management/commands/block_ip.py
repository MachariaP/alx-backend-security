from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from ip_tracking.models import BlockedIP
import ipaddress


class Command(BaseCommand):
    help = 'Block an IP address by adding it to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address to block'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for blocking this IP'
        )

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        reason = options['reason']

        # Validate IP address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise CommandError(f'Invalid IP address: {ip_address}')

        # Add to blacklist
        blocked_ip, created = BlockedIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={'reason': reason}
        )

        if created:
            # Clear cache for this IP
            cache_key = f'blocked_ip_{ip_address}'
            cache.delete(cache_key)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully blocked IP: {ip_address}'
                )
            )
            if reason:
                self.stdout.write(f'Reason: {reason}')
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'IP {ip_address} is already blocked'
                )
            )
