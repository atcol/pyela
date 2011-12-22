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
	"""A descriptor for events"""
	def __eq__(self, other):
		"""Must be implemented for all event types"""
		pass
	
	def __cmp__(self, other):
		"""Must be implemented for all event types"""
		pass
	
	def __hash__(self):
		"""Must be implemented for all event types"""
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


(NET_CONNECTED, NET_DISCONNECTED) = list(range(1,3))

class NetEventType(BaseEventType):
	def __init__(self, id):
		if not id in (NET_CONNECTED, NET_DISCONNECTED):
			raise TypeError("Not a valid net event")
		self.id = id

	def __str__(self):
		return repr("NetEventType.id=%s" % self.id)
	
	def __eq__(self, other):
		return self.id == other.id
	
	def __cmp__(self, other):
		return self.id - other.id
	
	def __hash__(self):
		s = self.__str__()
		return hash(s)

class NetEvent(BaseEvent):
	"""Network related events, like socket disconnected or connected.
	The data field contains the Connection object and the fileno of the socket.
	In the case of disconnection, NO operations should be performed on the socket."""
	def __init__(self, type, connection = None):
		if not isinstance(type, NetEventType):
			raise TypeError()
		self.type = type
		self.data = {'connection': connection}
		if connection.socket != None:
			self.data['fileno'] = connection.socket.fileno()
		else:
			self.data['fileno'] = None

	def get_type(self):
		return self.type

	def __str__(self):
		return repr("NetEvent.type=%s" % self.type)
