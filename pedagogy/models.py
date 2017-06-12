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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from core.views import CanViewMixin, CanEditMixin, CanEditPropMixin, CanCreateMixin, TabedViewMixin

from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView

from datetime import date

from core.models import User


# class PedaManager(models.Manager):
#   def get_queryset(self):
#      return super(PedaManager, self).get_queryset()


class Course(models.Model):
    """
    Course to comment
    """
    name = models.CharField(max_length=60)
    code = models.CharField(max_length=10)
    formation = models.CharField(_('Formation type'),
                                 max_length=255,
                                 choices=settings.SCHOOL_FORMATIONS.items())
    category = models.CharField(_('Category'),
                                max_length=255,
                                choices=settings.SCHOOL_CATEGORIES.items())
    semester = models.CharField(_('Semester'),
                                max_length=60,
                                choices=settings.SCHOOL_YEAR_PARTS.items())

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pedagogy:detail', kwargs={'subject_id': self.id})

    def can_be_viewed_by(self, user):
        return user.is_subscribed or user.was_subscribed

    def can_be_edit_by(self, user):
        return user.is_root


class PedaComment(models.Model):
    """
    This represent a comment given by someone on an UV
    """
    STARS = ((0, '\u2606\u2606\u2606\u2606\u2606'),
             (1, '\u2605\u2606\u2606\u2606\u2606'),
             (2, '\u2605\u2605\u2606\u2606\u2606'),
             (3, '\u2605\u2605\u2605\u2606\u2606'),
             (4, '\u2605\u2605\u2605\u2605\u2606'),
             (5, '\u2605\u2605\u2605\u2605\u2605'),
             )

    author = models.ForeignKey(User, related_name='given_comments')
    uv = models.ForeignKey(Course, verbose_name=_(
        "subject"), related_name='received_comments')
    comment = models.TextField(_("content"), default="")
    is_moderated = models.BooleanField(
        _("is the comment moderated"), default=False)
    comment_date = models.DateField(_('comment date'), default=date.today)
    interest = models.IntegerField(_('Interest'),
                                   default=5)
    utility = models.IntegerField(_('Utility'),
                                  default=5)
    work = models.IntegerField(_('Work'),
                               default=5)
    teaching = models.IntegerField(_('Teaching'),
                                   default=5)

    global_mark = models.IntegerField(_('Global mark'),
                                      default=5)


    class Meta:
        ordering = ('interest', 'utility', 'work', 'teaching')

    def can_be_viewed_by(self, user):
        return user.is_subscribed or user.was_subscribed

    def can_be_edit_by(self, user):
        return user.id == self.author.user.id or user.is_root
