from rest_framework.routers import DefaultRouter
from .views import SignalViewSet, SignalCategoryViewSet

router = DefaultRouter()

router.register('categories', SignalCategoryViewSet, basename='signalcategory')
router.register('signal', SignalViewSet, basename='signal')

urlpatterns = router.urls
