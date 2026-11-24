from django.urls import path

from .views import ExportView, ImportView

urlpatterns = [
    path('users/me/export/', ExportView.as_view(), name='export-data'),
    path('users/me/import/', ImportView.as_view(), name='import-data'),
]
