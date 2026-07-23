"""
Defines signal boards: curated, ordered collections of signals 
used for quick selection when logging events.
Depends only on 'signals'.

"""

from django.db import models
from django.conf import settings
from uuid import uuid7

class SignalBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boards',
    )
    name = models.CharField(max_length=100)

    signals = models.ManyToManyField(
        'signals.Signal',
        through='BoardSignal',
        related_name='boards',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_board_name_per_user'),
        ]

    def __str__(self):
        return self.name


class BoardSignal(models.Model):
    """Through model to control signal display order."""
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    board = models.ForeignKey(SignalBoard, on_delete=models.CASCADE, related_name='board_singnals')
    signal = models.ForeignKey('signals.Signal', on_delete=models.CASCADE, related_name='board_signal')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['board', 'signal'], name='unique_signal_per_board'),
        ]

    def __str__(self):
        return f"{self.signal.name} in {self.board.name}"
