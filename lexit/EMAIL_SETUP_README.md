# Email Backend Configuration for LEXIT

## What Does Email Backend Do?

The email backend in Django handles all email functionality for your LEXIT application. It enables:

### 🔧 Core Functions:
- **Send Emails**: Welcome messages, notifications, password resets
- **Email Authentication**: SMTP server connection and credentials
- **Error Handling**: Manages failed deliveries and retries
- **Multiple Environments**: Different configs for development/production

### 📧 Use Cases in LEXIT:
- **User Registration**: Welcome emails and account verification
- **Property Notifications**: Updates on property changes
- **Financial Reports**: Monthly rental income summaries
- **Contact Forms**: User inquiries to administrators
- **Password Reset**: Secure password recovery links
- **Marketing**: Property recommendations and newsletters

## 🚀 Quick Setup

### 1. Current Configuration (settings.py)

✅ **Development Mode**: Emails print to console (no setup needed)
✅ **Production Mode**: Uses SMTP (requires email provider setup)

### 2. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# For Gmail with lexit.tech domain
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=info@lexit.tech
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=info@lexit.tech
```

### 3. Email Provider Setup

#### Gmail Setup:
1. Enable 2-factor authentication
2. Generate App Password: Google Account > Security > App passwords
3. Use App Password in `EMAIL_HOST_PASSWORD`

#### SendGrid Setup:
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

#### Other Providers:
- **Outlook**: `smtp-mail.outlook.com:587`
- **Amazon SES**: `email-smtp.region.amazonaws.com:587`
- **Mailgun**: `smtp.mailgun.org:587`

## 🧪 Testing

### Test Email Configuration:
```bash
python manage.py test_email your-email@example.com
```

### Development Mode:
Emails are printed to console - no real emails sent.

### Production Mode:
Real emails are sent via configured SMTP server.

## 💻 Usage Examples

### Simple Email:
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Welcome to LEXIT!',
    message='Thanks for joining our platform.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['user@example.com'],
)
```

### HTML Email:
```python
from django.core.mail import EmailMessage

msg = EmailMessage(
    subject='Property Report',
    body='<h1>Monthly Report</h1><p>Your properties performed well!</p>',
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['user@example.com']
)
msg.content_subtype = "html"
msg.send()
```

## 🔒 Security Considerations

### Email Credentials:
- ✅ Store in environment variables (not in code)
- ✅ Use App Passwords instead of regular passwords
- ✅ Enable 2FA on email accounts
- ✅ Use dedicated email service for production

### Rate Limiting:
- Gmail: 500 emails/day for free accounts
- SendGrid: 100 emails/day free tier
- Consider upgrading for higher volume

## 🚨 Common Issues

### "SMTPAuthenticationError":
- Check email/password credentials
- Verify App Password is generated
- Ensure "Less secure app access" is enabled (Gmail)

### "Connection Refused":
- Check EMAIL_HOST and EMAIL_PORT
- Verify firewall/antivirus isn't blocking SMTP

### "Email Not Received":
- Check spam/junk folder
- Verify recipient email address
- Check email provider's sending limits

## 📁 Implementation Files

### Files Added/Modified:
- `lexit/settings.py` - Email backend configuration
- `lexit/.env.example` - Environment variables template
- `user_home/email_examples.py` - Usage examples
- `user_home/management/commands/test_email.py` - Test command

### Next Steps:
1. Copy `.env.example` to `.env`
2. Configure your email provider credentials
3. Set `ENVIRONMENT=production` for live emails
4. Test with `python manage.py test_email your-email@example.com`
5. Integrate email functions into your views

## 🎯 Ready to Use

The email backend is now configured and ready to use in your LEXIT application!

- ✅ Development: Console output (testing)
- ✅ Production: SMTP email delivery
- ✅ Test command available
- ✅ Example code provided
- ✅ Security best practices included