"""Email helpers for registration confirmation and password reset."""

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

email_token_generator = PasswordResetTokenGenerator()


def uid_for_user(user) -> str:
    return urlsafe_base64_encode(force_bytes(user.pk))


def user_from_uid(uidb64):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def frontend_origin_for_user(user, request=None) -> str:
    """Build school site origin for email links."""
    scheme = 'https'
    if request is not None:
        scheme = 'https' if request.is_secure() else request.scheme
        # Prefer explicit frontend base when set
    base = getattr(settings, 'FRONTEND_BASE_URL', '').rstrip('/')
    if base:
        # If FRONTEND_BASE_URL is apex, prefix school slug when present
        if user.school_id and '://' in base:
            # e.g. https://balamukundam.com → https://{slug}.balamukundam.com
            # or https://test.balamukundam.com → https://{slug}.test.balamukundam.com
            proto, rest = base.split('://', 1)
            return f'{proto}://{user.school.slug}.{rest}'
        return base

    app_domain = getattr(settings, 'APP_DOMAIN', 'localhost')
    port = getattr(settings, 'FRONTEND_PORT', '')
    port_suffix = f':{port}' if port else ''
    if app_domain in {'localhost', '127.0.0.1'} and not port:
        port_suffix = ':8080'
    if user.school_id:
        return f'{scheme}://{user.school.slug}.{app_domain}{port_suffix}'
    return f'{scheme}://{app_domain}{port_suffix}'


def send_confirmation_email(user, request=None) -> None:
    uid = uid_for_user(user)
    token = email_token_generator.make_token(user)
    origin = frontend_origin_for_user(user, request)
    link = f'{origin}/confirm-email?uid={uid}&token={token}'
    subject = 'Confirm your email — Balamukundam Vidyalayam'
    message = (
        f'Hello {user.first_name or user.email},\n\n'
        f'Please confirm your email by opening this link:\n{link}\n\n'
        f'After confirmation, a school admin must activate your account before you can sign in.\n\n'
        f'If you did not register, ignore this email.\n'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, request=None) -> None:
    uid = uid_for_user(user)
    token = email_token_generator.make_token(user)
    origin = frontend_origin_for_user(user, request)
    link = f'{origin}/reset-password?uid={uid}&token={token}'
    subject = 'Reset your password — Balamukundam Vidyalayam'
    message = (
        f'Hello {user.first_name or user.email},\n\n'
        f'Reset your password using this link:\n{link}\n\n'
        f'If you did not request a reset, ignore this email.\n'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
