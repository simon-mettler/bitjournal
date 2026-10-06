from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.http import require_safe


@require_safe
def spa_index(request, path=''):
    index = settings.FRONTEND_DIST / 'index.html'
    if not index.is_file():
        raise Http404('Frontend build not found.')
    response = FileResponse(open(index, 'rb'), content_type='text/html')
    response['Cache-Control'] = 'no-cache'
    return response
