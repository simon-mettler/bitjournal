from rest_framework.routers import DefaultRouter
from .views import SignalViewSet, SignalCategoryViewSet

router = DefaultRouter()

router.register('categories', SignalCategoryViewSet, basename='signalcategory')
router.register('signals', SignalViewSet, basename='signal')

urlpatterns = router.urls
