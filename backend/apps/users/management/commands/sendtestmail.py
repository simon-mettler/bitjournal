from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.users.mail import MailError, send_templated_mail


class Command(BaseCommand):
    help = 'Send a test mail through the configured provider (honors EMAIL_CATCH_ALL).'

    def add_arguments(self, parser):
        parser.add_argument('to', help='Recipient (replaced by EMAIL_CATCH_ALL when set)')

    def handle(self, *args, **options):
        if not settings.EMAIL_ENABLED:
            raise CommandError('Email is disabled: set RESEND_API_KEY and DEFAULT_FROM_EMAIL.')
        try:
            send_templated_mail(options['to'], 'test')
        except MailError as exc:
            raise CommandError(str(exc)) from exc
        target = settings.EMAIL_CATCH_ALL or options['to']
        self.stdout.write(self.style.SUCCESS(f'Test mail sent to {target}.'))
