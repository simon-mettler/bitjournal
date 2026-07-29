from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import viewsets, status
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

    def _resolve_signals(self, entries_data, request):
        """
        Resolve signal ids to Signal instances, scoped to the requesting user.
        Returns (signals_by_id, None) on success, or (None, error_dict) on failure.
        """
        signal_ids = [e['signal_id'] for e in entries_data]

        signals = {
            s.id: s
            for s in Signal.objects.filter(pk__in=signal_ids, user=request.user)
            .select_related('range_config')
        }

        unknown = {sid for sid in signal_ids if sid not in signals}
        if unknown:
            return None, {
                'entries': [
                    {'signal_id': f'Unknown or inaccessible signal id: {sid}'}
                    for sid in sorted(unknown, key=str)
                ]
            }

        # duplicate signal_ids are already rejected by
        # EventWriteSerializer.validate_entries before this is called.
        return signals, None

    def _validate_entry(self, signal, value, duration):
        """
        Run SignalEntry.clean() against an unsaved (or about-to-be-mutated)
        instance, so create and update share exactly one source of truth
        for entry validation.
        """
        probe = SignalEntry(signal=signal, value=value, duration=duration)
        try:
            probe.clean()
            return None
        except ValidationError as exc:
            return {'__all__': exc.messages}

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        entries_data = data.pop('entries')

        signals, error = self._resolve_signals(entries_data, request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        errors = {}
        instances = []
        for i, e in enumerate(entries_data):
            signal = signals[e['signal_id']]
            err = self._validate_entry(signal, e.get('value'), e.get('duration'))
            if err:
                errors[i] = err
                continue
            instances.append(SignalEntry(
                signal=signal,
                value=e.get('value'),
                duration=e.get('duration'),
            ))

        if errors:
            return Response({'entries': errors}, status=status.HTTP_400_BAD_REQUEST)

        event = Event.objects.create(user=request.user, **data)
        for entry in instances:
            entry.event = event
        SignalEntry.objects.bulk_create(instances)

        instance = self.get_queryset().get(pk=event.pk)
        return Response(EventSerializer(instance).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        entries_data = data.pop('entries')

        signals, error = self._resolve_signals(entries_data, request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        # Validate every incoming entry up front, against what it *would*
        # become, before mutating anything — so a bad entry fails the whole
        # request without partially updating existing rows.
        existing = {e.signal_id: e for e in event.entries.all()}
        errors = {}
        for i, e in enumerate(entries_data):
            signal = signals[e['signal_id']]
            err = self._validate_entry(signal, e.get('value'), e.get('duration'))
            if err:
                errors[i] = err

        if errors:
            return Response({'entries': errors}, status=status.HTTP_400_BAD_REQUEST)

        event.date = data['date']
        event.time = data['time']
        event.note = data.get('note', '')
        event.save()

        new_ids = {e['signal_id'] for e in entries_data}

        # remove entries for signals no longer present
        to_remove = set(existing) - new_ids
        if to_remove:
            SignalEntry.objects.filter(event=event, signal_id__in=to_remove).delete()

        # update in place (preserving id/created_at) or create new
        to_update = []
        to_create = []
        for e in entries_data:
            sid = e['signal_id']
            value = e.get('value')
            duration = e.get('duration')
            if sid in existing:
                entry = existing[sid]
                entry.value = value
                entry.duration = duration
                to_update.append(entry)
            else:
                to_create.append(SignalEntry(
                    event=event,
                    signal=signals[sid],
                    value=value,
                    duration=duration,
                ))

        if to_update:
            SignalEntry.objects.bulk_update(to_update, ['value', 'duration'])
        if to_create:
            SignalEntry.objects.bulk_create(to_create)

        instance = self.get_queryset().get(pk=event.pk)
        return Response(EventSerializer(instance).data)

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'PATCH is not supported.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
