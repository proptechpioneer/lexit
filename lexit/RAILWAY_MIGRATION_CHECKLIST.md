# Railway Migration Checklist for LEXIT

## ✅ Pre-Migration Setup

### Domain & Email Setup:
- [ ] Set up Google Workspace for lexit.tech OR configure Gmail forwarding
- [ ] Create/configure info@lexit.tech email address  
- [ ] Generate Gmail App Password for SMTP
- [ ] Test email configuration locally

### Code Updates (COMPLETED ✅):
- [x] Updated DEFAULT_FROM_EMAIL to info@lexit.tech
- [x] Updated SERVER_EMAIL to info@lexit.tech  
- [x] Updated ALLOWED_HOSTS for lexit.tech domain
- [x] Updated email examples with production URLs
- [x] Created Railway deployment guide

## 🚀 Migration Steps

### 1. Railway Project Setup:
- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Create new project from GitHub repo

### 2. Environment Variables:
```bash
ENVIRONMENT=production
SECRET_KEY=[generate-new-secret-key]
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=info@lexit.tech
EMAIL_HOST_PASSWORD=[gmail-app-password]
DEFAULT_FROM_EMAIL=info@lexit.tech
SERVER_EMAIL=info@lexit.tech
```

### 3. Domain Configuration:
- [ ] Add lexit.tech to Railway domains
- [ ] Add www.lexit.tech subdomain
- [ ] Configure DNS CNAME records
- [ ] Wait for SSL certificate provisioning

### 4. Database Migration:
- [ ] Railway auto-provisions PostgreSQL
- [ ] Migrations run automatically on deploy
- [ ] Verify data integrity
- [ ] Create admin superuser

### 5. Testing:
- [ ] Test email sending: `railway run python manage.py test_email your-email@gmail.com`
- [ ] Test file uploads work
- [ ] Test user registration/login
- [ ] Test property upload functionality
- [ ] Test admin panel access

## 📧 Email Provider Options

### Option A: Google Workspace (Recommended)
- Professional email with lexit.tech domain
- $6/month per user
- Full Gmail functionality
- Professional appearance

### Option B: Gmail with Custom Domain
- Use existing Gmail account
- Set up "Send mail as" info@lexit.tech
- Configure email forwarding
- Free option

## 🔧 Post-Migration Tasks

### Immediate:
- [ ] Test all core functionality
- [ ] Update any hardcoded URLs
- [ ] Monitor Railway logs for errors
- [ ] Set up monitoring/alerts

### Within 24 hours:
- [ ] Update DNS TTL if needed
- [ ] Test email deliverability
- [ ] Backup production database
- [ ] Update documentation

### Clean-up:
- [ ] Remove Render.com deployment
- [ ] Update any external integrations
- [ ] Cancel Render.com subscription

## 🎯 Success Criteria

- ✅ Site accessible at https://lexit.tech
- ✅ SSL certificate active and valid
- ✅ Emails sending from info@lexit.tech
- ✅ Database migrated successfully
- ✅ All features working correctly
- ✅ Performance equal or better than Render

## 📞 Support Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: Active community support
- **Django Deployment**: Standard Django production practices apply

---

**Current Status**: Code ready for Railway deployment ✅
**Next Step**: Set up Railway project and configure environment variables