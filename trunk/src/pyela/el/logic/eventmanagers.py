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
"""EL event management"""

import logging

from pyela.logic.eventmanager import SimpleEventManager

log = logging.getLogger('pyela.el.logic.eventmanagers.ELSimpleEventManager')

class ELSimpleEventManager(object):
	"""A singleton implementation of a SimpleEventManager"""
	__instance = None

	class __impl(SimpleEventManager):
		def __init__(self):
			self._handlers = {}

		def raise_event(self, event):
			"""Notify all handlers for the given event"""
			log.debug("Got event: %s" % event)
			if self._handlers.has_key(event.type.id):
				for handler in self._handlers[event.type.id]:
					handler.notify(event)
			else:
				log.debug("Event %s not handled, no mapping available" % event)

		def add_handler(self, event_handler):
			"""Manage the given handler. When an event raised
			whose .type value is in event_handler.get_event_types(),
			notify() will be called on this handler
			"""
			if log.isEnabledFor(logging.DEBUG): log.debug("received handler: %s"\
				% event_handler)

			for type in event_handler.get_event_types():
				if self._handlers.has_key(type.id):
					self._handlers[type.id].append(event_handler)
				else: 
					self._handlers[type.id] = [event_handler]

	def __init__(self):
		if ELSimpleEventManager.__instance is None:
			ELSimpleEventManager.__instance = ELSimpleEventManager.__impl()
		self.__dict__['_ELSimpleEventManager__instance'] = \
			ELSimpleEventManager.__instance

	def __getattr__(self, attr):
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		return setattr(self.__instance, attr, value)

