"""
Example email usage in Django views

This file demonstrates how to use the email backend configuration
in your LEXIT application for various email functionalities.
"""

from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

# Example 1: Simple email sending function
def send_welcome_email(user_email, user_name):
    """Send a welcome email to new users"""
    subject = 'Welcome to LEXIT!'
    message = f'''
    Hi {user_name},

    Welcome to LEXIT - your property investment companion!

    We're excited to have you on board. You can now:
    • Upload your properties
    • Track rental income and expenses
    • Calculate capital gains tax
    • Get AI-powered insights

    Get started by adding your first property: https://lexit.tech/upload-property/

    Best regards,
    The LEXIT Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False

# Example 2: Property notification email
def send_property_update_notification(property_obj, changes):
    """Send notification when property details are updated"""
    subject = f'Property Updated: {property_obj.property_name}'
    message = f'''
    Hi {property_obj.owner.first_name or property_obj.owner.username},

    Your property "{property_obj.property_name}" has been updated.

    Changes made:
    {chr(10).join([f"• {change}" for change in changes])}

    View your property: https://lexit.tech/property/{property_obj.slug}/

    Best regards,
    The LEXIT Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[property_obj.owner.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send property update email: {e}")
        return False

# Example 3: Contact form email
def send_contact_form_email(name, email, subject, message):
    """Send contact form submission to admin"""
    email_subject = f'Contact Form: {subject}'
    email_message = f'''
    New contact form submission:

    Name: {name}
    Email: {email}
    Subject: {subject}

    Message:
    {message}

    ---
    This email was sent from the LEXIT contact form.
    '''
    
    try:
        send_mail(
            subject=email_subject,
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['info@lexit.tech'],  # Admin email
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send contact form email: {e}")
        return False

# Example 4: HTML email with attachments
def send_monthly_report_email(user, report_data):
    """Send monthly property report via email"""
    subject = f'Monthly Property Report - {report_data["month"]} {report_data["year"]}'
    
    html_message = f'''
    <html>
    <body>
        <h2>Monthly Property Report</h2>
        <p>Hi {user.first_name or user.username},</p>
        
        <p>Here's your property performance report for {report_data["month"]} {report_data["year"]}:</p>
        
        <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Rental Income</td>
                <td>£{report_data["total_income"]}</td>
            </tr>
            <tr>
                <td>Total Expenses</td>
                <td>£{report_data["total_expenses"]}</td>
            </tr>
            <tr>
                <td>Net Profit</td>
                <td>£{report_data["net_profit"]}</td>
            </tr>
        </table>
        
        <p><a href="https://lexit.tech/dashboard/">View Full Dashboard</a></p>
        
        <p>Best regards,<br>The LEXIT Team</p>
    </body>
    </html>
    '''
    
    try:
        msg = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        return True
    except Exception as e:
        print(f"Failed to send monthly report email: {e}")
        return False

# Example 5: Password reset email (if implementing custom auth)
def send_password_reset_email(user, reset_token):
    """Send password reset email"""
    subject = 'Reset Your LEXIT Password'
    message = f'''
    Hi {user.first_name or user.username},

    You requested a password reset for your LEXIT account.

    Click the link below to reset your password:
    https://lexit.tech/reset-password/{reset_token}/

    This link will expire in 24 hours.

    If you didn't request this, please ignore this email.

    Best regards,
    The LEXIT Team
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False

# Example usage in a view
@login_required
def test_email_view(request):
    """Test view to send an email - for development only"""
    if request.method == 'POST':
        success = send_welcome_email(
            request.user.email,
            request.user.first_name or request.user.username
        )
        
        if success:
            messages.success(request, 'Test email sent successfully!')
        else:
            messages.error(request, 'Failed to send test email.')
    
    return redirect('user_home:dashboard')