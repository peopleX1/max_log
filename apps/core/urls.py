from django.urls import path

from apps.core.views import ManagerDashboardView, ManagerVisitorListView, VisitorControlView


urlpatterns = [
    path('manager/', ManagerDashboardView.as_view(), name='manager-dashboard'),
    path('manager/visitors/', ManagerVisitorListView.as_view(), name='manager-visitors'),
    path('manager/<str:visitor_id>/', VisitorControlView.as_view(), name='manager-visitor'),
]
