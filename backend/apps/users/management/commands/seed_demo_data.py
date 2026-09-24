import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.boards.models import BoardSignal, SignalBoard
from apps.events.models import Event, SignalEntry
from apps.signals.models import (
    Signal,
    SignalRangeConfig,
    SignalType,
    SignalValueConfig,
    SummaryMethod,
)

DEMO_PASSWORD = 'Demo12345!'

TALLY = SignalType.TALLY
RANGE = SignalType.RANGE
VALUE = SignalType.VALUE
DURATION = SignalType.DURATION
AVERAGE = SummaryMethod.AVERAGE
SUM = SummaryMethod.SUM

NOTE_POOL = [
    'Feeling good today.',
    'Tough one.',
    'Back on track.',
    'Solid session.',
    'Slow start.',
    'Great progress!',
    'Long day.',
    'Nice and easy.',
]


def clamp(value, lo=None, hi=None):
    if lo is not None:
        value = max(value, lo)
    if hi is not None:
        value = min(value, hi)
    return value


def gauss(mean, sigma, lo=None, hi=None):
    return clamp(random.gauss(mean, sigma), lo, hi)


def half(value):
    return round(value * 2) / 2


def dec(value, places=2):
    return Decimal(str(round(value, places)))


PERSONAS = [
    {
        'username': 'demo_fitness',
        'email': 'demo_fitness@bitjournal.demo',
        'first_name': 'Alex',
        'last_name': 'Fischer',
        'tz': 'Europe/Zurich',
        'signals': [
            {'key': 'sleep', 'name': 'Sleep', 'type': DURATION, 'icon': 'BedDouble',
             'color': '#6366f1', 'summary': AVERAGE},
            {'key': 'weight', 'name': 'Weight', 'type': VALUE, 'unit': 'kg', 'icon': 'Target',
             'color': '#0891b2', 'summary': AVERAGE},
            {'key': 'mood', 'name': 'Mood', 'type': RANGE, 'min': 1, 'max': 10,
             'min_label': 'Low', 'max_label': 'Great', 'icon': 'Smile',
             'color': '#f59e0b', 'summary': AVERAGE},
            {'key': 'steps', 'name': 'Steps', 'type': VALUE, 'unit': 'steps', 'icon': 'Bike',
             'color': '#10b981', 'summary': AVERAGE},
            {'key': 'workout', 'name': 'Workout', 'type': DURATION, 'icon': 'Dumbbell',
             'color': '#ef4444', 'summary': SUM},
            {'key': 'water', 'name': 'Water', 'type': TALLY, 'icon': 'Droplet',
             'color': '#0ea5e9', 'summary': SUM},
        ],
        'boards': [
            {'name': 'Morning Check-in', 'signals': ['sleep', 'mood', 'weight']},
            {'name': 'Training & Recovery', 'signals': ['workout', 'steps', 'water']},
        ],
        'moments': [
            {'hour_range': (6, 8.5), 'entries': [
                {'signal': 'sleep', 'weekday_p': 0.85, 'weekend_p': 0.8,
                 'value': lambda d, w: gauss(430 + (25 if w else 0), 35, 240, 600)},
                {'signal': 'mood', 'weekday_p': 0.55, 'weekend_p': 0.6,
                 'value': lambda d, w: half(gauss(6.3 + 0.003 * d, 1.3, 1, 10))},
                {'signal': 'weight', 'weekday_p': 0.4, 'weekend_p': 0.25,
                 'value': lambda d, w: gauss(78 - 0.015 * d, 0.35, 50, None)},
            ]},
            {'hour_range': (17.5, 22), 'entries': [
                {'signal': 'workout', 'weekday_p': 0.35, 'weekend_p': 0.65,
                 'value': lambda d, w: gauss(40 + (20 if w else 0), 15, 10, 120)},
                {'signal': 'steps', 'weekday_p': 0.8, 'weekend_p': 0.85,
                 'value': lambda d, w: gauss(7000 + (1400 if w else 0), 2200, 500, 25000)},
                {'signal': 'water', 'weekday_p': 0.7, 'weekend_p': 0.6,
                 'value': lambda d, w: random.randint(1, 4)},
            ]},
        ],
    },
    {
        'username': 'demo_focus',
        'email': 'demo_focus@bitjournal.demo',
        'first_name': 'Jordan',
        'last_name': 'Lee',
        'tz': 'America/New_York',
        'signals': [
            {'key': 'deep_work', 'name': 'Deep work', 'type': DURATION, 'icon': 'Briefcase',
             'color': '#1d4ed8', 'summary': SUM},
            {'key': 'pomodoros', 'name': 'Pomodoros', 'type': TALLY, 'icon': 'Target',
             'color': '#f97316', 'summary': SUM},
            {'key': 'coffee', 'name': 'Coffee', 'type': TALLY, 'icon': 'Coffee',
             'color': '#92400e', 'summary': SUM},
            {'key': 'focus', 'name': 'Focus level', 'type': RANGE, 'min': 1, 'max': 10,
             'min_label': 'Distracted', 'max_label': 'Locked in', 'icon': 'Brain',
             'color': '#7c3aed', 'summary': AVERAGE},
            {'key': 'reading', 'name': 'Reading', 'type': DURATION, 'icon': 'Book',
             'color': '#059669', 'summary': SUM},
            {'key': 'screen_free', 'name': 'Screen-free time', 'type': DURATION, 'icon': 'Leaf',
             'color': '#16a34a', 'summary': SUM},
        ],
        'boards': [
            {'name': 'Work Day', 'signals': ['deep_work', 'pomodoros', 'coffee', 'focus']},
            {'name': 'Wind Down', 'signals': ['reading', 'screen_free']},
        ],
        'moments': [
            {'hour_range': (9, 17), 'entries': [
                {'signal': 'deep_work', 'weekday_p': 0.88, 'weekend_p': 0.15,
                 'value': lambda d, w: gauss(60, 30, 0, 150) if w else gauss(185 + 0.05 * d, 45, 20, 420)},
                {'signal': 'pomodoros', 'weekday_p': 0.8, 'weekend_p': 0.1,
                 'value': lambda d, w: random.randint(1, 3) if w else random.randint(3, 9)},
                {'signal': 'coffee', 'weekday_p': 0.85, 'weekend_p': 0.4,
                 'value': lambda d, w: random.randint(0, 2) if w else random.randint(1, 3)},
                {'signal': 'focus', 'weekday_p': 0.8, 'weekend_p': 0.3,
                 'value': lambda d, w: half(gauss(5.5, 1.6, 1, 10)) if w else half(gauss(6.4 + 0.002 * d, 1.4, 1, 10))},
            ]},
            {'hour_range': (19, 22.5), 'entries': [
                {'signal': 'reading', 'weekday_p': 0.4, 'weekend_p': 0.65,
                 'value': lambda d, w: gauss(45, 20, 10, 120) if w else gauss(20, 10, 5, 60)},
                {'signal': 'screen_free', 'weekday_p': 0.3, 'weekend_p': 0.45,
                 'value': lambda d, w: gauss(40, 18, 10, 150)},
            ]},
        ],
    },
    {
        'username': 'demo_wellness',
        'email': 'demo_wellness@bitjournal.demo',
        'first_name': 'Sam',
        'last_name': 'Ortiz',
        'tz': 'Australia/Sydney',
        'signals': [
            {'key': 'meditation', 'name': 'Meditation', 'type': DURATION, 'icon': 'Leaf',
             'color': '#0d9488', 'summary': SUM},
            {'key': 'sleep', 'name': 'Sleep', 'type': DURATION, 'icon': 'Moon',
             'color': '#4338ca', 'summary': AVERAGE},
            {'key': 'mood', 'name': 'Mood', 'type': RANGE, 'min': 1, 'max': 10,
             'min_label': 'Rough', 'max_label': 'Wonderful', 'icon': 'Smile',
             'color': '#eab308', 'summary': AVERAGE},
            {'key': 'gratitude', 'name': 'Gratitude notes', 'type': TALLY, 'icon': 'Star',
             'color': '#f43f5e', 'summary': SUM},
            {'key': 'journaling', 'name': 'Journaling', 'type': DURATION, 'icon': 'Pencil',
             'color': '#0369a1', 'summary': SUM},
            {'key': 'water', 'name': 'Water', 'type': TALLY, 'icon': 'Droplet',
             'color': '#0ea5e9', 'summary': SUM},
        ],
        'boards': [
            {'name': 'Daily Reflection', 'signals': ['mood', 'gratitude', 'journaling']},
            {'name': 'Sleep & Calm', 'signals': ['sleep', 'meditation', 'water']},
        ],
        'moments': [
            {'hour_range': (6, 8), 'entries': [
                {'signal': 'meditation', 'weekday_p': 0.55, 'weekend_p': 0.65,
                 'value': lambda d, w: gauss(15, 8, 5, 60)},
                {'signal': 'sleep', 'weekday_p': 0.85, 'weekend_p': 0.8,
                 'value': lambda d, w: gauss(415 + (20 if w else 0), 40, 240, 600)},
                {'signal': 'mood', 'weekday_p': 0.45, 'weekend_p': 0.5,
                 'value': lambda d, w: half(gauss(6.6 + 0.0025 * d, 1.2, 1, 10))},
            ]},
            {'hour_range': (20, 23), 'entries': [
                {'signal': 'gratitude', 'weekday_p': 0.5, 'weekend_p': 0.55,
                 'value': lambda d, w: random.randint(1, 3)},
                {'signal': 'journaling', 'weekday_p': 0.4, 'weekend_p': 0.45,
                 'value': lambda d, w: gauss(12, 6, 3, 45)},
                {'signal': 'water', 'weekday_p': 0.65, 'weekend_p': 0.55,
                 'value': lambda d, w: random.randint(1, 4)},
                {'signal': 'mood', 'weekday_p': 0.45, 'weekend_p': 0.5,
                 'value': lambda d, w: half(gauss(6.6 + 0.0025 * d, 1.2, 1, 10))},
            ]},
        ],
    },
    {
        'username': 'demo_habits',
        'email': 'demo_habits@bitjournal.demo',
        'first_name': 'Riley',
        'last_name': 'Nguyen',
        'tz': 'America/Los_Angeles',
        'signals': [
            {'key': 'steps', 'name': 'Steps', 'type': VALUE, 'unit': 'steps', 'icon': 'Bike',
             'color': '#10b981', 'summary': AVERAGE},
            {'key': 'coffee', 'name': 'Coffee', 'type': TALLY, 'icon': 'Coffee',
             'color': '#92400e', 'summary': SUM},
            {'key': 'reading', 'name': 'Reading', 'type': DURATION, 'icon': 'Book',
             'color': '#059669', 'summary': SUM},
            {'key': 'mood', 'name': 'Mood', 'type': RANGE, 'min': 1, 'max': 10,
             'min_label': 'Meh', 'max_label': 'Amazing', 'icon': 'Smile',
             'color': '#f59e0b', 'summary': AVERAGE},
            {'key': 'alcohol', 'name': 'Drinks', 'type': TALLY, 'icon': 'Circle',
             'color': '#b91c1c', 'summary': SUM},
            {'key': 'spending', 'name': 'Spending', 'type': VALUE, 'unit': '$', 'icon': 'Wallet',
             'color': '#ca8a04', 'summary': SUM},
        ],
        'boards': [
            {'name': 'Daily', 'signals': ['mood', 'coffee', 'steps']},
            {'name': 'Evening', 'signals': ['reading', 'alcohol', 'spending']},
        ],
        'moments': [
            {'hour_range': (7, 10), 'entries': [
                {'signal': 'coffee', 'weekday_p': 0.8, 'weekend_p': 0.5,
                 'value': lambda d, w: random.randint(0, 2) if w else random.randint(1, 3)},
                {'signal': 'mood', 'weekday_p': 0.55, 'weekend_p': 0.6,
                 'value': lambda d, w: half(gauss(6.0 + 0.002 * d, 1.5, 1, 10))},
            ]},
            {'hour_range': (18, 23), 'entries': [
                {'signal': 'steps', 'weekday_p': 0.7, 'weekend_p': 0.75,
                 'value': lambda d, w: gauss(6500 + (1200 if w else 0), 2400, 500, 22000)},
                {'signal': 'reading', 'weekday_p': 0.35, 'weekend_p': 0.5,
                 'value': lambda d, w: gauss(20, 12, 5, 80)},
                {'signal': 'alcohol', 'weekday_p': 0.1, 'weekend_p': 0.5,
                 'value': lambda d, w: random.randint(1, 4)},
                {'signal': 'spending', 'weekday_p': 0.25, 'weekend_p': 0.35,
                 'value': lambda d, w: gauss(25, 20, 0, 200)},
            ]},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed demo accounts with realistic signals, boards and events for local development.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete existing demo accounts (and their data) before seeding.',
        )
        parser.add_argument(
            '--days', type=int, default=300,
            help='Number of days of event history to generate per account (default: 300).',
        )
        parser.add_argument(
            '--seed', type=int, default=None,
            help='Random seed for reproducible output (default: non-deterministic).',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('seed_demo_data can only be run with DEBUG=True (local/dev only).')

        if options['seed'] is not None:
            random.seed(options['seed'])

        days = options['days']
        User = get_user_model()
        usernames = [persona['username'] for persona in PERSONAS]

        if options['flush']:
            deleted, _ = User.objects.filter(username__in=usernames).delete()
            self.stdout.write(f'Removed {deleted} existing demo objects (cascaded).')

        existing = User.objects.filter(username__in=usernames)
        if existing.exists():
            names = ', '.join(existing.values_list('username', flat=True))
            raise CommandError(f'Demo accounts already exist ({names}). Re-run with --flush to replace them.')

        today = date.today()
        totals = {'signals': 0, 'boards': 0, 'events': 0, 'entries': 0}

        for persona in PERSONAS:
            with transaction.atomic():
                user = self._create_user(User, persona)
                signals = self._create_signals(user, persona['signals'])
                boards = self._create_boards(user, persona['boards'], signals)
                events, entries = self._create_events(user, persona, signals, today, days)

            totals['signals'] += len(signals)
            totals['boards'] += len(boards)
            totals['events'] += events
            totals['entries'] += entries

            self.stdout.write(self.style.SUCCESS(
                f"{persona['username']}: {len(signals)} signals, {len(boards)} boards, "
                f"{events} events, {entries} entries"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {len(PERSONAS)} accounts, {totals['signals']} signals, {totals['boards']} boards, "
            f"{totals['events']} events, {totals['entries']} entries."
        ))
        self.stdout.write(f'Password for every demo account: {DEMO_PASSWORD}')
        for persona in PERSONAS:
            self.stdout.write(f"  {persona['email']}")

    def _create_user(self, User, persona):
        return User.objects.create_user(
            username=persona['username'],
            email=persona['email'],
            password=DEMO_PASSWORD,
            first_name=persona['first_name'],
            last_name=persona['last_name'],
        )

    def _create_signals(self, user, signal_defs):
        signals = {}
        for s in signal_defs:
            signal = Signal.objects.create(
                user=user,
                name=s['name'],
                type=s['type'],
                icon=s['icon'],
                color=s['color'],
                summary_method=s['summary'],
            )
            if s['type'] == VALUE:
                SignalValueConfig.objects.create(signal=signal, unit=s['unit'])
            elif s['type'] == RANGE:
                SignalRangeConfig.objects.create(
                    signal=signal,
                    min_value=s['min'],
                    max_value=s['max'],
                    min_label=s.get('min_label', ''),
                    max_label=s.get('max_label', ''),
                )
            signals[s['key']] = signal
        return signals

    def _create_boards(self, user, board_defs, signals):
        boards = []
        for order, b in enumerate(board_defs):
            board = SignalBoard.objects.create(user=user, name=b['name'], order=order)
            for s_order, key in enumerate(b['signals']):
                BoardSignal.objects.create(board=board, signal=signals[key], order=s_order)
            boards.append(board)
        return boards

    def _create_events(self, user, persona, signals, today, days):
        tz = ZoneInfo(persona['tz'])
        event_count = 0
        entry_count = 0

        for day_idx in range(days):
            day_date = today - timedelta(days=days - day_idx)
            is_weekend = day_date.weekday() >= 5

            for moment in persona['moments']:
                hits = [
                    e for e in moment['entries']
                    if random.random() < (e['weekend_p'] if is_weekend else e['weekday_p'])
                ]
                if not hits:
                    continue

                hour = random.uniform(*moment['hour_range'])
                occurred_at = datetime(
                    day_date.year, day_date.month, day_date.day,
                    int(hour), int((hour % 1) * 60),
                    tzinfo=tz,
                )
                note = random.choice(NOTE_POOL) if random.random() < 0.12 else ''
                event = Event.objects.create(user=user, occurred_at=occurred_at, note=note)

                for e in hits:
                    signal = signals[e['signal']]
                    raw = e['value'](day_idx, is_weekend)
                    if signal.type == DURATION:
                        SignalEntry.objects.create(
                            event=event, signal=signal, duration=timedelta(minutes=round(raw)),
                        )
                    else:
                        SignalEntry.objects.create(event=event, signal=signal, value=dec(raw))
                    entry_count += 1

                event_count += 1

        return event_count, entry_count
