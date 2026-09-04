from django.views.generic import TemplateView

from apps.users.forms import PhoneLoginForm
from apps.users.phone_countries import get_country_options


class LoginView(TemplateView):
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PhoneLoginForm()
        context['country_options'] = get_country_options()
        return context
