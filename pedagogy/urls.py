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

from django.conf.urls import url

from pedagogy.views import *

urlpatterns = [
    url(r'^$', CourseListView.as_view(), name='course_list'),
    url(r'^course/new$', CourseCreateView.as_view(), name='create'),
    url(r'^course/(?P<course_id>[0-9]+)/edit$', CourseEditView.as_view(), name='edit'),
    url(r'^course/(?P<course_id>[0-9]+)/comment/new$', PedaCommentCreateView.as_view(), name='new_comment'),
    url(r'^course/(?P<course_id>[0-9]+)$', CourseDetailView.as_view(), name='course_detail'),
]
