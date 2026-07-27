from django.db import transaction, IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import SignalBoard, BoardSignal
from .serializers import (
    SignalBoardSerializer,
    SignalBoardCreateSerializer,
    SignalBoardUpdateSerializer,
    BoardReorderSerializer,
)
from signals.models import Signal


class SignalBoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            SignalBoard.objects
            .filter(user=self.request.user)
            .prefetch_related('board_signals__signal')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return SignalBoardCreateSerializer
        if self.action in ('update', 'partial_update'):
            return SignalBoardUpdateSerializer
        if self.action == 'reorder':
            return BoardReorderSerializer
        return SignalBoardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            SignalBoardSerializer(seriqlizer.instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        return self._save_board(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'PATCH is not supported.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @transaction.atomic
    def _save_board(self, request, *args, **kwargs):
        board = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        board.name = data['name']
        try:
            with transaction.atomic():
                board.save(update_fields=['name'])
        except IntegrityError:
            return Response(
                {'name': 'A board with this name already exists.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_ids = [str(sid) for sid in data['signal_ids']]

        valid_ids = set(
            str(pk) for pk in Signal.objects.filter(
                pk__in=new_ids, user=request.user
            ).values_list('pk', flat=True)
        )
        unknown = set(new_ids) - valid_ids
        if unknown:
            return Response(
                {'signal_ids': f'Unknown or inaccessible signal ids: {sorted(unknown)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # wipe and recreate membership/order.
        board.board_signals.all().delete()
        BoardSignal.objects.bulk_create([
            BoardSignal(board=board, signal_id=sid, order=i)
            for i, sid in enumerate(new_ids)
        ])

        # re-fetch: board.board_signals is cached from get_object()'s
        # prefetch and won't reflect the delete/bulk_create above
        board = self.get_queryset().get(pk=board.pk)
        return Response(SignalBoardSerializer(board).data)

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board_ids = [str(bid) for bid in serializer.validated_data['board_ids']]

        boards = {str(b.id): b for b in self.get_queryset()}

        # check if request contains exactly all boards
        if len(board_ids) != len(boards) or set(board_ids) != set(boards.keys()):
            return Response(
                {'detail': 'board_ids must match exactly your current boards.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for index, board_id in enumerate(board_ids):
                board = boards[board_id]
                if board.order != index:
                    board.order = index
                    board.save(update_fields=['order'])

        ordered_boards = [boards[bid] for bid in board_ids]
        return Response(SignalBoardSerializer(ordered_boards, many=True).data)
