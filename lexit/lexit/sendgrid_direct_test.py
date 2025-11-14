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
        
        data = json.loads(request.body)
        to_email = data.get('to_email', 'ashley.osborne@prs-im.co.uk')
        
        # Get API key
        api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not api_key:
            return JsonResponse({'success': False, 'error': 'SendGrid API key not found'})
        
        # Create SendGrid client
        sg = SendGridAPIClient(api_key=api_key)
        
        # Create simple email - try with a basic from email first
        message = Mail(
            from_email='test@mg.lexit.tech',  # Simple test from email
            to_emails=to_email,
            subject='Direct SendGrid Test - LEXIT',
            plain_text_content='This is a direct SendGrid API test from LEXIT platform!'
        )
        
        # Send email
        response = sg.send(message)
        
        return JsonResponse({
            'success': True,
            'status_code': response.status_code,
            'message': 'Direct SendGrid test completed',
            'from_email': 'test@mg.lexit.tech',
            'to_email': to_email,
            'api_key_status': 'Configured' if api_key else 'Missing'
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        })