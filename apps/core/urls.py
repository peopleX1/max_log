from django.urls import path

from apps.core.views import ManagerDashboardView, VisitorControlView


urlpatterns = [
    path('manager/', ManagerDashboardView.as_view(), name='manager-dashboard'),
    path('manager/<str:visitor_id>/', VisitorControlView.as_view(), name='manager-visitor'),
]
