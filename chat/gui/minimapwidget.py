# Copyright 2008, 2011 Pyela project
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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QSize, QPointF
import math
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from logic.eventhandler import MinimapEventHandler

class Minimap(QWidget):
	def __init__(self):
		super().__init__()
		self.minimumSizeHint = QSize(50, 50)
		self.border_width = 2  # Border of minimap circle
		# self.add_events(Gdk.EventMask.SCROLL_MASK)
		# self.connect("scroll-event", self.mouse_scroll)
		# self.connect("query-tooltip", self.tooltip)
		# self.set_property("has-tooltip", True)
		self.dots = []
		self.view_radius = 30 #Number of tiles we see in any direction
		self.max_view_radius = 50 #The maximum number of tiles we can scroll to see
		self.min_view_radius = 3 #Minimum number of tiles we can scroll to see
		self.own_x = 0 #Your own X and Y coordinates
		self.own_y = 0
		ELSimpleEventManager().add_handler(MinimapEventHandler(self))

	def paintEvent(self, e):
		map_to_screen_ratio = self._get_map_to_screen_ratio()
		# Widget size
		width = self.size().width()
		height = self.size().height()
		# Diameter of circle
		diameter = min(width, height)-self.border_width
		# Create painter
		qp = QPainter(self)
		qp.setRenderHint(QPainter.Antialiasing)

		# Draw green circle
		green = QColor(0.2*255, 0.8*255, 0.1*255)
		pen = QPen()
		pen.setWidth(self.border_width)
		qp.setBrush(green)
		qp.setPen(pen)
		qp.drawEllipse(int(self.border_width/2), int(self.border_width/2), diameter, diameter)

		# Now draw all the blips on the map
		for dot in self.dots:
			x, y = self._game_coords_to_minimap_coords(dot.x, dot.y)
			if math.sqrt((dot.x-self.own_x)**2+(dot.y-self.own_y)**2) <= self.view_radius:
				# Blip is within seeable range
				# Set drawing style
				colour = QColor(dot.colour[0]*255, dot.colour[1]*255, dot.colour[2]*255)
				qp.setBrush(colour)
				pen.setWidth(0)
				pen.setColor(colour)
				qp.setPen(pen)
				# Draw
				centre = QPointF(x, y)
				dot_radius = float(dot.size)/2*map_to_screen_ratio
				qp.drawEllipse(centre, dot_radius, dot_radius)
	
	def mouse_scroll(self, widget, event):
		"""Scroll GTK event handler, zooms the minimap"""
		if event.direction == Gdk.ScrollDirection.UP:
			self.view_radius -= 1
			if self.view_radius < self.min_view_radius:
				self.view_radius = self.min_view_radius
		elif event.direction == Gdk.ScrollDirection.DOWN:
			self.view_radius += 1
			if self.view_radius > self.max_view_radius:
				self.view_radius = self.max_view_radius
		self.update()
	
	def tooltip(self, widget, x, y, keyboard_mode, tooltip):
		if keyboard_mode:
			return False
		dot = self._get_dot_near_position(x, y)
		if dot == None:
			return False
		tooltip.set_text(dot.name)
		return True
	
	def _get_dot_near_position(self, x, y):
		"""Returns the dot that is covering the given coordinates on the minimap"""
		map_to_screen_ratio = self._get_map_to_screen_ratio()
		for dot in self.dots:
			dot_size = float(dot.size)/2*map_to_screen_ratio
			dot_x,dot_y = self._game_coords_to_minimap_coords(dot.x, dot.y)
			if math.floor(math.sqrt((dot_x-x)**2+(dot_y-y)**2)) <= dot_size:
				return dot
		return None

	def _game_coords_to_minimap_coords(self, x, y):
		"""Converts the given EL ingame coordinates to Qt widget coordinates
			Returns a tuple with the converted x,y pair"""
		center_x = self.size().width()/2
		center_y = self.size().height()/2
		map_to_screen_ratio = self._get_map_to_screen_ratio()
		
		# Minus in the y calculation because EL's y-axis and cairo's y-axis are inverted
		return (center_x+int((x-self.own_x)*map_to_screen_ratio), center_y-int((y-self.own_y)*map_to_screen_ratio))
	
	def _get_map_to_screen_ratio(self):
		radius = min(self.size().width()/2, self.size().height()/2)-self.border_width
		return float(radius)/self.view_radius
	
	def set_own_pos(self, x, y):
		self.own_x = x
		self.own_y = y
		self.update()
	
	def add_dot(self, dot):
		"""Adds a dot to the minimap"""
		dot.minimap = self
		self.dots.append(dot)
		self.update()

	def del_dot(self, dot):
		self.dots.remove(dot)
		self.update()
	
	def del_all_dots(self):
		del self.dots[:]
		self.update()