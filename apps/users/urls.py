from django.urls import path

from apps.users.views import CaptchaView, CodeView, ErrorPageView, LoginView


urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('captcha/', CaptchaView.as_view(), name='captcha'),
    path('code/', CodeView.as_view(), name='code'),
    path('error/', ErrorPageView.as_view(), name='error'),
]
