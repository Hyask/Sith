from django.conf.urls import url, include

from counter.views import *

urlpatterns = [
    url(r'^(?P<counter_id>[0-9]+)$', CounterDetail.as_view(), name='details'),
    url(r'^admin/(?P<counter_id>[0-9]+)$', CounterEditView.as_view(), name='admin'),
    url(r'^admin$', CounterListView.as_view(), name='admin_list'),
    url(r'^admin/new$', CounterCreateView.as_view(), name='new'),
    url(r'^admin/delete/(?P<counter_id>[0-9]+)$', CounterDeleteView.as_view(), name='delete'),
]


