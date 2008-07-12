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
		places responses in the output queue.
		Depending on the packets,
		a list of Event objects may be returned.
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
