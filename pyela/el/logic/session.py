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
"""Sessions represent the information we recored while logged-in to an EL server
"""

from pyela.el.net.elconstants import ELNetToServer, ELConstants
from pyela.el.net.packets import ELPacket
import struct

def get_elsession_by_config(config):
	"""Load all relevant configuration and message values from the given
	ConfigParser instance and construct an ELSession instance to return
	"""
	return ELSession(config.get('login', 'username'), \
		config.get('login', 'password'), \
		config.get('messages', 'login').split('|'), \
		config.get('messages', 'logout').split('|'))

class Session(object):
	"""A basic session object"""

	def __init__(self, username, password, login_msgs=[], logout_msgs=[]):
		"""
		Assign username, password and optional login and logout messages
		"""
		self.name = username
		self.password = password
		self.login_msgs = login_msgs
		self.logout_msgs = logout_msgs
	
	def get_login_messages(self):
		"""returns a list of strings from the config for all login messages"""
		return self.login_msgs
	def get_logout_messages(self):
		"""returns a list of strings from the config for all logout messages"""
		return self.logout_msgs

class ELSession(Session):
	"""An EL-specific session that 
	contains non-persistent information collected since logon, such as
	actors, ignores, channels, etc.
	"""

	def __init__(self, username, password, login_msgs=[], logout_msgs=[]):
		super(ELSession, self).__init__(username, password, login_msgs, logout_msgs)
		self.actors = {}
		self.channels = []
		self.buddies = []
		self.own_actor_id = -1
		self.own_actor = None
		self.game_time = 0 # The ingame time, hour given by int(.gametime/360) and minute by .gametime%360
		self.current_map = ""
	
	def add_actor(self, actor):
		self.actors.append(actor)
	
	#TODO: Consider adding a channel manager class for all the below methods:
	def add_channel(self, channel):
		self.channels.append(channel)
	
	def get_channel_pos(self, channel):
		"""Return the channel's position in the channel list (1, 2 or 3).
		Returns -1 if the channel is not found."""
		i = 1
		for ch in self.channels:
			if ch.number == int(channel):
				return i
			i += 1
		return -1
	
	def get_channel_by_num(self, num):
		"""Look up channel by its number, returns None if not found"""
		for ch in self.channels:
			if ch.number == num:
				return ch
		return None
	
	def get_active_channel(self):
		"""return the active channel from self.channels"""
		for ch in self.channels:
			if ch.is_active:
				return ch
		return None
	
	def set_active_channel(self, channel):
		"""Changes the .active properties for the channels in the channel list and
		   sends the new info to the server.
		   
		   Arguments: channel: The channel to become active (type Channel)"""
		if channel.is_active:
			return
		pos = self.get_channel_pos(channel.number)
		#Calculate the channel ID from the position in the list and notify the server of the change
		data = struct.pack('B', pos-1+ELConstants.CHAT_CHANNEL1)
		channel.connection.send(ELPacket(ELNetToServer.SET_ACTIVE_CHANNEL, data))
		#Update the local list
		for c in self.channels:
			if c.number == channel.number:
				c.is_active = True
			else:
				c.is_active = False
