"""
Defines tracker boards: curated, ordered collections of trackers 
used for quick selection when logging events.
Depends only on 'trackers'.

"""

from django.db import models
from django.conf import settings

class TrackerBoard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='boards',
    )
    name = models.CharField(max_length=100)

    trackers = models.ManyToManyField(
        'trackers.Tracker',
        through='BoardTracker',
        related_name='boards',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_board_name_per_user'),
        ]

    def __str__(self):
        return self.name


class BoardTracker(models.Model):
    """Through model to control tracker display order."""

    board = models.ForeignKey(TrackerBoard, on_delete=models.CASCADE, related_name='board_trackers')
    tracker = models.ForeignKey('trackers.Tracker', on_delete=models.CASCADE, related_name='board_tracker')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['board', 'tracker'], name='unique_tracker_per_board'),
        ]

    def __str__(self):
        return f"{self.tracker.name} in {self.board.name}"
