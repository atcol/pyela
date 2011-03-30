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

from pyela.el.common.actors import ELActor
from pyela.el.util.strings import strip_chars, split_str, is_colour, el_colour_to_rgb
from pyela.el.net.packets import ELPacket
from pyela.el.net.elconstants import ELNetFromServer, ELNetToServer, ELConstants
from pyela.el.net.channel import Channel
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.logic.events import ELEventType, ELEvent

log = logging.getLogger('pyela.el.net.parsers')
em = ELSimpleEventManager()

class MessageParser(object):
	"""A message received from the Eternal Lands server"""

	def __init__(self, connection):
		"""The connection should be an instance of ELConnection"""
		self.connection = connection
	
	def parse(self, packet):
		"""Parse the given packet and return a list of Event
		instances (or derivatives) (if any)
		"""
		pass

class ELRawTextMessageParser(MessageParser):
	"""Parses RAW_TEXT messages"""
	def parse(self, packet):
		event = ELEvent(ELEventType(ELNetFromServer.RAW_TEXT))
		event.data = {}
		event.data['connection'] = self.connection #The connection the message origins from
		event.data['channel'] = struct.unpack('<b', packet.data[0])[0] # The channel of the message
		event.data['text'] = strip_chars(packet.data[1:]) # The stripped text of the message, no colour codes, special characters translated to utf8
		event.data['raw'] = packet.data[1:] # The raw text including colour codes and untranslated special characters
		return [event]

class ELAddActorMessageParser(MessageParser):
	def parse(self, packet):
		"""Parse an ADD_NEW_(ENHANCED)_ACTOR message"""
		if log.isEnabledFor(logging.DEBUG): log.debug("New actor: %s" % packet)
		actor = ELActor()
		actor.id, actor.x_pos, actor.y_pos, actor.z_pos, \
		actor.z_rot, actor.type, frame, actor.max_health, \
		actor.cur_health, actor.kind_of_actor \
		= struct.unpack('<HHHHHBBHHB', packet.data[:17])
		events = []

		#Remove the buffs from the x/y coordinates
		actor.x_pos = actor.x_pos & 0x7FF
		actor.y_pos = actor.y_pos & 0x7FF

		if packet.type == ELNetFromServer.ADD_NEW_ENHANCED_ACTOR:
			actor.name = packet.data[28:]
			frame = struct.unpack('B', packet.data[22])[0] #For some reason, data[11] is unused in the ENHANCED message
			actor.kind_of_actor = struct.unpack('B', packet.data[27])[0]
		else:
			actor.name = packet.data[17:]
		
		#The end of name is a \0, and there _might_ be two OR three more bytes
		# containing actor-scale info.
		name_end = actor.name.find('\0')
		if name_end < len(actor.name)-2:
			#There are two OR three more bytes after the name,
			# the actor scaling bytes and possibly the attachment type
			unpacked = struct.unpack('<H', actor.name[name_end+1:name_end+3])
			actor.scale = unpacked[0]
			#actor.scale = float(scale)/ELConstants.ACTOR_SCALE_BASE
			if len(actor.name) > name_end+3:
				pass
				#TODO: The actor class has no attachment_type member (yet)
				#      The below code is tested and extracts the correct information
				#actor.attachment_type = struct.unpack('B', actor.name[name_end+3])[0]
				#if actor.attachment_type > 0 and actor.attachment_type < 255:
				#	##ON A HORSE!!
				#else:
				#	actor.attachment_type = 0 # The server sends either 255 or 0 if we're not on a horse
			actor.name = actor.name[:name_end]
		else:
			actor.scale = 1
			actor.name = actor.name[:-1]

		#Find the actor's name's colour char
		i = 0
		while i < len(actor.name) and is_colour(actor.name[i]):
			actor.name_colour = el_colour_to_rgb(ord(actor.name[i]))
			i += 1
		if actor.name_colour[0] == -1:
			#We didn't find any colour codes, use kind_of_actor
			if actor.kind_of_actor == ELConstants.NPC:
				#NPC, bluish
				#The official client colour is (0.3, 0.8, 1.0), but it's too green to see on the minimap
				actor.name_colour = (0.0, 0.0, 1.0)
			elif actor.kind_of_actor in (ELConstants.HUMAN, ELConstants.COMPUTER_CONTROLLED_HUMAN):
				#Regular player, white
				actor.name_colour = (1.0, 1.0, 1.0)
			elif packet.type == ELNetFromServer.ADD_NEW_ENHANCED_ACTOR and actor.kind_of_actor in (ELConstants.PKABLE_HUMAN, ELConstants.PKABLE_COMPUTER_CONTROLLED):
				#PKable player, red
				actor.name_colour = (1.0, 0.0, 0.0)
			else:
				#Animal, yellow
				actor.name_colour = (1.0, 1.0, 0.0)

		space = actor.name.rfind(' ')
		if space != -1 and space > 0 and space+1 < len(actor.name) and is_colour(actor.name[space+1]):
			if log.isEnabledFor(logging.DEBUG): log.debug("Actor has a guild. Parsing from '%s'" % actor.name)
			# split the name into playername and guild
			tokens = actor.name.rsplit(' ', 1)
			actor.name = tokens[0]
			actor.guild = strip_chars(tokens[1])
		actor.name = strip_chars(actor.name)
		
		#Deal with the current frame of the actor
		if frame in (ELConstants.FRAME_DIE1, ELConstants.FRAME_DIE2):
			actor.dead = True
		elif frame in (ELConstants.FRAME_COMBAT_IDLE, ELConstants.FRAME_IN_COMBAT):
			actor.fighting = True
		elif frame >= ELConstants.FRAME_ATTACK_UP_1 and frame <= ELConstants.FRAME_ATTACK_UP_10:
			actor.fighting = True
		elif frame in (ELConstants.PAIN1, ELConstants.PAIN2):
			actor.fighting = True

		self.connection.session.actors[actor.id] = actor
		
		event = ELEvent(ELEventType(ELNetFromServer.ADD_NEW_ACTOR))
		event.data = actor #TODO: add connection to event data
		events.append(event)
		if actor.id == self.connection.session.own_actor_id:
			self.connection.session.own_actor = actor
			event = ELEvent(ELEventType(ELNetFromServer.YOU_ARE))
			event.data = actor #TODO: add connection to event data
			events.append(event)

		if log.isEnabledFor(logging.DEBUG): log.debug("Actor parsed: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (actor.id, actor.x_pos, actor.y_pos, actor.z_pos, \
			actor.z_rot, actor.type, actor.max_health, \
			actor.cur_health, actor.kind_of_actor, actor.name))
		return events

class ELRemoveActorMessageParser(MessageParser):
	def _get_ids(data):
		offset = 0
		while offset < len(data):
			yield struct.unpack_from('<H', data, offset)[0]
			offset += 2
	_get_ids = staticmethod(_get_ids)

	def parse(self, packet):
		"""Remove actor packet. Remove from self.connection.session.actors dict"""
		if log.isEnabledFor(logging.DEBUG): log.debug("Remove actor packet: '%s'" % packet.data)
		if log.isEnabledFor(logging.DEBUG): log.debug("Actors: %s" % self.connection.session.actors)
		for actor_id in self._get_ids(packet.data):
			event = ELEvent(ELEventType(ELNetFromServer.REMOVE_ACTOR))
			event.data = {}
			event.data['connection'] = self.connection
			event.data['id'] = actor_id
			event.data['actor'] = self.connection.session.actors[actor_id]
			if actor_id in self.connection.session.actors:
				del self.connection.session.actors[actor_id]
			if actor_id == self.connection.session.own_actor_id:
				self.connection.session.own_actor_id = -1
				self.connection.session.own_actor = None
		return [event]

class ELRemoveAllActorsParser(MessageParser):
	def parse(self, packet):
		event = ELEvent(ELEventType(ELNetFromServer.KILL_ALL_ACTORS))
		event.data = {'connection': self.connection} # The full actors list can be added to the event data if it's required
		
		self.connection.session.actors = {}
		if log.isEnabledFor(logging.DEBUG): log.debug("Remove all actors packet")
		return [event]

class ELAddActorCommandParser(MessageParser):
	def _get_commands(data):
		offset = 0
		while offset < len(data):
			yield struct.unpack_from('<HB', data, offset)
			offset += 3
	_get_commands = staticmethod(_get_commands)

	def parse(self, packet):
		events = []
		if log.isEnabledFor(logging.DEBUG): log.debug("Actor command packet: '%s'" % packet.data)
		for actor_id, command in self._get_commands(packet.data):
			if actor_id in self.connection.session.actors:
				self.connection.session.actors[actor_id].handle_command(command)
	
				event = ELEvent(ELEventType(ELNetFromServer.ADD_ACTOR_COMMAND))
				event.data = {'actor': self.connection.session.actors[actor_id], 'command': command, 'connection': self.connection}
				events.append(event)
		return events

class ELYouAreParser(MessageParser):
	def parse(self, packet):
		if log.isEnabledFor(logging.DEBUG): log.debug("YouAre packet: '%s'" % packet.data)
		id = struct.unpack('<H', packet.data)[0]
		self.connection.session.own_actor_id = id
		if id in self.connection.session.actors:
			self.connection.session.own_actor = self.connection.session.actors[id]
			
			event = ELEvent(ELEventType(ELNetFromServer.YOU_ARE))
			event.data = self.connection.session.own_actor #TODO: Add connection to event.data
			return[event]
		return []

class ELGetActiveChannelsMessageParser(MessageParser):
	"""parse the GET_ACTIVE_CHANNELS message"""
	def parse(self, packet):
		del self.connection.session.channels[:]
		#Message structure: Active channel (1, 2 or 3), channel 1, channel 2, channel 3
		chans = struct.unpack('<BIII', packet.data)
		i = 0
		active = chans[0]
		for c in chans[1:]:
			if c != 0:
				self.connection.session.channels.append(Channel(self.connection, c, i == active))
			i += 1
		#Event to notify about the change in the channel list
		event = ELEvent(ELEventType(ELNetFromServer.GET_ACTIVE_CHANNELS))
		event.data = {'connection': self.connection, 'channels': self.connection.session.channels}
		return [event]

class ELBuddyEventMessageParser(MessageParser):
	"""Parse the BUDDY_EVENT message"""
	def parse(self, packet):
		change = ord(packet.data[0])# 1 is online, 0 offline
		event = ELEvent(ELEventType(ELNetFromServer.BUDDY_EVENT))
		event.data = {}
		if change == 1:
			#Buddy came online
			buddy = str(strip_chars(packet.data[2:]))
			self.connection.session.buddies.append(buddy)
			event.data['event'] = 'online'
		else:
			#Buddy went offline
			buddy = str(strip_chars(packet.data[1:]))
			self.connection.session.buddies.remove(buddy)
			event.data['event'] = 'offline'
		event.data['name'] = buddy
		event.data['connection'] = self.connection
		return [event]

class ELLoginFailedParser(MessageParser):
	"""Parse the LOG_IN_NOT_OK message"""
	def parse(self, packet):
		event = ELEvent(ELEventType(ELNetFromServer.LOG_IN_NOT_OK))
		event.data = {}
		event.data['text'] = strip_chars(packet.data)
		event.data['raw'] = packet.data
		event.data['connection'] = self.connection
		return [event]

class ELYouDontExistParser(MessageParser):
	"""Parse the YOU_DONT_EXIST message"""
	def parse(self, packet):
		event = ELEvent(ELEventType(ELNetFromServer.YOU_DONT_EXIST))
		event.data = {}
		event.data['connection'] = self.connection
		return[event]

class ELLoginOKParser(MessageParser):
	"""Parse the LOG_IN_OK message"""
	def parse(self, packet):
		event = ELEvent(ELEventType(ELNetFromServer.LOG_IN_OK))
		event.data = {}
		event.data['connection'] = self.connection
		self.connection.con_tries = 0
		return [event]

class ELPingRequestParser(MessageParser):
	"""Parse the PING_REQUEST message and respond with the appropriate message.
	Does not raise an event, as this is strictly a protocol feature and not
	something the application itself should worry about."""
	def parse(self, packet):
		# Send the message back as-is.
		self.connection.send(ELPacket(ELNetToServer.PING_RESPONSE, packet.data))
		return []
