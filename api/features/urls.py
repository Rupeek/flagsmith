from django.conf import settings
from django.conf.urls import include
from django.urls import path
from rest_framework_nested import routers

from features.feature_segments.views import FeatureSegmentViewSet
from features.views import SimpleFeatureStateViewSet

router = routers.DefaultRouter()
router.register(r"featurestates", SimpleFeatureStateViewSet, basename="featurestates")
router.register(r"feature-segments", FeatureSegmentViewSet, basename="feature-segment")


app_name = "features"

urlpatterns = [
    path("", include(router.urls)),
]

if settings.WORKFLOWS_LOGIC_INSTALLED:
    urlpatterns.append(
        path(
            "workflows/",
            include(
                f"{settings.WORKFLOWS_LOGIC_MODULE_PATH}.urls", namespace="workflows"
            ),
        )
    )
