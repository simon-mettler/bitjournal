from django.dispatch import Signal

# Sent right before a user and all their data are deleted, inside the deletion
# transaction.
account_deleting = Signal()
