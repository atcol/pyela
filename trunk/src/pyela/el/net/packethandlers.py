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
from pyela.el.net.parsers import BotRawTextMessageParser, \
	ELAddActorMessageParser, ELAddActorCommandParser, \
	ELRemoveActorMessageParser, ELGetActiveChannelsMessageParser, \
	ELBuddyEventMessageParser, ELRemoveAllActorsParser, ELYouAreParser, \
	ELRawTextMessageParser, ELBuddyEventMessageParser, ELLoginFailedParser, \
	ELYouDontExistParser

log = logging.getLogger('pyela.el.net.packethandlers')

class BaseELPacketHandler(BasePacketHandler):
	"""Defines base functionality for handling an ELConnection.
	"""

	def __init__(self, session):
		super(BaseELPacketHandler, self).__init__()
		self.session = session
		self.CALLBACKS = {}

	def process_packets(self, packets):
		events = []
		for packet in packets:
			log.debug("Message: %s?, %d, type=%s" % \
				(ELNetFromServer.to_identifier(ELNetFromServer(), int(packet.type)), packet.type, type(packet)))
			if packet.type in self.CALLBACKS:
				events = self.CALLBACKS[packet.type].parse(packet)
		return events

## ExtendedELPacketHandler is the same as above, except it has all the
## message parsers related to session handling set up
class ExtendedELPacketHandler(BaseELPacketHandler):
	def __init__(self, session):
		super(ExtendedELPacketHandler, self).__init__(session)
		self.CALLBACKS[ELNetFromServer.RAW_TEXT] = ELRawTextMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ENHANCED_ACTOR] = ELAddActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ACTOR] = ELAddActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_ACTOR_COMMAND] = ELAddActorCommandParser(self.session)
		self.CALLBACKS[ELNetFromServer.REMOVE_ACTOR] = ELRemoveActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.KILL_ALL_ACTORS] = ELRemoveAllActorsParser(self.session)
		self.CALLBACKS[ELNetFromServer.YOU_ARE] = ELYouAreParser(self.session)
		self.CALLBACKS[ELNetFromServer.GET_ACTIVE_CHANNELS] = ELGetActiveChannelsMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.BUDDY_EVENT] = ELBuddyEventMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.LOG_IN_NOT_OK] = ELLoginFailedParser(self.session)
		self.CALLBACKS[ELNetFromServer.YOU_DONT_EXIST] = ELYouDontExistParser(self.session)

class ELTestPacketHandler(BaseELPacketHandler):
	"""A derivative of BasePacketHandler that watches for RAW_TEXT packets 
	from an ELConnection and responds to their content
	"""

	def __init__(self, session):
		super(ELTestPacketHandler, self).__init__(session)
		self.session = session
		self.CALLBACKS = {}
		self.__setup_callbacks()

	def __setup_callbacks(self):
		self.CALLBACKS[ELNetFromServer.RAW_TEXT] = BotRawTextMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ENHANCED_ACTOR] = ELAddActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ACTOR] = ELAddActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_ACTOR_COMMAND] = ELAddActorCommandParser(self.session)
		self.CALLBACKS[ELNetFromServer.REMOVE_ACTOR] = ELRemoveActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.KILL_ALL_ACTORS] = ELRemoveAllActorsParser(self.session)
		self.CALLBACKS[ELNetFromServer.YOU_ARE] = ELYouAreParser(self.session)
		self.CALLBACKS[ELNetFromServer.GET_ACTIVE_CHANNELS] = ELGetActiveChannelsMessageParser(self.session)
