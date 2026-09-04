from django.urls import path

from apps.users.views import LoginView


urlpatterns = [
    path('', LoginView.as_view(), name='login'),
]
