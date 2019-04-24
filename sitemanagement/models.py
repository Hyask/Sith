# -*- coding:utf-8 -*
#
# Copyright 2016,2019
# - Skia <skia@libskia.so>
# - Krophil <pierre.brunet@krophil.fr>
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
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils.functional import cached_property

from datetime import timedelta, date, datetime
import random
import string
import os
import base64
import datetime

from club.models import Club
from accounting.models import CurrencyField
from core.models import Group, User, SithFile
from subscription.models import Subscription


class Cheque(models.Model):
    """
    This describes a caution cheque, with all its related informations
    """
    comment = models.TextField(_("description"), blank=True)
    user = models.ForeignKey(
        User, related_name="cheques_as_user", blank=False
    )
    amount = CurrencyField(_("amount"))
    bank = models.CharField(_("name"), max_length=30)
    returned = models.BooleanField(_("is returned"), default=False)
    scan = models.ForeignKey(
        SithFile,
        related_name="cheques",
        verbose_name=_("scan"),
        null=True,
        blank=True,
    )


class Asset(models.Model):
    """
    This describes an asset, with all its related informations
    """
    LOCATION, ROOM, ELEMENT, BOARDGAME, KEY = range(5)
    ASSET_TYPES = (
        (LOCATION, _('Location')),
        (ROOM, _('Room')),
        (ELEMENT, _('Element')),
        (BOARDGAME, _('Boardgame')),
        (KEY, _('Key')),
    )
    type = models.PositiveIntegerField(choices=ASSET_TYPES, default=ELEMENT)
    name = models.CharField(_("name"), max_length=64)
    description = models.TextField(_("description"), blank=True)
    code = models.CharField(_("code"), max_length=16, blank=True)
    borrowable = models.BooleanField(_("borrowable"), default=False)
    loan_form = models.CharField(_("code"), max_length=16, blank=True)
    purchase_price = CurrencyField(_("purchase price"))
    purchase_date = models.DateField(_("date"), default=0)
    caution_price = CurrencyField(_("caution price"))
    icon = models.ImageField(
        upload_to="assets", null=True, blank=True, verbose_name=_("icon")
    )
    club = models.ForeignKey(Club, related_name="assets", verbose_name=_("asset_club"))
    condition = models.CharField(
        _("condition"), max_length=255, choices=settings.SITH_WORKING_CONDITION, default="OTHER"
    )
    archived = models.BooleanField(_("archived"), default=False)

    def is_owned_by(self, user):
        """
        Method to see if that object can be edited by the given user
        """
        if user.is_in_group(settings.SITH_GROUP_SITE_MANAGEMENT_ID):
            return True
        return False

    def can_be_edited_by(self, user):
        """
        Method to see if that object can be edited by the given user
        """
        m = self.club.get_membership_for(user)
        if m and m.role == settings.SITH_CLUB_ROLES_ID["Secretary"]:
            return True
        return False

    def can_be_viewed_by(self, user):
        """
        Method to see if that object can be viewed by the given user
        """
        if user.is_subscribed and self.borrowable:
            return True
        return False

    def can_be_borrowed_by(self, user):
        """
        Method to see if that object can be borrowed by the given user
        """

        if user.is_subscribed and self.borrowable:
            return True
        return False

    def can_be_borrowed_between(self, start_date, end_date):
        loan = self.loans.filter(
            subscription_start__gte=start_date, subscription_end__lte=end_date
        )
        return not loan.exists()

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")


class Loan(models.Model):
    """
    This describes an asset group to make borrowing groups, with all its related informations
    """
    assets = models.ManyToManyField(
        Asset,
        related_name="loans",
        verbose_name=_("assets"),
        blank=True
    )
    comment = models.TextField(_("comment"), blank=True)
    asker_type = models.CharField(
        _("asker type"),
        max_length=10,
        choices=[
            ("USER", _("User")),
            ("CLUB", _("Club")),
            ("OTHER", _("Other")),
        ],
    )
    asker_id = models.IntegerField(_("target id"), null=True, blank=True)
    asker_label = models.CharField(
        _("asker label"), max_length=32, default="", blank=True
    )
    operator = models.ForeignKey(
        User, related_name="loans_as_operator", blank=False
    )
    start_date = models.DateField(_("date"), default=timezone.now)
    planned_end_date = models.DateField(_("date"))
    end_date = models.DateField(_("date"), default=None)
    caution_cheque = models.ForeignKey(
        Cheque,
        related_name="loans",
        verbose_name=_("cheque"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    accepted = models.BooleanField(_("is accepted"), default=False)
    archived = models.BooleanField(_("is archived"), default=False)
    done = models.BooleanField(_("is done"), default=False)

    @cached_property
    def is_late(self):
        return self.end_date is not None and self.end_date < datetime.now()
