from rest_framework.routers import DefaultRouter
from .views import SignalBoardViewSet

router = DefaultRouter()
router.register('boards', SignalBoardViewSet, basename='signal-board')

urlpatterns = router.urls
