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
	
	def __str__(self):
		return "ELPacket: %s - %s" % (self.type, self.data)
