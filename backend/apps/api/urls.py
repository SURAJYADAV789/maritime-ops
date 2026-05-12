from django.urls import path
from .views import (
    # Auth
    RegisterView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    ProfileView,
    # Ships
    ShipListView,
    ShipDetailView,
    # Maintenance
    TaskListView,
    TaskDetailView,
    TaskCommentView,
    # Drills
    DrillListView,
    DrillDetailView,
    DrillAttendanceView,
    # Compliance
    ComplianceView,
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="api-register"),
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="api-refresh"),
    path("auth/me/", ProfileView.as_view(), name="api-me"),
    # Ships
    path("ships/", ShipListView.as_view(), name="api-ship-list"),
    path("ships/<int:pk>/", ShipDetailView.as_view(), name="api-ship-detail"),
    # Maintenance
    path("maintenance/", TaskListView.as_view(), name="api-task-list"),
    path("maintenance/<int:pk>/", TaskDetailView.as_view(), name="api-task-detail"),
    path("maintenance/<int:pk>/comments/", TaskCommentView.as_view(), name="api-task-comment"),
    # Drills
    path("drills/", DrillListView.as_view(), name="api-drill-list"),
    path("drills/<int:pk>/", DrillDetailView.as_view(), name="api-drill-detail"),
    path("drills/<int:pk>/attend/",DrillAttendanceView.as_view(),name="api-drill-attend"),
    # Compliance
    path("compliance/", ComplianceView.as_view(), name="api-compliance"),
]
