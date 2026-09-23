from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from apps.core.models import STEP_LABELS, Visitor
from apps.core.presence import online_visitor_ids

VISITOR_DB_SORT_FIELDS = ('phone', 'country', 'step', 'ip', 'last_seen_at')
VISITOR_COMPUTED_SORT_FIELDS = ('online', 'needs_action')
VISITOR_SORT_FIELDS = VISITOR_DB_SORT_FIELDS + VISITOR_COMPUTED_SORT_FIELDS
VISITOR_DEFAULT_SORT = '-last_seen_at'
VISITOR_FILTER_FIELDS = ('phone', 'country', 'step', 'ip')


class ManagerDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'core/manager_dashboard.html'
    login_url = reverse_lazy('admin:login')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['step_labels'] = STEP_LABELS
        return context


class ManagerVisitorListView(UserPassesTestMixin, TemplateView):
    template_name = 'core/manager_visitor_list.html'
    login_url = reverse_lazy('admin:login')
    page_size = 25

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sort = self.request.GET.get('sort', VISITOR_DEFAULT_SORT)
        sort_field = sort.lstrip('-')
        if sort_field not in VISITOR_SORT_FIELDS:
            sort = VISITOR_DEFAULT_SORT
            sort_field = 'last_seen_at'

        filters = {name: self.request.GET.get(name, '').strip() for name in VISITOR_FILTER_FIELDS}

        qs = Visitor.objects.all()
        if filters['phone']:
            qs = qs.filter(phone__icontains=filters['phone'])
        if filters['country']:
            qs = qs.filter(country__icontains=filters['country'])
        if filters['step']:
            qs = qs.filter(step=filters['step'])
        if filters['ip']:
            qs = qs.filter(ip__icontains=filters['ip'])

        online_ids = set(online_visitor_ids())

        if sort_field in VISITOR_COMPUTED_SORT_FIELDS:
            # not DB columns - sort in Python instead
            visitors = list(qs.order_by('-last_seen_at', 'visitor_id'))
            if sort_field == 'online':
                key = lambda v: v.visitor_id in online_ids
            else:
                key = lambda v: bool(v.needs_action and v.visitor_id in online_ids)
            visitors.sort(key=key, reverse=sort.startswith('-'))
        else:
            visitors = qs.order_by(sort, 'visitor_id')

        page_obj = Paginator(visitors, self.page_size).get_page(self.request.GET.get('page'))

        context['page_obj'] = page_obj
        context['paginator'] = page_obj.paginator
        context['is_paginated'] = page_obj.has_other_pages()
        context['sort'] = sort
        context['sort_columns'] = self._sort_columns(sort)
        context['filters'] = filters
        context['step_choices'] = STEP_LABELS.items()
        context['list_qs'] = self.request.GET.urlencode()
        context['page_qs_extra'] = self._page_qs_extra()
        context['rows'] = [
            {
                'visitor_id': v.visitor_id,
                'phone': v.phone,
                'country': v.country,
                'ip': v.ip,
                'last_seen_at': v.last_seen_at,
                'step_label': STEP_LABELS.get(v.step, v.step),
                'is_waiting': v.step == 'waiting',
                'is_online': v.visitor_id in online_ids,
                'needs_action': v.needs_action and v.visitor_id in online_ids,
            }
            for v in page_obj
        ]
        return context

    def _sort_columns(self, current_sort):
        active_field = current_sort.lstrip('-')
        columns = {}
        for field in VISITOR_SORT_FIELDS:
            if field == active_field:
                arrow = '↓' if current_sort.startswith('-') else '↑'
                next_sort = field if current_sort.startswith('-') else f'-{field}'
            else:
                arrow = ''
                next_sort = field
            params = self.request.GET.copy()
            params['sort'] = next_sort
            params.pop('page', None)
            columns[field] = {'url': f'?{params.urlencode()}', 'arrow': arrow}
        return columns

    def _page_qs_extra(self):
        """Current filters/sort as a '&key=value...' suffix (no 'page') for page-number links."""
        params = self.request.GET.copy()
        params.pop('page', None)
        qs = params.urlencode()
        return f'&{qs}' if qs else ''


class VisitorControlView(UserPassesTestMixin, TemplateView):
    template_name = 'core/visitor_control.html'
    login_url = reverse_lazy('admin:login')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visitor_id'] = kwargs['visitor_id']
        context['step_labels'] = STEP_LABELS
        back_qs = self.request.GET.get('back', '')
        visitors_url = reverse('manager-visitors')
        context['visitors_back_url'] = f'{visitors_url}?{back_qs}' if back_qs else visitors_url
        return context
