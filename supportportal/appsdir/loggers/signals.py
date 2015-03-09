from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import AuthenticationLogger

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    AuthenticationLogger(ip=get_client_ip(request), user_agent=request.META.get('HTTP_USER_AGENT', ''), request_method=request.method, user=user, action="LOGIN").save()

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    AuthenticationLogger(ip=get_client_ip(request), user_agent=request.META.get('HTTP_USER_AGENT', ''), request_method=request.method, user=user, action="LOGOUT").save()