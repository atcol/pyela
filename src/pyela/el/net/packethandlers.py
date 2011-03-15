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
"""Packet processing"""

import logging
import collections
import struct

from pyela.net.packethandlers import BasePacketHandler
from pyela.el.net.elconstants import ELNetFromServer, ELNetToServer
from pyela.el.net.packets import ELPacket
from pyela.el.net.parsers import ELAddActorMessageParser, \
	ELAddActorCommandParser, ELRemoveActorMessageParser, \
	ELGetActiveChannelsMessageParser, \
	ELBuddyEventMessageParser, ELRemoveAllActorsParser, ELYouAreParser, \
	ELRawTextMessageParser, ELBuddyEventMessageParser, ELLoginFailedParser, \
	ELYouDontExistParser, ELLoginOKParser

log = logging.getLogger('pyela.el.net.packethandlers')

class BaseELPacketHandler(BasePacketHandler):
	"""Defines base functionality for handling an ELConnection.
	"""

	def __init__(self, connection):
		"""
			Parameters:
			connection - the ELConnection that this packet handler handles packets for
		"""
		super(BaseELPacketHandler, self).__init__()
		self.connection = connection
		self.CALLBACKS = {}

	def process_packets(self, packets):
		events = []
		for packet in packets:
			log.debug("Message: %s?, %d, type=%s" % \
				(ELNetFromServer.to_identifier(ELNetFromServer(), int(packet.type)), packet.type, type(packet)))
			if packet.type in self.CALLBACKS:
				events.extend(self.CALLBACKS[packet.type].parse(packet))
		return events

## ExtendedELPacketHandler is the same as above, except it has all the
## message parsers related to connection/session handling set up
class ExtendedELPacketHandler(BaseELPacketHandler):
	""" ExtendedELPacketHandler is the same as BaseELPacketHandler, except it
	has all the message parsers related to session handling set up
	"""
	def __init__(self, connection):
		super(ExtendedELPacketHandler, self).__init__(connection)
		self.CALLBACKS[ELNetFromServer.RAW_TEXT] = ELRawTextMessageParser(self.connection)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ENHANCED_ACTOR] = ELAddActorMessageParser(self.connection)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ACTOR] = ELAddActorMessageParser(self.connection)
		self.CALLBACKS[ELNetFromServer.ADD_ACTOR_COMMAND] = ELAddActorCommandParser(self.connection)
		self.CALLBACKS[ELNetFromServer.REMOVE_ACTOR] = ELRemoveActorMessageParser(self.connection)
		self.CALLBACKS[ELNetFromServer.KILL_ALL_ACTORS] = ELRemoveAllActorsParser(self.connection)
		self.CALLBACKS[ELNetFromServer.YOU_ARE] = ELYouAreParser(self.connection)
		self.CALLBACKS[ELNetFromServer.GET_ACTIVE_CHANNELS] = ELGetActiveChannelsMessageParser(self.connection)
		self.CALLBACKS[ELNetFromServer.BUDDY_EVENT] = ELBuddyEventMessageParser(self.connection)
		self.CALLBACKS[ELNetFromServer.LOG_IN_NOT_OK] = ELLoginFailedParser(self.connection)
		self.CALLBACKS[ELNetFromServer.LOG_IN_OK] = ELLoginOKParser(self.connection)
		self.CALLBACKS[ELNetFromServer.YOU_DONT_EXIST] = ELYouDontExistParser(self.connection)
