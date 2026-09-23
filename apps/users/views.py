import uuid

from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.core.consumers import log_visitor_input, update_visitor_and_notify
from apps.core.models import Visitor
from apps.users.forms import PhoneLoginForm
from apps.users.phone_countries import apply_mask, country_name_ru, find_country, get_country_options, mask_from_placeholder


def ensure_visitor_id(request):
    if not request.session.get('visitor_id'):
        request.session['visitor_id'] = str(uuid.uuid4())


def format_phone_display(phone, country_name=None):
    if not phone.startswith('+'):
        return phone

    country = find_country(dial=phone, name_ru=country_name)
    if not country:
        return phone

    national_digits = phone[len(country['dial']):]
    mask = mask_from_placeholder(country['placeholder'])
    formatted = apply_mask(national_digits, mask)
    return f"{country['dial']} {formatted}".rstrip()


class PhoneRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('visitor_phone'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class ResumeWaitingMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visitor_id = self.request.session.get('visitor_id')
        context['resume_waiting'] = bool(
            visitor_id and Visitor.objects.filter(visitor_id=visitor_id, step='waiting').exists()
        )
        return context


class LoginView(ResumeWaitingMixin, TemplateView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        ensure_visitor_id(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('form', PhoneLoginForm())
        context['country_options'] = get_country_options()
        return context

    def post(self, request, *args, **kwargs):
        ensure_visitor_id(request)
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            visitor_id = request.session.get('visitor_id')
            phone = form.cleaned_data['phone']
            country = form.cleaned_data.get('phone_country', '')
            country = country_name_ru(country)
            request.session['visitor_phone'] = phone
            request.session['visitor_country'] = country
            update_visitor_and_notify(visitor_id, phone=phone, country=country)
            phone_log_value = f'{phone} ({country})' if country else phone
            log_visitor_input(visitor_id, 'phone', phone_log_value)
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


class ErrorPageView(PhoneRequiredMixin, TemplateView):
    template_name = 'users/error.html'

    def get(self, request, *args, **kwargs):
        ensure_visitor_id(request)
        return super().get(request, *args, **kwargs)


class CaptchaView(ResumeWaitingMixin, PhoneRequiredMixin, TemplateView):
    template_name = 'users/captcha.html'

    def get(self, request, *args, **kwargs):
        ensure_visitor_id(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['captcha_id'] = uuid.uuid4()
        return context


class CodeView(ResumeWaitingMixin, PhoneRequiredMixin, TemplateView):
    template_name = 'users/code.html'

    def get(self, request, *args, **kwargs):
        ensure_visitor_id(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phone'] = format_phone_display(
            self.request.session.get('visitor_phone', ''),
            self.request.session.get('visitor_country', ''),
        )
        return context
