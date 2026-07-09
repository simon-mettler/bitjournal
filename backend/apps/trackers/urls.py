from rest_framework.routers import DefaultRouter
from .views import TrackerViewSet, TrackerCategoryViewSet

router = DefaultRouter()

router.register('categories', TrackerCategoryViewSet, basename='trackercategory')
router.register('trackers', TrackerViewSet, basename='tracker')

urlpatterns = router.urls
