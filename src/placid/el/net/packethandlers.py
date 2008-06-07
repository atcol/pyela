"""Packet processing"""

import logging
import collections
import struct

from placid.net.packethandlers import BasePacketHandler
from placid.el.net.elconstants import ELNetFromServer, ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.net.parsers import ELRawTextMessageParser, ELAddActorMessageParser
from placid.el.common.actors import ELActor
from placid.el.util.strings import strip_chars

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
		#self.CALLBACKS[ELNetFromServer.REMOVE_ACTOR] = ELRemoveActorMessageParser(self.session)
		#self.CALLBACKS[ELNetFromServer.ADD_NEW_ACTOR] = 'new_actor'

	def process_packets(self, packets):
		for packet in packets:
			log.debug("Message: %s?, %d, type=%s" % \
				(ELNetFromServer.to_identifier(ELNetFromServer(), int(packet.type)), packet.type, type(packet)))
			packets.remove(packet)
			if packet.type in self.CALLBACKS:
				opt_packets = self.CALLBACKS[packet.type].parse(packet)
				if len(opt_packets) > 0:
					self._opt.append(opt_packets)


	def remove_actor(self, packet):
		"""Remove actor packet. Remove from self.session.actors dict"""
		log.debug("Remove actor packet: '%s'" % packet.data)
		actor_id = struct.unpack('<H', packet.data)
		#log.debug("Removing actor '%s' by ID '%d' from %s" % (self.session.actors[actor_id], actor_id, self.session.actors))
		log.debug("Actors: %s" % self.session.actors)
		if actor_id in self.session.actors:
			del self.session.actors[actor_id]
