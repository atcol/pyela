import collections
import logging

log = logging.getLogger('placid.net.packethandlers')

class BasePacketHandler(object):
	"""The base packet handler type.
	
	Attributes:
		_inp	- an instance of collections.deque
		_opt	- an instance of collections.deque
	"""
	
	def __init__(self):
		self._inp = collections.deque()
		self._opt = collections.deque()
		
	def process_packets(self, packets):
		"""Reads the packets in packets and
		places responses in the output queue
		"""
		pass

	def get_opt_packets(self):
		"""Return the packets eligable for output"""
		return self._opt
	
	def opt_queue_shift(self):
		"""Send the first packet in self._opt, and remove it
		from the queue
		"""
		if len(self._opt) > 0:
			p =  self._opt.popleft()
			log.debug("packet handler popped %s from queue" % p)
			return p
