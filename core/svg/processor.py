#!/usr/bin/env python3
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

import hashlib
import os
import re
from core.utils import find_file
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile


class SVGIconsProcessor(object):
	"""
		Initialized
	"""
	cache = FileSystemStorage(
		location=os.path.join(settings.MEDIA_ROOT, 'svg'),
		base_url=os.path.join(settings.MEDIA_URL, 'svg'))
	svg_extension = '.svg'
	svg_regexp = re.compile('<svg[^>]*>(.*)</svg>', re.M | re.S)

	def __init__(self, icons):
		icons.sort()
		self.icons = icons

	def get(self):
		digest = hashlib.sha256()
		digest.update(repr(self.icons).encode('utf-8'))
		hash = digest.hexdigest()

		filename = hash + self.svg_extension

		if self.icons:
			content = ''

			if self.cache.exists(filename):
				with self.cache.open(filename) as svg_file:
					content = svg_file.read().decode()
			else:
				content = self._process()
				self.cache.save(filename, ContentFile(content))
			return content
		else:
			return ''

	def _process(self):
		svg_icons_content = ''
		for icon in self.icons:
			svg_icons_content += self._get_icon(icon)
		return self._encapsulate(svg_icons_content)

	def _get_icon(self, name):
		icon_filename = name + self.svg_extension

		path = find_file(os.path.join('core', 'icons', icon_filename))

		if not path:
			return ''

		content = None
		with open(path) as svg_file:
			content = svg_file.read()

		matches = self.svg_regexp.match(content)

		parts = [
			'<symbol id="icon-',
			name,
			'">',
			matches.group(1),
			'</symbol>'
		]

		return ''.join(parts)

	def _encapsulate(self, svg_icons_content):
		parts = [
			'<svg xmlns="http://www.w3.org/2000/svg" class="svg-sprites"><defs>',
			svg_icons_content,
			'</defs></svg>'
		]
		return ''.join(parts)
