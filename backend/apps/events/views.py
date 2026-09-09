from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.signals.models import Signal
from .models import Event, SignalEntry
from .serializers import EventSerializer, EventWriteSerializer


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Event.objects.filter(user=self.request.user)
            .prefetch_related('entries__signal')
        )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return EventWriteSerializer
        return EventSerializer


    # HELPERS

    def _resolve_signals(self, entries_data, request):
        """
        Check Signal for each entry, scoped to the requesting user.
        """
        signal_ids = [entry['signal_id'] for entry in entries_data]

        signals_by_id = {
            signal.id: signal
            for signal in Signal.objects.filter(pk__in=signal_ids, user=request.user)
            .select_related('range_config')
        }

        unknown_ids = {sid for sid in signal_ids if sid not in signals_by_id}
        if unknown_ids:
            error = {
                'entries': [
                    {'signal_id': f'Unknown or inaccessible signal id: {sid}'}
                    for sid in sorted(unknown_ids, key=str)
                ]
            }
            return None, error

        return signals_by_id, None

    def _validate_entry(self, signal, value, duration):
        """
        Validate a SignalEntry without saving it.
        """
        probe = SignalEntry(signal=signal, value=value, duration=duration)
        try:
            probe.clean()
            return None
        except ValidationError as exc:
            return {'__all__': exc.messages}

    def _validate_entries(self, entries_data, signals_by_id):
        """
        Validate every entry against its resolved signal.
        Returns a dict of {entry_index: error}, empty if all entries are valid.
        """
        errors = {}
        for index, entry_data in enumerate(entries_data):
            signal = signals_by_id[entry_data['signal_id']]
            error = self._validate_entry(
                signal, entry_data.get('value'), entry_data.get('duration')
            )
            if error:
                errors[index] = error
        return errors

    def _serialize_event(self, event):
        instance = self.get_queryset().get(pk=event.pk)
        return EventSerializer(instance).data

    # CREATE

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        entries_data = data.pop('entries')

        signals_by_id, error = self._resolve_signals(entries_data, request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        errors = self._validate_entries(entries_data, signals_by_id)
        if errors:
            return Response({'entries': errors}, status=status.HTTP_400_BAD_REQUEST)

        event = Event.objects.create(user=request.user, **data)
        SignalEntry.objects.bulk_create([
            SignalEntry(
                event=event,
                signal=signals_by_id[entry_data['signal_id']],
                value=entry_data.get('value'),
                duration=entry_data.get('duration'),
            )
            for entry_data in entries_data
        ]) 

        return Response(self._serialize_event(event), status=status.HTTP_201_CREATED)

    # UPDATE

    def _check_entries_belong_to_event(self, entries_data, existing_entries_by_id):
        """
        Reject entries with unknown id
        """
        incoming_ids = {entry['id'] for entry in entries_data if entry.get('id')}
        foreign_ids = incoming_ids - set(existing_entries_by_id)

        if not foreign_ids:
            return None

        return {
            'entries': [
                {'id': f'Entry {entry_id} does not belong to this event.'}
                for entry_id in foreign_ids
            ]
        }

    def _apply_entry_changes(self, event, entries_data, signals_by_id, existing_entries_by_id):
        """
        Sync event entries with submitted payload. Delete entries missing from payload, create entriese without id
        and update entries with matching id.
        """
        incoming_ids = {entry['id'] for entry in entries_data if entry.get('id')}

        stale_ids = set(existing_entries_by_id) - incoming_ids
        if stale_ids:
            SignalEntry.objects.filter(pk__in=stale_ids).delete()

        entries_to_update = []
        entries_to_create = []

        for entry_data in entries_data:
            entry_id = entry_data.get('id')
            signal = signals_by_id[entry_data['signal_id']]
            value = entry_data.get('value')
            duration = entry_data.get('duration')

            if entry_id and entry_id in existing_entries_by_id:
                entry = existing_entries_by_id[entry_id]
                entry.signal = signal
                entry.value = value
                entry.duration = duration
                entries_to_update.append(entry)
            else:
                entries_to_create.append(
                    SignalEntry(event=event, signal=signal, value=value, duration=duration)
                )

        if entries_to_update:
            now = timezone.now()
            # set auto_now 'manually' because bulk_update() does not trigger save()
            for entry in entries_to_update:
                entry.updated_at = now
            SignalEntry.objects.bulk_update(
                entries_to_update, ['signal', 'value', 'duration', 'updated_at']
            )

        if entries_to_create:
            SignalEntry.objects.bulk_create(entries_to_create)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        entries_data = data.pop('entries')

        signals_by_id, error = self._resolve_signals(entries_data, request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        existing_entries_by_id = {entry.id: entry for entry in event.entries.all()}

        error = self._check_entries_belong_to_event(entries_data, existing_entries_by_id)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        errors = self._validate_entries(entries_data, signals_by_id)
        if errors:
            return Response({'entries': errors}, status=status.HTTP_400_BAD_REQUEST)

        event.occurred_at = data['occurred_at']
        event.note = data.get('note', '')
        event.save()

        self._apply_entry_changes(event, entries_data, signals_by_id, existing_entries_by_id)

        return Response(self._serialize_event(event))

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'PATCH is not supported.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
