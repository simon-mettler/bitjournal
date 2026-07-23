from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid7

class BitjournalUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
