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
	
	def add_actor(self, actor):
		self.actors.append(actor)
