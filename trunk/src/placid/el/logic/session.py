"""Sessions represent the information we recored while logged-in to an EL server
"""

import ConfigParser

class Session(object):
	"""A basic session object"""

	def __init__(self, config):
		"""assign this session's config"""
		self.config = config
	
	def get_login_messages(self):
		"""returns a list of strings from the config for all login messages"""
		return self.config.get('messages', 'login').split('|')
	
	def get_logout_messages(self):
		"""returns a list of strings from the config for all logout messages"""
		return self.config.get('messages', 'logout').split('|')

class ELSession(Session):
	"""An EL-specific session"""
	
