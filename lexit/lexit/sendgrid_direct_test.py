from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

# Direct SendGrid test without Django's send_mail
@csrf_exempt
def direct_sendgrid_test(request):
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # Handle both GET and POST requests
        if request.method == 'POST' and request.body:
            try:
                data = json.loads(request.body)
                to_email = data.get('to_email', 'ashley.osborne@prs-im.co.uk')
            except json.JSONDecodeError:
                to_email = 'ashley.osborne@prs-im.co.uk'
        else:
            # Default for GET requests
            to_email = 'ashley.osborne@prs-im.co.uk'
        
        # Get API key
        api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not api_key:
            return JsonResponse({'success': False, 'error': 'SendGrid API key not found'})
        
        # Create SendGrid client
        sg = SendGridAPIClient(api_key=api_key)
        
        # Try different verified sender addresses
        # 1. First try with noreply@lexit.tech (what we configured in DNS)
        # 2. If that fails, try with a generic SendGrid sender
        from_emails_to_try = [
            'noreply@lexit.tech',          # Our authenticated domain
            'test@example.com',            # Generic test address
            'noreply@sendgrid.com'         # SendGrid default
        ]
        
        last_error = None
        
        for from_email in from_emails_to_try:
            try:
                # Create simple email
                message = Mail(
                    from_email=from_email,
                    to_emails=to_email,
                    subject=f'Direct SendGrid Test - LEXIT (from {from_email})',
                    plain_text_content=f'This is a direct SendGrid API test from LEXIT platform using {from_email}!'
                )
                
                # Send email
                response = sg.send(message)
                
                # If we get here, it worked!
                return JsonResponse({
                    'success': True,
                    'status_code': response.status_code,
                    'message': 'Direct SendGrid test completed successfully',
                    'from_email': from_email,
                    'to_email': to_email,
                    'api_key_status': 'Configured and working',
                    'response_headers': dict(response.headers) if hasattr(response, 'headers') else None
                })
                
            except Exception as email_error:
                last_error = {
                    'from_email': from_email,
                    'error': str(email_error),
                    'error_type': type(email_error).__name__
                }
                continue  # Try next from_email
        
        # If we get here, all from_emails failed
        return JsonResponse({
            'success': False,
            'error': 'All sender addresses failed',
            'last_error': last_error,
            'tried_addresses': from_emails_to_try,
            'to_email': to_email,
            'api_key_status': 'Configured but sender verification failed'
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        })