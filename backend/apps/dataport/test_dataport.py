import json
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.analytics.models import AnalyticsBoard, AnalyticsWidget
from apps.boards.models import BoardSignal, SignalBoard
from apps.events.models import Event, SignalEntry
from apps.signals.models import Signal, SignalCategory, SignalRangeConfig, SignalType, SignalValueConfig

from .services import InvalidExport, export_user, import_user


@pytest.fixture
def populated(user):
    category = SignalCategory.objects.create(user=user, name='Health', color='#aabbcc')
    mood = Signal.objects.create(user=user, name='Mood', type=SignalType.RANGE, category=category)
    SignalRangeConfig.objects.create(signal=mood, min_value=1, max_value=5)
    weight = Signal.objects.create(user=user, name='Weight', type=SignalType.VALUE)
    SignalValueConfig.objects.create(signal=weight, unit='kg')
    run = Signal.objects.create(user=user, name='Run', type=SignalType.DURATION)

    board = SignalBoard.objects.create(user=user, name='Morning', order=1)
    for order, signal in enumerate([run, mood]):
        BoardSignal.objects.create(board=board, signal=signal, order=order)

    dashboard = AnalyticsBoard.objects.create(user=user, name='Overview')
    AnalyticsWidget.objects.create(
        board=dashboard, signal=mood, title='Mood', timeframe='last_days', days=7,
    )

    event = Event.objects.create(
        user=user, occurred_at=datetime(2026, 11, 2, 8, tzinfo=timezone.utc), note='hi',
    )
    SignalEntry.objects.create(event=event, signal=mood, value=Decimal('4'))
    SignalEntry.objects.create(event=event, signal=run, duration=timedelta(0))
    return user


def normalize(data):
    """Export minus the fields that legitimately differ (timestamp)."""
    return {k: v for k, v in data.items() if k != 'exported_at'}


def without_ids(data):
    """Ids are regenerated on import: replace them by the position they appear at."""
    text = json.dumps({k: v for k, v in data.items() if k != 'exported_at'})
    ids = dict.fromkeys(re.findall(r'"([0-9a-f]{8}-[0-9a-f-]{27})"', text))
    for n, uuid in enumerate(ids):
        text = text.replace(uuid, f'id{n}')
    return text


def test_round_trip_into_other_user(populated):
    other = get_user_model().objects.create_user(email='b@example.com', password='x')
    exported = export_user(populated)
    import_user(other, json.loads(json.dumps(exported)))
    assert without_ids(export_user(other)) == without_ids(exported)
    assert not set(other.signals.values_list('id', flat=True)) & set(
        populated.signals.values_list('id', flat=True))
    assert populated.signals.count() == 3  # source untouched


def test_import_purges_existing_data(populated):
    exported = export_user(populated)
    Signal.objects.create(user=populated, name='Extra', type=SignalType.TALLY)
    import_user(populated, exported)
    assert sorted(populated.signals.values_list('name', flat=True)) == ['Mood', 'Run', 'Weight']
    assert populated.events.count() == 1


def test_invalid_import_changes_nothing(populated):
    exported = export_user(populated)
    exported['events'][0]['entries'][0]['value'] = '99'  # outside the range 1-5
    with pytest.raises(InvalidExport):
        import_user(populated, exported)
    assert populated.signals.count() == 3
    assert SignalEntry.objects.filter(event__user=populated).count() == 2


@pytest.mark.parametrize('version', [1, 3])
def test_rejects_other_versions(populated, version):
    exported = export_user(populated) | {'version': version}
    with pytest.raises(InvalidExport):
        import_user(populated, exported)
    assert populated.signals.count() == 3


@pytest.mark.parametrize('config', [None, [], {'nope': 1}, {'aggregation': 'median'}])
def test_rejects_invalid_widget_config(populated, config):
    exported = export_user(populated)
    exported['analytics_boards'][0]['widgets'][0]['config'] = config
    with pytest.raises(InvalidExport):
        import_user(populated, exported)
    assert AnalyticsWidget.objects.filter(board__user=populated).count() == 1


def test_import_keeps_settings_that_no_longer_fit_the_signal(populated):
    # a signal can be switched to "average" after a widget was saved
    AnalyticsWidget.objects.filter(board__user=populated).update(config={'aggregation': 'per_event'})
    Signal.objects.filter(user=populated, name='Mood').update(summary_method='average')
    import_user(populated, export_user(populated))
    assert AnalyticsWidget.objects.get(board__user=populated).config == {'aggregation': 'per_event'}


def upload(data, password='x'):
    return {'file': SimpleUploadedFile('e.json', json.dumps(data).encode()), 'password': password}


def test_export_and_import_endpoints(populated):
    client = APIClient()
    client.force_authenticate(populated)
    response = client.get('/api/users/me/export/')
    assert response.status_code == 200
    assert 'attachment' in response['Content-Disposition']
    exported = json.loads(response.content)

    assert client.post('/api/users/me/import/', upload(exported, 'wrong')).status_code == 400
    assert client.post('/api/users/me/import/', upload(exported), format='multipart').status_code == 204
    bad = client.post('/api/users/me/import/', upload({'x': 1}), format='multipart')
    assert bad.status_code == 400
    assert populated.signals.count() == 3
