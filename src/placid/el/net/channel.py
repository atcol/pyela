"""Represents an in-game channel"""

class Channel(object):
	def __init__(self, number, is_active):
		self.number = number
		self.is_active = is_active
