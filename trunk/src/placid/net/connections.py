from placid.logic.packethandlers import BasePacketHandler

class BaseConnection(object):
	"""Base connection class that defines common functionality for TCP connections"""

	def __init__(self):
		self.packet_handler = BasePacketHandler()

	def fileno(self):
		"""Return the fileno for this connection's socket"""
		pass
	
	def is_connected(self):
		"""Are we connected?"""
		pass

	def connect(self):
		"""Connects to a remote server"""
		pass
	
	def reconnect(self):
		"""Disconnects then reconnects"""
		pass

	def disconnect(self):
		"""Closes the connection gracefully"""
		pass

	def keep_alive(self):
		"""Send the protocol-relevant packet that tells the server we're still alive"""
		pass

	def send(self, packet):
		"""sends the given packet to the remote server"""
		pass

	def send_all(self, packets):
		"""Send all of the ELPacket instances in the list packets"""
		pass
	
	def recv(self, length=2048):
		"""process input and convert to an instance of placid.el.net.packets.Packet"""
		pass

	def process_packets(self, packets):
		"""Passes the given packets to the underlying packet handler if present."""
		self.packet_handler.process_packets(packets)

	def process_queue(self):
		"""Process this connection's output queue, if present
		By default, this will retrieve its output queue from
		self.packet_handler.opt_queue_shift()
		"""
		while True:
			p = self.packet_handler.opt_queue_shift()
			if not p:
				break
			else:
				self.send(p)
