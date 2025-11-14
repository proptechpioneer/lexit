from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import socket
import smtplib
from django.conf import settings

@csrf_exempt
@require_POST
def test_email(request):
    try:
        # Parse JSON data
        data = json.loads(request.body)
        to_email = data.get('to_email', 'ashley.osborne@prs-im.co.uk')
        subject = data.get('subject', 'LEXIT Email Test from Railway')
        message = data.get('message', 'This is a test email from LEXIT Railway deployment.')
        
        # First, test SMTP connection directly
        try:
            # Test the connection
            print(f"Testing SMTP connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            
            if settings.EMAIL_USE_SSL:
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            else:
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
                if settings.EMAIL_USE_TLS:
                    server.starttls()
            
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.quit()
            
            # If connection test passes, send the email
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            if result:
                return JsonResponse({'success': True, 'message': 'Email sent successfully!'})
            else:
                return JsonResponse({'success': False, 'error': 'Email sending failed - no error details'})
                
        except socket.timeout:
            return JsonResponse({'success': False, 'error': 'SMTP connection timeout - Railway may be blocking SMTP ports'})
        except socket.gaierror as e:
            return JsonResponse({'success': False, 'error': f'DNS resolution failed: {str(e)}'})
        except smtplib.SMTPAuthenticationError as e:
            return JsonResponse({'success': False, 'error': f'SMTP Authentication failed: {str(e)}'})
        except smtplib.SMTPConnectError as e:
            return JsonResponse({'success': False, 'error': f'SMTP Connection failed: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'SMTP test failed: {str(e)}'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'})