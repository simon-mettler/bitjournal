import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from rest_framework.test import APIClient

from apps.signals.models import Signal, SignalType

from .models import AnalyticsBoard, AnalyticsWidget, WidgetType
from .widget_types import WIDGET_TYPES


def test_every_widget_type_has_a_definition():
    assert set(WIDGET_TYPES) == set(WidgetType.values)


@pytest.mark.parametrize('widget_type, config, expected', [
    ('value', {}, {'aggregation': 'total'}),
    ('value', {'aggregation': 'average'}, {'aggregation': 'average'}),
    ('timeseries', {}, {'chart_type': 'bar', 'show_average': True}),
    ('timeseries', {'show_average': False}, {'chart_type': 'bar', 'show_average': False}),
])
def test_clean_config_fills_defaults(widget_type, config, expected):
    assert WIDGET_TYPES[widget_type].clean_config(config) == expected


@pytest.mark.parametrize('widget_type, config', [
    ('value', None),
    ('value', []),
    ('value', {'chart_type': 'bar'}),  # a setting of another type
    ('value', {'aggregation': 'median'}),
    ('value', {'aggregation': ['total']}),
    ('timeseries', {'show_average': 'yes'}),
    ('timeseries', {'show_average': 1}),
])
def test_clean_config_rejects(widget_type, config):
    with pytest.raises(ValidationError):
        WIDGET_TYPES[widget_type].clean_config(config)


@pytest.fixture
def api(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def payload(user):
    signal = Signal.objects.create(user=user, name='Coffee', type=SignalType.TALLY)
    board = AnalyticsBoard.objects.create(user=user, name='B')
    return {
        'board_id': str(board.id), 'signal_id': str(signal.id), 'type': 'timeseries',
        'title': 'W', 'config': {'chart_type': 'line'}, 'timeframe': 'this_week',
    }


def test_create_update_and_read_config(api, payload):
    created = api.post('/api/analytics-widgets/', payload, format='json')
    assert created.status_code == 201
    assert created.data['config'] == {'chart_type': 'line', 'show_average': True}

    url = f'/api/analytics-widgets/{created.data["id"]}/'
    update = {**payload, 'config': {'chart_type': 'bar', 'show_average': False}}
    assert api.put(url, update, format='json').data['config'] == update['config']

    values = api.get(f'/api/analytics-boards/{payload["board_id"]}/values/?tz=UTC').data[0]
    assert values['value'] is None and values['timeseries']['step'] == 'day'


@pytest.mark.parametrize('change, field', [
    ({'config': {'aggregation': 'total'}}, 'config'),
    ({'config': None}, 'config'),
    ({'timeframe': 'today'}, 'timeframe'),
    ({'type': 'value', 'config': {'aggregation': 'per_event'}}, 'config'),  # tally
])
def test_create_rejects(api, payload, change, field):
    response = api.post('/api/analytics-widgets/', {**payload, **change}, format='json')
    assert response.status_code == 400
    assert field in response.data


def test_update_without_config_keeps_the_settings(api, payload):
    """A cached app from before 'config' existed must not reset the settings."""
    created = api.post('/api/analytics-widgets/', payload, format='json')
    old = {key: value for key, value in payload.items() if key != 'config'}
    response = api.put(f'/api/analytics-widgets/{created.data["id"]}/', old, format='json')
    assert response.status_code == 400
    assert AnalyticsWidget.objects.get().config['chart_type'] == 'line'


@pytest.mark.django_db(transaction=True)
def test_migration_moves_settings_into_config_and_back():
    before = [('analytics', '0003_alter_analyticswidget_aggregation')]
    after = [('analytics', '0004_widget_config')]

    def migrate(target):
        MigrationExecutor(connection).migrate(target)
        # the models of the other apps must match the database, which stays at their latest
        loader = MigrationExecutor(connection).loader
        others = [node for node in loader.graph.leaf_nodes() if node[0] != target[0][0]]
        return loader.project_state([*others, *target]).apps

    latest = MigrationExecutor(connection).loader.graph.leaf_nodes()
    try:
        apps = migrate(before)
        user = apps.get_model('users', 'BitjournalUser').objects.create(email='m@example.com')
        signal = apps.get_model('signals', 'Signal').objects.create(user=user, name='S', type='value')
        board = apps.get_model('analytics', 'AnalyticsBoard').objects.create(user=user, name='B')
        old_widgets = apps.get_model('analytics', 'AnalyticsWidget').objects
        common = {'board': board, 'signal': signal, 'timeframe': 'this_week'}
        old_widgets.create(type='value', title='v', aggregation='per_event', **common)
        old_widgets.create(
            type='timeseries', title='t', chart_type='line', show_average=False, **common)

        widgets = migrate(after).get_model('analytics', 'AnalyticsWidget').objects
        assert dict(widgets.values_list('title', 'config')) == {
            'v': {'aggregation': 'per_event'},
            't': {'chart_type': 'line', 'show_average': False},
        }

        widgets = migrate(before).get_model('analytics', 'AnalyticsWidget').objects
        columns = ('title', 'aggregation', 'chart_type', 'show_average')
        assert sorted(widgets.values_list(*columns)) == [
            ('t', 'total', 'line', False), ('v', 'per_event', 'bar', True),
        ]
    finally:
        migrate(latest)
