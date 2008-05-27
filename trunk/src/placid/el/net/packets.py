
class Packet(object):
	"""Represents a TCP network packet"""
	def __init__():
		pass

class ELPacket(Packet):
	"""Represents an Eternal Lands network packet"""
		
	def __init__(self, type, data):
		self.type = type
		self.data = data
	
	def pack(self):
		"""Converts the data ready for transmission"""
		pass

	def unpack(self):
		"""Unpacks the data into a readable form"""
