from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json

@csrf_exempt
@require_POST
def test_email(request):
    try:
        # Parse JSON data
        data = json.loads(request.body)
        to_email = data.get('to_email', 'ashley.osborne@prs-im.co.uk')
        subject = data.get('subject', 'LEXIT Email Test from Railway')
        message = data.get('message', 'This is a test email from LEXIT Railway deployment.')
        
        # Add configuration info to message
        backend_info = f"""
        Email Configuration Test
        
        Backend: {settings.EMAIL_BACKEND}
        From: {settings.DEFAULT_FROM_EMAIL}
        To: {to_email}
        
        Original Message:
        {message}
        
        If you're receiving this email, your email configuration is working correctly!
        
        ---
        LEXIT Real Estate Platform
        """
        
        try:
            # Send the email using Django's send_mail (works with any backend)
            result = send_mail(
                subject=subject,
                message=backend_info,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            # Debug: Check if SendGrid API key is configured
            sendgrid_key_status = "Configured" if getattr(settings, 'SENDGRID_API_KEY', None) else "Missing"
            
            if result:
                return JsonResponse({
                    'success': True, 
                    'message': f'Email sent successfully to {to_email}!',
                    'backend': settings.EMAIL_BACKEND,
                    'from_email': settings.DEFAULT_FROM_EMAIL,
                    'sendgrid_api_key': sendgrid_key_status,
                    'result_count': result
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'Email sending returned 0 - check SendGrid configuration',
                    'backend': settings.EMAIL_BACKEND,
                    'sendgrid_api_key': sendgrid_key_status,
                    'from_email': settings.DEFAULT_FROM_EMAIL
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Email sending exception: {str(e)}',
                'backend': settings.EMAIL_BACKEND,
                'error_type': type(e).__name__,
                'sendgrid_api_key': "Configured" if getattr(settings, 'SENDGRID_API_KEY', None) else "Missing"
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'})