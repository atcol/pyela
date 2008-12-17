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
"""EL related events"""

from pyela.logic.event import BaseEventType, BaseEvent, EventException

class ELEventType(BaseEventType):
	def __init__(self, id):
		self.id = id

	def __str__(self):
		return repr("ELEventType.id=%s" % self.id)

class ELEvent(BaseEvent):

	def __init__(self, type):
		self.type = type

	def get_type(self):
		return self.type

	def __str__(self):
		return repr("ELEvent.type=%s" % self.type)

class ELNetEvent(ELEvent):
	"""A network related event. The constructor will enforce the given type is 
	in ELConstants, ELNetFromServer or ELNetToServer
	"""
	
	def __init__(self, type):
		#if type not in ELConstants or type not in ELNetFromServer \
		#	or type not in ELNetToServer:
		#		raise EventException("Incorrect type for a network event")
		#else:
		self.type = type
