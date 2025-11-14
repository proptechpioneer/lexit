from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def test_email(request):
    """Test email functionality - for testing purposes only"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        to_email = data.get('to_email', 'ashley.osborne@prs-im.co.uk')
        
        # Send test email
        result = send_mail(
            subject='LEXIT Email Test from Railway',
            message=f'''
            🎉 Email Test Successful!
            
            This email was sent from your LEXIT application deployed on Railway.
            
            Configuration:
            - From: {settings.DEFAULT_FROM_EMAIL}
            - To: {to_email}
            - Environment: Production (Railway)
            
            If you're receiving this email, your Office 365 SMTP configuration is working correctly!
            
            ---
            LEXIT Real Estate Platform
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Email sent successfully to {to_email}',
            'result': result,
            'from_email': settings.DEFAULT_FROM_EMAIL
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured')
        }, status=500)