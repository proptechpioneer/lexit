from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from urllib import request, error

# Direct Postmark test without Django's send_mail
@csrf_exempt
def direct_postmark_test(request):
    try:
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
        
        server_token = getattr(settings, 'POSTMARK_SERVER_TOKEN', None)
        if not server_token:
            return JsonResponse({'success': False, 'error': 'Postmark server token not found'})

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@lexit.tech')
        payload = {
            'From': from_email,
            'To': to_email,
            'Subject': f'Direct Postmark Test - LEXIT (from {from_email})',
            'TextBody': f'This is a direct Postmark API test from LEXIT platform using {from_email}!',
            'MessageStream': 'outbound',
        }

        req = request.Request(
            'https://api.postmarkapp.com/email',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Postmark-Server-Token': server_token,
            },
            method='POST',
        )

        with request.urlopen(req, timeout=getattr(settings, 'EMAIL_TIMEOUT', 30)) as response:
            response_body = response.read().decode('utf-8') if response else ''
            return JsonResponse({
                'success': 200 <= response.status < 300,
                'status_code': response.status,
                'message': 'Direct Postmark test completed',
                'from_email': from_email,
                'to_email': to_email,
                'postmark_server_token': 'Configured',
                'response_body': response_body,
            })
    except error.HTTPError as http_error:
        body = http_error.read().decode('utf-8') if hasattr(http_error, 'read') else ''
        return JsonResponse({
            'success': False,
            'error': str(http_error),
            'error_type': type(http_error).__name__,
            'status_code': http_error.code,
            'response_body': body,
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        })