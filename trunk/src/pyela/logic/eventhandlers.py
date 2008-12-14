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
"""Event handlers subscribe to particular events and act on them when raised"""

class HandlerException(Exception):
	def __init__(self, val):
		self.val = val

	def __str__(self):
		return repr(self.val)

class BaseEventHandler(object):
	"""The base class defining the contract for any EventHandler"""

	def notify(self, event):
		"""Notify this instance that the given event has been raised"""
		pass

	def subscribe_event(self, event):
		"""Tell this handler to watch for the given event"""
		pass

	def get_events(self):
		"""Returns a list of events that this handler is subscribed to"""
		pass

class SingleEventHandler(BaseEventHandler):
	"""An event handler that deals with only one event"""

	def __init__(self, event):
		self._event = event

	def notify(self, event):
		if event.id == self._event.id:
			

	def get_events(self):
		return [self._event]

	def subscribe_event(self, event):
		"""Raises HandlerException. Event subscribed in constructor"""
		raise HandlerException("This class does not allow multiple events")
