# Copyright 2008, 2011 Pyela project
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
"""EL related event handlers"""

from pyela.logic.eventhandlers import BaseEventHandler
from pyela.el.logic.events import ELEventType
from pyela.el.util.strings import split_str
from pyela.el.net.packets import ELPacket
from pyela.el.net.elconstants import ELNetFromServer, ELNetToServer

import logging
import time

log = logging.getLogger('pyela.bots.logic.eventhandlers')

class BotRawTextEventHandler(BaseEventHandler):
	"""Handles RAW_TEXT messages

	Attributes:
		commands - a dict of command name ('who', 'inv') and the 
					respective callback to use
					
					The callback takes three parameters, session, person, params
					- session: The ELSession that the command occured in (this may change to ELConnection in the future if it turns out that this is more suitable)
					- person: The person who sent the command
					- params: A list of the parameters to the command (params[0] is the command itself)
					
					The callback must return a list of ELPacket instances it wants to return
					to the server.
	"""

	def __init__(self):
		self.event_types = [ELEventType(ELNetFromServer.RAW_TEXT)]
		self.commands = {}
		self.commands['WHO'] = self._do_who
		self.commands['HI'] = self._do_hi
		self.commands['TIME'] = self._do_time
		self.commands['LICK'] = self._do_lick

	def notify(self, event):
		text = event.data['text']

		name_str = "%s:" % event.data['connection'].session.name
		#TODO: This must all be cleaned up
		if not text.startswith(name_str):
			if log.isEnabledFor(logging.DEBUG): log.debug("Not a message from me! (%s)" % name_str)
			if log.isEnabledFor(logging.DEBUG): log.debug("Found: %d" % (text.find(':') + 1))
			person = text[:text.find(':')]
			text = text[text.find(':') + 2:]
			if log.isEnabledFor(logging.DEBUG): log.debug("is message for me: (%s) %s" % (text, text.lower().startswith("%s," % name_str[0].lower())))
			if text.lower().startswith("%s," % name_str[0].lower()):
				words = text[text.find(",") + 1:].split()
				if log.isEnabledFor(logging.DEBUG): log.debug("Data; %s" % text)
				if log.isEnabledFor(logging.DEBUG): log.debug("Words for commands: %s" % words)
				if len(words) >= 1 and words[0].upper() in self.commands:
					if log.isEnabledFor(logging.DEBUG): log.debug("Found command '%s', executing" % words[0].upper())
					# data[1] is the params onwards to the command
					packets = self.commands[words[0].upper()](event.data['connection'].session, person, words)
					for packet in packets:
						event.data['connection'].send(packet)

	def get_event_types(self):
		return self.event_types

	def subscribe_event(self, event):
		pass

	def __str__(self):
		return repr("RawTextHandler.types=%s" % self.event_types)
	
	def _do_who(self, session, person, params):
		packets = []
		actors_str = ""
		for actor in session.actors.values():
			actors_str += "%s, " % actor
		actors_strs = split_str(actors_str, 157)
		packets = []
		for part in actors_strs:
			packets.append(ELPacket(ELNetToServer.RAW_TEXT, part))
		return packets

	def _do_hi(self, session, person, params):
		return [ELPacket(ELNetToServer.RAW_TEXT, "Hi there, %s :D" % person)]

	def _do_time(self, session, person, params):
		return [ELPacket(ELNetToServer.RAW_TEXT, "%s: %s" % (person, time.asctime()))]

	def _do_lick(self, session, person, params):
		print params
		if len(params) > 1:
			return [ELPacket(ELNetToServer.RAW_TEXT, ":licks %s" % params[1])]
		else:
			return [ELPacket(ELNetToServer.RAW_TEXT, "...I'm not going to lick the air...")]
