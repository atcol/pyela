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
"""Holds the event mappings and allows the raising of events"""

from pyela.logic.event import BaseEvent

class SimpleEventManager(object):
	"""Defines the 'contract' for all events and their respective handlers. 
	An event manager will deal with notifying the relevant handlers when 
	a particular event is raised"""

	def __init__(self):
		self._handlers = {}

	def raise_event(self, event):
		"""Notify all handlers for the given event"""
		pass

	def add_handler(self, event_handler):
		"""Manage the given handler"""
		# for each event in event_handler.get_events():
		# 	if event in self._handlers:
		# 		self._handlers[event.type].append(event_handler)
		#	else: 
		#		self._handlers[event.type] = (event_handler)
		pass
