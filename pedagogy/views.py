# -*- coding:utf-8 -*
#
# Copyright 2017
# - Krophil' <pierre.brunet@krophil.fr>
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


from core.views import CanViewMixin, CanEditPropMixin, CanCreateMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView

from django.conf import settings

from django import forms
from django.core.urlresolvers import reverse_lazy
from pedagogy.models import Course, PedaComment


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'formation', 'category', 'semester']


class CourseCreateView(CanCreateMixin, CreateView):
    """
    Create a course
    """
    model = Course
    form_class = CourseForm
    template_name = 'core/create.jinja'
    success_url = reverse_lazy('pedagogy:course_list')


class CourseEditView(CanCreateMixin, UpdateView):
    """
    Edit a course
    """
    model = Course
    pk_url_kwarg = "course_id"
    fields = ['name']
    template_name = 'core/edit.jinja'
    success_url = reverse_lazy('pedagogy:course_list')


class CourseDetailView(CanViewMixin, DetailView):
    """
    Details of the course
    """
    model = Course
    pk_url_kwarg = "course_id"
    template_name = 'pedagogy/detail.jinja'

    def get_context_data(self, **kwargs):
        kwargs = super(CourseDetailView, self).get_context_data(**kwargs)
        kwargs['year_parts'] = settings.SCHOOL_YEAR_PARTS
        kwargs['course'] = self.object
        kwargs['comments'] = self.object.received_comments.all()
        return kwargs


class CourseListView(ListView, CanEditPropMixin):
    """
    Displays the user list
    """
    model = Course
    template_name = "pedagogy/course_list.jinja"


class PedaCommentForm(forms.ModelForm):
    class Meta:
        model = PedaComment
        fields = ['author', 'uv', 'comment']
    interest = forms.ChoiceField(choices=PedaComment.STARS)
    utility = forms.ChoiceField(choices=PedaComment.STARS)
    work = forms.ChoiceField(choices=PedaComment.STARS)
    teaching = forms.ChoiceField(choices=PedaComment.STARS)
    global_mark = forms.ChoiceField(choices=PedaComment.STARS)


class PedaCommentCreateView(CanCreateMixin, CreateView):
    model = PedaComment
    form_class = PedaCommentForm
    template_name = 'core/create.jinja'
    success_url = reverse_lazy('pedagogy:course_list')
