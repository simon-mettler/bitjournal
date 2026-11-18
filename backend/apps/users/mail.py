import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class MailError(Exception):
    """Raised when a mail could not be sent."""


def send_mail(to, subject, text, html=None):
    """Send a mail through the configured SMTP server."""
    if not settings.EMAIL_ENABLED:
        raise MailError('Email is not configured.')

    recipient = to
    if settings.EMAIL_CATCH_ALL:
        recipient = settings.EMAIL_CATCH_ALL
        subject = f'[to: {to}] {subject}'
        text = f'Original recipient: {to}\n\n{text}'
        if html:
            html = f'<p><em>Original recipient: {to}</em></p>{html}'
    elif settings.DEBUG:
        raise MailError('DEBUG is on and EMAIL_CATCH_ALL is not set: refusing to send.')

    message = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [recipient])
    if html:
        message.attach_alternative(html, 'text/html')
    try:
        message.send()
    except Exception as exc:
        logger.exception('Sending mail to %s failed', recipient)
        raise MailError('Sending the mail failed.') from exc


SITE_NAME = 'bitjournal'

SUBJECTS = {
    'test': f'{SITE_NAME} test mail',
    'password_reset': 'Reset your password',
    'email_change': 'Confirm your new email address',
    'password_changed': 'Your password was changed',
    'email_changed': 'Your email address was changed',
}


def send_templated_mail(to, template, context=None):
    """Render `users/email/<template>.txt/html` and sends mail."""
    context = {'site_name': SITE_NAME, **(context or {})}
    text = render_to_string(f'users/email/{template}.txt', context).strip()
    html = render_to_string(f'users/email/{template}.html', context)
    send_mail(to, SUBJECTS[template], text, html)


def notify(to, template, context=None):
    """Security notification."""
    if not settings.EMAIL_ENABLED:
        return
    try:
        send_templated_mail(to, template, context)
    except MailError:
        pass  # already logged
