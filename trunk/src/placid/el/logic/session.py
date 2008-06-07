"""Sessions represent the information we recored while logged-in to an EL server
"""

import ConfigParser

class Session(object):
	"""A basic session object"""

	def __init__(self, config):
		"""assign this session's config and load properties from the given
		configuration file
		"""
		self.load_config(config)
	
	def load_config(self, config):
		"""Load all relevant configuration and message values from the given
		ConfigParser instance and reassign, or reload from self.config if no 
		ConfigParser instance is given
		"""
		self.config = config
		self.name = self.config.get('login', 'username')
		self.password = self.config.get('login', 'password')
		self.login_msgs = self.config.get('messages', 'login').split('|')
		self.logout_msgs = self.config.get('messages', 'logout').split('|')
	
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

	def __init__(self, config):
		super(ELSession, self).__init__(config)
		self.actors = {}
