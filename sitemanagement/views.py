from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, CreateView
from sitemanagement.models import Asset
from django.conf import settings
from django import forms
from core.views import (
    CanViewMixin,
    CanEditMixin,
    CanEditPropMixin,
    CanCreateMixin,
    can_view,
)


class SiteManagementMainView(ListView):
    queryset = Asset.objects.filter(type=Asset.LOCATION)
    template_name = "sitemanagement/location_list.jinja"


class LocationForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "name",
            "description",
        ]


class LocationCreateView(CanCreateMixin, CreateView):
    model = Asset
    form_class = LocationForm
    template_name = "core/create.jinja"

    def get_initial(self):
        init = super(LocationCreateView, self).get_initial()
        return init
