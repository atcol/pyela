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

from gi.repository import Gtk, Gdk
import math
from pyela.logic.eventhandlers import BaseEventHandler
from pyela.el.logic.events import ELEventType
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.net.elconstants import ELNetFromServer
from logic.eventhandler import MinimapEventHandler

class Minimap(Gtk.DrawingArea):
	def __init__(self):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.SCROLL_MASK)
		self.connect("draw", self.draw)
		self.connect("scroll-event", self.mouse_scroll)
		self.connect("query-tooltip", self.tooltip)
		self.set_property("has-tooltip", True)
		self.dots = []
		self.view_radius = 30 #Number of tiles we see in any direction
		self.max_view_radius = 50 #The maximum number of tiles we can scroll to see
		self.min_view_radius = 3 #Minimum number of tiles we can scroll to see
		self.own_x = 0 #Your own X and Y coordinates
		self.own_y = 0
		ELSimpleEventManager().add_handler(MinimapEventHandler(self))
	
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
		self.redraw_canvas()
	
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
		"""Converts the given EL ingame coordinates to cairo coordinates
			Returns a tuple with the converted x,y pair"""
		rect = self.get_allocation()
		center_x = rect.width/2
		center_y = rect.height/2
		radius = min(rect.width/2, rect.height/2)-2 #Radius of the minimap area, -2 to make room for the border
		map_to_screen_ratio = self._get_map_to_screen_ratio()
		
		#Minus in the y calculation because EL's y-axis and cairo's y-axis are inverted
		return (center_x+int((x-self.own_x)*map_to_screen_ratio), center_y-int((y-self.own_y)*map_to_screen_ratio))
	
	def _get_map_to_screen_ratio(self):
		rect = self.get_allocation()
		radius = min(rect.width/2, rect.height/2)-2
		return float(radius)/self.view_radius
	
	def redraw_canvas(self):
		"""Force a redraw of the canvas"""
		#http://developer.gnome.org/gtk3/stable/GtkWidget.html#gtk-widget-queue-draw-region
		window = self.get_property('window')
		if window:
			alloc = self.get_allocation()
			rect = Gdk.Rectangle()
			rect.x = 0
			rect.y = 0
			rect.width = alloc.width
			rect.height = alloc.height
			window.invalidate_rect(rect, True)
			window.process_updates(True)
	
	def draw(self, widget, context):
		#First some initial calculations
		rect = self.get_allocation()
		center_x = rect.width/2
		center_y = rect.height/2
		radius = min(rect.width/2, rect.height/2)-2
		map_to_screen_ratio = self._get_map_to_screen_ratio()

		#Draw the big circle
		context.arc(center_x, center_y, radius, 0, 2*math.pi)
		context.set_source_rgb(0.2,0.8,0.1) #Green
		context.fill_preserve()
		context.set_source_rgb(0,0,0)
		context.stroke()

		#Now draw all the blips on the map
		for dot in self.dots:
			x, y = self._game_coords_to_minimap_coords(dot.x, dot.y)
			if math.sqrt((dot.x-self.own_x)**2+(dot.y-self.own_y)**2) <= self.view_radius:
				#Blip is within seeable range
				context.arc(x, y, float(dot.size)/2*map_to_screen_ratio, 0, 2*math.pi)
				context.set_source_rgb(dot.colour[0], dot.colour[1], dot.colour[2])
				context.fill()
		return False
	
	def set_own_pos(self, x, y):
		self.own_x = x
		self.own_y = y
		self.redraw_canvas()
	
	def add_dot(self, dot):
		"""Adds a dot to the minimap"""
		dot.minimap = self
		self.dots.append(dot)
		self.redraw_canvas()

	def del_dot(self, dot):
		self.dots.remove(dot)
		self.redraw_canvas()
	
	def del_all_dots(self):
		del self.dots[:]
		self.redraw_canvas()

