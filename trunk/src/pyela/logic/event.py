"""Objects and methods relating to events within the framework"""

class Event(object):
	"""Represents an action or occurance of actions within the framework.
	Used in an event-driven manner within the PacketHandlers
	"""

	def __init__(self, data=None):
		"""Construct a basic event object with the optional 
		data"""
		self.data = data
