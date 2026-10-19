from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


def blacklist_all_tokens(user):
    """Log out everywhere: revoke every refresh token from user."""
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)
