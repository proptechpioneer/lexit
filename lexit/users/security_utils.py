import logging
from functools import wraps
from django.http import HttpResponseBadRequest
from django.conf import settings
from honeypot.decorators import verify_honeypot_value


logger = logging.getLogger('security')


def get_client_ip(request):
    """Get the real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_honeypot_attempt(request, field_name, field_value):
    """Log honeypot attempt to database and log file"""
    from .models import HoneypotAttempt
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    path = request.get_full_path()
    referer = request.META.get('HTTP_REFERER', '')
    
    # Create database record
    try:
        HoneypotAttempt.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            honeypot_field=field_name,
            honeypot_value=field_value,
            form_data=dict(request.POST),
            path=path,
            referer=referer,
            attempt_type='honeypot',
            blocked=True
        )
        
        # Log to file
        logger.warning(
            f"Honeypot violation detected: IP={ip_address}, "
            f"Field={field_name}, Value={field_value[:50]}..., "
            f"Path={path}, UserAgent={user_agent[:100]}..."
        )
        
        print(f"SECURITY ALERT: Honeypot violation from {ip_address} at {path}")
        
    except Exception as e:
        logger.error(f"Failed to log honeypot attempt: {e}")


def check_honeypot_with_logging(func):
    """Enhanced honeypot decorator that logs violations to database"""
    @wraps(func)
    def inner(request, *args, **kwargs):
        if request.method == 'POST':
            field_name = getattr(settings, 'HONEYPOT_FIELD_NAME', 'honeypot')
            field_value = request.POST.get(field_name, '')
            expected_value = getattr(settings, 'HONEYPOT_VALUE', '')
            
            # Check if honeypot field was filled (bot behavior)
            if field_value != expected_value:
                # Log the violation
                log_honeypot_attempt(request, field_name, field_value)
                
                # Return bad request (same as original honeypot)
                return HttpResponseBadRequest('Bad request')
        
        return func(request, *args, **kwargs)
    return inner