class ReferralCodeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        referral_code = (request.GET.get('ref') or '').strip().upper()
        if referral_code:
            request.session['referral_code'] = referral_code
        return self.get_response(request)
