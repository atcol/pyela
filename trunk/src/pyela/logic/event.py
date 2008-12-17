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
"""Objects and methods relating to events within the framework"""

class EventException(Exception):
	def __init__(self, val):
		self.val = val

	def __str__(self):
		return repr(self.val)

class BaseEventType(object):
	"""A desciriptor for events"""
	pass

class BaseEvent(object):
	"""Represents an action or occurance of actions within the framework.
	Used in an event-driven manner within the PacketHandlers
	"""

	def __init__(self):
		"""Construct a basic event object with the optional 
		data"""
		pass

	def get_type(self):
		"""An identifier describing this particular event"""
		pass
