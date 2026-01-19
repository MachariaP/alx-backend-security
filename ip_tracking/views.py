from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required


@ratelimit(key='ip', rate='5/m', method='POST')
@require_http_methods(["POST"])
def anonymous_login(request):
    """
    Example login view with rate limiting for anonymous users.
    Rate: 5 requests per minute for anonymous users.
    """
    if getattr(request, 'limited', False):
        return JsonResponse(
            {'error': 'Too many requests. Please try again later.'},
            status=429
        )
    
    # Login logic would go here
    return JsonResponse({'message': 'Login endpoint'})


@ratelimit(key='ip', rate='10/m', method='POST')
@login_required
@require_http_methods(["POST"])
def authenticated_action(request):
    """
    Example sensitive view with rate limiting for authenticated users.
    Rate: 10 requests per minute for authenticated users.
    """
    if getattr(request, 'limited', False):
        return JsonResponse(
            {'error': 'Too many requests. Please try again later.'},
            status=429
        )
    
    # Sensitive action logic would go here
    return JsonResponse({'message': 'Authenticated action endpoint'})


@ratelimit(key='ip', rate='5/m', method=['GET', 'POST'])
def sensitive_endpoint(request):
    """
    Generic sensitive endpoint with rate limiting.
    Rate: 5 requests per minute regardless of authentication.
    """
    if getattr(request, 'limited', False):
        return JsonResponse(
            {'error': 'Too many requests. Please try again later.'},
            status=429
        )
    
    return JsonResponse({'message': 'Sensitive endpoint accessed successfully'})
