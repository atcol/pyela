"""Packet processing"""

import logging
import collections
import struct

from placid.net.packethandlers import BasePacketHandler
from placid.el.net.elconstants import ELNetFromServer, ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.net.parsers import ELRawTextMessageParser, ELAddActorMessageParser, ELRemoveActorMessageParser, ELGetActiveChannelsMessageParser

log = logging.getLogger('placid.el.net.packethandlers')

class ELTestPacketHandler(BasePacketHandler):
	"""A derivative of BasePacketHandler that watches for RAW_TEXT packets 
	from an ELConnection and responds to their content
	"""

	def __init__(self, session):
		super(ELTestPacketHandler, self).__init__()
		self.session = session
		self.CALLBACKS = {}
		self.__setup_callbacks()

	def __setup_callbacks(self):
		self.CALLBACKS[ELNetFromServer.RAW_TEXT] = ELRawTextMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.ADD_NEW_ENHANCED_ACTOR] = ELAddActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.REMOVE_ACTOR] = ELRemoveActorMessageParser(self.session)
		self.CALLBACKS[ELNetFromServer.GET_ACTIVE_CHANNELS] = ELGetActiveChannelsMessageParser(self.session)

	def process_packets(self, packets):
		for packet in packets:
			log.debug("Message: %s?, %d, type=%s" % \
				(ELNetFromServer.to_identifier(ELNetFromServer(), int(packet.type)), packet.type, type(packet)))
			packets.remove(packet)
			if packet.type in self.CALLBACKS:
				opt_packets = self.CALLBACKS[packet.type].parse(packet)
				if opt_packets and len(opt_packets) > 0:
					self._opt.extend(opt_packets)
