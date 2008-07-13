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
"""Numerous objects for parsing the messages (raw bytes) from a server 
into their relevant format for use with the rest of the API.

The MessageParser base class defines common functionality for using these 
objects without prior knowledge of the instance at runtime.
"""
import logging
import struct
import time

from placid.el.common.actors import ELActor
from placid.el.util.strings import strip_chars, split_str
from placid.el.net.packets import ELPacket
from placid.el.net.elconstants import ELNetFromServer, ELNetToServer, ELConstants
from placid.el.net.channel import Channel

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

class GUIRawTextMessageParser(MessageParser):
	def parse(self, packet):
		if struct.unpack('<b', packet.data[0])[0] in \
			(ELConstants.CHAT_CHANNEL1, ELConstants.CHAT_CHANNEL2, ELConstants.CHAT_CHANNEL3):
			channel = int(struct.unpack('<b', packet.data[0])[0])
			text = strip_chars(packet.data[1:])
			self.session.msg_buf.extend(["\n%s" % (text.replace(']', " @ %s]" % \
				self.session.channels[int(channel - ELConstants.CHAT_CHANNEL1)].number))])
		else:
			self.session.msg_buf.extend(["\n%s" % strip_chars(packet.data[1:])])
	
class BotRawTextMessageParser(MessageParser):
	"""Handles RAW_TEXT messages

	Attributes:
		commands - a dict of command name ('who', 'inv') and the 
					respective callback to use
	"""

	def __init__(self, session):
		super(ELRawTextMessageParser, self).__init__(session)
		self.commands = {}
		self.commands['WHO'] = self._do_who
		self.commands['HI'] = self._do_hi
		self.commands['TIME'] = self._do_time
		self.commands['LICK'] = self._do_lick
	
	def parse(self, packet):
		"""Parses a RAW_TEXT message"""
		data = strip_chars(packet.data[2:])
		log.debug("Data for RAW_TEXT packet %s: %s" % (packet.type, data))
		name_str = "%s:" % self.session.name
		if not data.startswith(name_str):
			log.debug("Not a message from me! (%s)" % name_str)
			log.debug("Found: %d" % (data.find(':') + 1))
			person = data[:data.find(':')]
			data = data[data.find(':') + 2:]
			log.debug("is message for me: (%s) %s" % (data, data.startswith("%s," % name_str[0].lower())))
			if data.startswith("%s," % name_str[0].lower()):
				words = data[data.find(",") + 1:].split()
				log.debug("Data; %s" % data)
				log.debug("Words for commands: %s" % words)
				if len(words) >= 1 and words[0].upper() in self.commands:
					log.debug("Found command '%s', executing" % words[0].upper())
					# data[1] is the params onwards to the command
					packets = self.commands[words[0].upper()](person, words[1:])
					return packets
		return []
	
	def _do_who(self, person, params):
		packets = []
		actors_str = ""
		for actor in self.session.actors.values():
			actors_str += "%s, " % actor
		actors_strs = split_str(actors_str, 157) 
		for str in actors_strs:
			packets.append(ELPacket(ELNetToServer.RAW_TEXT, str))

		return packets
	
	def _do_hi(self, person, params):
		return [ELPacket(ELNetToServer.RAW_TEXT, "Hi there, %s :D" % person)]

	def _do_time(self, person, params):
		return [ELPacket(ELNetToServer.RAW_TEXT, "%s: %s" % (person, time.asctime()))]
	
	def _do_lick(self, person, params):
		if len(words) > 1:
			return [ELPacket(ELNetToServer.RAW_TEXT, ":licks %s" % words[0])]
		else:
			return [ELPacket(ELNetToServer.RAW_TEXT, "...I'm not going to lick the air...")]

class ELAddActorMessageParser(MessageParser):
	def parse(self, packet):
		"""Parse an ADD_ENHANCED_ACTOR message"""
		log.debug("New actor: %s" % packet)
		actor = ELActor()
		actor.id, actor.x_pos, actor.y_pos, actor.z_pos, \
		actor.z_rot, actor.type, frame, actor.max_health, \
		actor.cur_health, actor.kind_of_actor \
		= struct.unpack('<HHHHHBBHHB', packet.data[:17])

		#Remove the buffs from the x/y coordinates
		actor.x_pos = actor.x_pos & 0x7FF
		actor.y_pos = actor.y_pos & 0x7FF

		if packet.type == ELNetFromServer.ADD_NEW_ENHANCED_ACTOR:
			actor.name = packet.data[28:]
			frame = packet.data[22] #For some reason, data[11] is unused in the ENHANCED message
		else:
			actor.name = packet.data[17:]

		
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
			log.debug("Actor has a guild. Parsing from '%s'" % actor.name)
			# split the name into playername and guild
			tokens = actor.name.split()
			actor.name = tokens[0]
			actor.guild = tokens[1]
		
		#Deal with the current frame of the actor
		if frame in (ELConstants.FRAME_DIE1, ELConstants.FRAME_DIE2):
			actor.dead = True
		elif frame in (ELConstants.FRAME_COMBAT_IDLE, ELConstants.FRAME_IN_COMBAT):
			actor.fighting = True
		elif frame >= ELConstants.FRAME_ATTACK_UP_1 and frame <= ELConstants.FRAME_ATTACK_UP_10:
			actor.fighting = True
		elif frame in (ELConstants.PAIN1, ELConstants.PAIN2):
			actor.fighting = True

		self.session.actors[actor.id] = actor

		log.debug("Actor parsed: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (actor.id, actor.x_pos, actor.y_pos, actor.z_pos, \
			actor.z_rot, actor.type, actor.max_health, \
			actor.cur_health, actor.kind_of_actor, actor.name))
		return []

class ELRemoveActorMessageParser(MessageParser):
	def _get_ids(data):
		offset = 0
		while offset < len(data):
			yield struct.unpack_from('<H', data, offset)[0]
			offset += 2
	_get_ids = staticmethod(_get_ids)
	def parse(self, packet):
		"""Remove actor packet. Remove from self.session.actors dict"""
		log.debug("Remove actor packet: '%s'" % packet.data)
		log.debug("Actors: %s" % self.session.actors)
		for actor_id in self._get_ids(packet.data):
			if actor_id in self.session.actors:
				del self.session.actors[actor_id]
		return []

class ELAddActorCommandParser(MessageParser):
	def _get_commands(data):
		offset = 0
		while offset < len(data):
			yield struct.unpack_from('<HB', data, offset)
			offset += 3
	_get_commands = staticmethod(_get_commands)

	def parse(self, packet):
		log.debug("Actor command packet: '%s'" % packet.data)
		for actor_id, command in self._get_commands(packet.data):
			if actor_id in self.session.actors:
				self.session.actors[actor_id].handle_command(command)
		return []

class ELGetActiveChannelsMessageParser(MessageParser):
	"""parse the GET_ACTIVE_CHANNELS message"""
	def parse(self, packet):
		del self.session.channels[:]
		chans = struct.unpack('<BIII', packet.data)
		i = 0
		active = chans[0]
		for c in chans[1:]:
			if c != 0:
				self.session.channels.append(Channel(c, i == active))
			i += 1
		return []

class ELBuddyEventMessageParser(MessageParser):
	"""Parse the BUDDY_EVENT message"""

	def parse(self, packet):
		event = ord(packet.data[0])# 1 is online, 0 offline
		if event == 1:
			buddy = str(strip_chars(packet.data[2:]))
			self.session.buddies.append(buddy)
		else:
			buddy = str(strip_chars(packet.data[1:]))
			self.session.buddies.remove(buddy)
		return []
