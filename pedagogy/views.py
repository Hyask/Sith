# -*- coding:utf-8 -*
#
# Copyright 2017
# - Sli <antoine@bartuccio.fr>
#
# Ce fichier fait partie du site de l'Association des Étudiants de l'UTBM,
# http://ae.utbm.fr.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License a published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Sofware Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA.
#
#

from django.views.generic import CreateView, DeleteView, DetailView, ListView, FormView
from django.core.urlresolvers import reverse_lazy

from core.views import (
    DetailFormView,
    CanCreateMixin,
    CanEditMixin,
    CanViewMixin,
    CanEditPropMixin,
)

from pedagogy.forms import UVForm
from pedagogy.models import UV


class UVDetailFormView(DetailFormView):
    """
    Dispaly every comment of an UV and detailed infos about it
    Allow to comment the UV
    """

    pass


class UVCommentDetailView(DetailView):
    """
    Display a specified UVComment (for easy sharing of the comment)
    """

    pass


class UVListView(ListView):
    """
    UV guide main page
    """

    pass


class UVCommentReportCreateView(CreateView):
    """
    Create a new report for an inapropriate comment
    """

    pass


class UVCommentReportListView(ListView):
    """
    List all UV reports for moderation (Privileged)
    """

    pass


class UVModerationFormView(FormView):
    """
    List all UVs to moderate and allow to moderate them (Privileged)
    """

    pass


class UVCreateView(CanCreateMixin, CreateView):
    """
    Add a new UV (Privileged)
    """

    model = UV
    form_class = UVForm
    template_name = "core/edit.jinja"

    def get_form_kwargs(self):
        kwargs = super(UVCreateView, self).get_form_kwargs()
        kwargs["author_id"] = self.request.user.id
        return kwargs

    def get_success_url(self):
        return reverse_lazy("pedagogy:uv_detail", kwargs={"uv_id": self.object.id})


class UVDeleteView(DeleteView):
    """
    Allow to delete an UV (Privileged)
    """

    pass


class EducationDepartmentCreateView(CreateView):
    """
    Add a new Education Department (Privileged)
    """

    pass


class EducationDepartmentDeleteView(DeleteView):
    """
    Allow to delete an Education Department (Privileged)
    """

    pass


class StudyFieldCreateView(CreateView):
    """
    Add a new Study Field (Privileged)
    """

    pass


class StudyFieldDeleteView(DeleteView):
    """
    Allow to delete an Study Field (Privileged)
    """

    pass
