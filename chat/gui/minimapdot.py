# Copyright 2011 Pyela Project
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

class MinimapDot:
	"""MinimapDot represents a dot on the minimap"""
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.size = 1 # The size of a dot (in tiles)
		self.colour = (1, 0, 0) # RGB colours
		self.text = None # The "name" of the dot
		self.minimap = None
