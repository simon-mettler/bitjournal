from rest_framework.pagination import CursorPagination

class EventCursorPagination(CursorPagination):
    page_size = 50
    max_page_size = 80
    page_size_query_param = 'limit'
    ordering = ('-occurred_at', '-id')
