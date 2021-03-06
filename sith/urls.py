# -*- coding:utf-8 -*
#
# Copyright 2016,2017
# - Skia <skia@libskia.so>
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

"""sith URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from ajax_select import urls as ajax_select_urls

js_info_dict = {"packages": ("sith",)}

handler403 = "core.views.forbidden"
handler404 = "core.views.not_found"
handler500 = "core.views.internal_servor_error"

urlpatterns = [
    re_path(r"^", include(("core.urls", "core"), namespace="core")),
    re_path(
        r"^rootplace/", include(("rootplace.urls", "rootplace"), namespace="rootplace")
    ),
    re_path(
        r"^subscription/",
        include(("subscription.urls", "subscription"), namespace="subscription"),
    ),
    re_path(r"^com/", include(("com.urls", "com"), namespace="com")),
    re_path(r"^club/", include(("club.urls", "club"), namespace="club")),
    re_path(r"^counter/", include(("counter.urls", "counter"), namespace="counter")),
    re_path(r"^stock/", include(("stock.urls", "stock"), namespace="stock")),
    re_path(
        r"^accounting/",
        include(("accounting.urls", "accounting"), namespace="accounting"),
    ),
    re_path(r"^eboutic/", include(("eboutic.urls", "eboutic"), namespace="eboutic")),
    re_path(
        r"^launderette/",
        include(("launderette.urls", "launderette"), namespace="launderette"),
    ),
    re_path(r"^sas/", include(("sas.urls", "sas"), namespace="sas")),
    re_path(r"^api/v1/", include(("api.urls", "api"), namespace="api")),
    re_path(
        r"^election/", include(("election.urls", "election"), namespace="election")
    ),
    re_path(r"^forum/", include(("forum.urls", "forum"), namespace="forum")),
    re_path(r"^trombi/", include(("trombi.urls", "trombi"), namespace="trombi")),
    re_path(r"^matmatronch/", include(("matmat.urls", "matmat"), namespace="matmat")),
    re_path(
        r"^pedagogy/", include(("pedagogy.urls", "pedagogy"), namespace="pedagogy")
    ),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^ajax_select/", include(ajax_select_urls)),
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
    re_path(r"^jsi18n/$", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    re_path(r"^captcha/", include("captcha.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar

    urlpatterns += [re_path(r"^__debug__/", include(debug_toolbar.urls))]
