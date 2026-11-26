"""
Export and import of all of a user's data as one JSON.

Import assigns fresh ids. Ids in the file only link records to each other.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import DatabaseError, transaction

from apps.analytics.models import AnalyticsBoard, AnalyticsWidget
from apps.boards.models import BoardSignal, SignalBoard
from apps.events.models import Event, SignalEntry
from apps.signals.models import Signal, SignalCategory, SignalRangeConfig, SignalValueConfig

FORMAT = 'bitjournal-export'
VERSION = 4

SIGNAL_FIELDS = ('name', 'type', 'icon', 'color', 'summary_method', 'empty_days_as_zero', 'is_archived')
RANGE_FIELDS = ('min_value', 'max_value', 'min_label', 'max_label')
WIDGET_FIELDS = (
    'order', 'type', 'title', 'config', 'timeframe', 'period_start', 'days',
)
BATCH_SIZE = 1000


class InvalidExport(Exception):
    pass


def _fields(obj, names):
    return {name: getattr(obj, name) for name in names}


def _decimal(value):
    return None if value is None else str(value)


def _seconds(value):
    return None if value is None else value.total_seconds()


def export_user(user) -> dict:
    signals = user.signals.select_related('range_config', 'value_config')
    boards = user.boards.prefetch_related('board_signals')
    analytics_boards = user.analytics_boards.prefetch_related('widgets')
    events = user.events.prefetch_related('entries')

    def export_signal(signal):
        data = {
            'id': str(signal.id),
            'category': signal.category_id and str(signal.category_id),
            **_fields(signal, SIGNAL_FIELDS),
            'range': None,
            'value': None,
        }
        if hasattr(signal, 'range_config'):
            cfg = signal.range_config
            data['range'] = {
                **_fields(cfg, RANGE_FIELDS),
                'min_value': _decimal(cfg.min_value),
                'max_value': _decimal(cfg.max_value),
            }
        if hasattr(signal, 'value_config'):
            data['value'] = {'unit': signal.value_config.unit}
        return data

    def export_widget(widget):
        return {
            **_fields(widget, WIDGET_FIELDS),
            'config': widget.settings,
            'signal': str(widget.signal_id),
            'period_start': widget.period_start and widget.period_start.isoformat(),
        }

    return {
        'format': FORMAT,
        'version': VERSION,
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'categories': [
            {'id': str(c.id), 'name': c.name, 'icon': c.icon, 'color': c.color}
            for c in user.signal_categories.all()
        ],
        'signals': [export_signal(s) for s in signals],
        'boards': [
            {
                'name': b.name,
                'order': b.order,
                'signals': [str(bs.signal_id) for bs in b.board_signals.all()],
            }
            for b in boards
        ],
        'analytics_boards': [
            {
                'name': b.name,
                'order': b.order,
                'widgets': [export_widget(w) for w in b.widgets.all()],
            }
            for b in analytics_boards
        ],
        'events': [
            {
                'occurred_at': e.occurred_at.isoformat(),
                'note': e.note,
                'entries': [
                    {
                        'signal': str(entry.signal_id),
                        'value': _decimal(entry.value),
                        'duration': _seconds(entry.duration),
                    }
                    for entry in e.entries.all()
                ],
            }
            for e in events.iterator(chunk_size=BATCH_SIZE)
        ],
    }


def _save(obj):
    obj.full_clean()
    obj.save()
    return obj


def _aware(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError('datetime without timezone')
    return parsed


def _import(user, data):
    if data['format'] != FORMAT or data['version'] != VERSION:
        raise InvalidExport('Not a bitjournal export or unsupported version.')

    # Cascades remove entries, board links and widgets too.
    user.signals.all().delete()
    user.signal_categories.all().delete()
    user.boards.all().delete()
    user.analytics_boards.all().delete()
    user.events.all().delete()

    categories = {
        c['id']: _save(SignalCategory(user=user, name=c['name'], icon=c['icon'], color=c['color']))
        for c in data['categories']
    }

    signals = {}
    for s in data['signals']:
        signal = Signal(
            user=user,
            category=s['category'] and categories[s['category']],
            **{name: s[name] for name in SIGNAL_FIELDS},
        )
        # Configs are attached before saving so Signal.clean() sees them.
        if s['range']:
            SignalRangeConfig(
                signal=signal,
                **{name: s['range'][name] for name in RANGE_FIELDS},
            )
        if s['value']:
            SignalValueConfig(signal=signal, unit=s['value']['unit'])
        _save(signal)
        for config in ('range_config', 'value_config'):
            if hasattr(signal, config):
                _save(getattr(signal, config))
        signals[s['id']] = signal

    for b in data['boards']:
        board = _save(SignalBoard(user=user, name=b['name'], order=b['order']))
        for order, signal_id in enumerate(b['signals']):
            _save(BoardSignal(board=board, signal=signals[signal_id], order=order))

    for b in data['analytics_boards']:
        board = _save(AnalyticsBoard(user=user, name=b['name'], order=b['order']))
        for w in b['widgets']:
            _save(AnalyticsWidget(
                board=board,
                signal=signals[w['signal']],
                **{name: w[name] for name in WIDGET_FIELDS if name != 'period_start'},
                period_start=w['period_start'] and date.fromisoformat(w['period_start']),
            ))

    events, entries = [], []
    for e in data['events']:
        event = Event(user=user, occurred_at=_aware(e['occurred_at']), note=e['note'])
        events.append(event)
        for entry in e['entries']:
            entry = SignalEntry(
                event=event,
                signal=signals[entry['signal']],
                value=None if entry['value'] is None else Decimal(entry['value']),
                duration=None if entry['duration'] is None else timedelta(seconds=entry['duration']),
            )
            entry.clean()
            entries.append(entry)
    Event.objects.bulk_create(events, batch_size=BATCH_SIZE)
    SignalEntry.objects.bulk_create(entries, batch_size=BATCH_SIZE)


def import_user(user, data):
    """Replace all of the user's data with the export. All or nothing."""
    try:
        with transaction.atomic():
            _import(user, data)
    except (KeyError, TypeError, AttributeError, ValueError, InvalidOperation,
            ValidationError, DatabaseError) as e:
        raise InvalidExport('The file is not a valid bitjournal export.') from e
