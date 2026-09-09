from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class ManagerDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'core/manager_dashboard.html'
    login_url = reverse_lazy('admin:login')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class VisitorControlView(UserPassesTestMixin, TemplateView):
    template_name = 'core/visitor_control.html'
    login_url = reverse_lazy('admin:login')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visitor_id'] = kwargs['visitor_id']
        return context
