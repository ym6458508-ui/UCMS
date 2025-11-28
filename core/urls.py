from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    DepartmentViewSet,
    CourseViewSet,
    EnrollmentViewSet,
    MaterialViewSet,
    AnnouncementViewSet,
)


router = DefaultRouter()
router.register(r"departments", DepartmentViewSet)
router.register(r"courses", CourseViewSet)
router.register(r"enrollments", EnrollmentViewSet)
router.register(r"materials", MaterialViewSet)
router.register(r"announcements", AnnouncementViewSet)

urlpatterns = [
    path("", include(router.urls)),

    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
