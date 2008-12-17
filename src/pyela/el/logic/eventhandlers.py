# Copyright 2008 Alex Collins
#
# This file is part of Pyela.
# 
# Pyela is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pyela is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Pyela.  If not, see <http://www.gnu.org/licenses/>.
"""EL related event handlers"""

from pyela.logic.eventhandlers import BaseEventHandler
from pyela.el.logic.events import ELEventType
from pyela.el.net.elconstants import ELNetFromServer

import logging

log = logging.getLogger('pyela.el.logic.eventhandlers')

class RawTextEventHandler(BaseEventHandler):
	"""Deals with all network related events"""

	def __init__(self):
		self.event_types = []
		self.event_types.append(ELEventType(ELNetFromServer.RAW_TEXT))
		# TODO: these could be configurable

	def notify(self, event):
		if event.type.id == ELNetFromServer.RAW_TEXT:
			log.debug("HAHAH I GOTZ RAW TEXT JA!")

	def get_event_types(self):
		return self.event_types

	def subscribe_event(self, event):
		pass

	def __str__(self):
		return repr("RawTextHandler.types=%s" % self.event_types)
