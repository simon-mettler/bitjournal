import json

from django.http import JsonResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ImportSerializer
from .services import InvalidExport, export_user, import_user


class ExportView(APIView):
    throttle_scope = 'auth'

    def get(self, request):
        response = JsonResponse(export_user(request.user))
        filename = f'bitjournal-export-{timezone.localdate():%Y-%m-%d}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ImportView(APIView):
    """Replace all of the user's data with an uploaded export."""
    throttle_scope = 'auth'

    def post(self, request):
        serializer = ImportSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            data = json.load(serializer.validated_data['file'])
        except ValueError:
            raise ValidationError({'file': ['The file is not valid JSON.']})
        try:
            import_user(request.user, data)
        except InvalidExport as e:
            raise ValidationError({'file': [str(e)]})
        return Response(status=204)
