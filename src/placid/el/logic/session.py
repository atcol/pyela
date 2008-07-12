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

import ConfigParser

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
		self.msg_buf = []# global messages
	
	def get_login_messages(self):
		"""returns a list of strings from the config for all login messages"""
		return self.login_msgs
	def get_logout_messages(self):
		"""returns a list of strings from the config for all logout messages"""
		return self.logout_msgs

class ELSession(Session):
	"""An EL-specific session that 
	contains non-persistent information collected since logon, such as
	actors, ignores, channels etc
	"""

	def __init__(self, username, password, login_msgs=[], logout_msgs=[]):
		super(ELSession, self).__init__(username, password, login_msgs=[], logout_msgs=[])
		self.actors = {}
		self.channels = []
		self.buddies = []
	
	def add_actor(self, actor):
		self.actors.append(actor)
	
	def get_active_channel(self):
		"""return the active channel from self.channels"""
		for ch in self.channels:
			if ch.is_active:
				return ch
		return None
	
	def add_channel(self, channel):
		self.channels.append(channel)
