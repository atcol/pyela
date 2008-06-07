"""Numerous objects for parsing the messages (raw bytes) from a server 
into their relevant format for use with the rest of the API.

The MessageParser base class defines common functionality for using these 
objects without prior knowledge of the instance at runtime.
"""
import logging
import struct

from placid.el.common.actors import ELActor
from placid.el.util.strings import strip_chars
from placid.el.net.packets import ELPacket
from placid.el.net.elconstants import ELNetFromServer, ELNetToServer

log = logging.getLogger('placid.el.net.parsers')

class MessageParser(object):
	"""A message received from the Eternal Lands server"""

	def __init__(self, session):
		"""The session should be an instance of ELSession"""
		self.session = session
	
	def parse(self, packet):
		"""Parse the given packet and return a list of Packet
		instances (or derivatives) ready for output (if any)
		"""
		pass
	
class ELRawTextMessageParser(MessageParser):
	
	def parse(self, packet):
		"""Parses a RAW_TEXT message"""
		data = packet.data[2:]
		log.debug("Data for packet %s: %s" % (packet.type, packet.data))
		if not data.startswith("Volturin:"):
			data = data[data.find("Volturin: ") + len("Volturin: "):]
			if data.startswith("%s," % self.session.name[0].lower()) \
				or data.startswith("%s," % self.session.name[0].upper()):
				if data[data.find(",") + 1:].split()[0] == "who":
					actors_str = ""
					for actor in self.session.actors.values():
						actors_str += "%s, " % actor

					return [ELPacket(ELNetToServer.RAW_TEXT, actors_str[:-1])]
		return []

class ELAddActorMessageParser(MessageParser):
	def parse(self, packet):
		"""Parse an ADD_ENHANCED_ACTOR message"""
		log.debug("New actor: %s" % packet)
		actor = ELActor()
		actor.id, actor.x_pos, actor.y_pos, actor.z_pos, \
		actor.z_rot, actor.type, actor.frame, actor.max_health, \
		actor.cur_health, actor.kind_of_actor \
		= struct.unpack('<HHHHHBBHHB', packet.data[:17])
		actor.name = packet.data[28:]

		
		#The end of name is a \0, and there _might_ be two more bytes
		# containing actor-scale info.
		if actor.name[-3] == '\0':
			#There are two more bytes after the name,
			# the actor scaling bytes
			unpacked = struct.unpack('<H', actor.name[-2:])
			actor.scale = unpacked[0]
			#actor.scale = float(scale)/ELConstants.ACTOR_SCALE_BASE
			actor.name = actor.name[:-3]
		else:
			actor.scale = 1
			actor.name = actor.name[:-1]

		actor.name = strip_chars(actor.name)

		if ' ' in actor.name:
			# split the name into playername and guild
			actor.name = actor.name[:actor.name.find(' ')]
			actor.guild = actor.name[actor.name.find(' '):]

		self.session.actors[actor.id] = actor

		log.debug("Actor parsed: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (actor.id, actor.x_pos, actor.y_pos, actor.z_pos, \
			actor.z_rot, actor.type, actor.frame, actor.max_health, \
			actor.cur_health, actor.kind_of_actor, actor.name))
		return []

class ELRemoveActorMessageParser(MessageParser):
	def parse(self, packet):
		"""Remove actor packet. Remove from self.session.actors dict"""
		log.debug("Remove actor packet: '%s'" % packet.data)
		actor_id = struct.unpack('<H', packet.data)
		log.debug("Actors: %s" % self.session.actors)
		if actor_id in self.session.actors:
			del self.session.actors[actor_id]
