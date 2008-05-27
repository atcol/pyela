"""Various exceptions pertaining to...exception circumstances at runtime"""

class BaseException(Exception):
	def __init__(self, val):
		self.value = val

	def __str__(self):
		return repr(self.value)

class ConnectionException(BaseException):
	pass

class ManagerException(BaseException):
	pass
	
