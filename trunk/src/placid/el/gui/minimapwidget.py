# Copyright 2008 Vegar Storvann
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

import pygtk
pygtk.require('2.0')
import gtk
import math


class MinimapDot:
	"""MinimapDot represents a dot on the minimap"""
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.size = 1 #The size of a dot (in tiles)
		self.colour = (1, 0, 0) #RGB colours
		self.text = None
		self.minimap = None

class Minimap(gtk.DrawingArea):
	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.add_events(gtk.gdk.SCROLL_MASK)
		self.connect("expose_event", self.expose)
		self.connect("scroll_event", self.mouse_scroll)
		self.dots = []#[MinimapDot(0, 0), MinimapDot(20, 0), MinimapDot(0,-1), MinimapDot(-6,-6)]
		#self.dots[0].colour = (0,0,1)
		#self.dots[0].text = "YOURSELF!"
		self.view_radius = 30 #Number of tiles we see in any direction
		self.max_view_radius = 50 #The maximum number of tiles we can scroll to see
		self.min_view_radius = 3 #Minimum number of tiles we can scroll to see
		self.own_x = 0 #Your own X and Y coordinates
		self.own_y = 0
	
	def expose(self, widget, event):
		"""Expose event handler"""
		self.context = widget.window.cairo_create()
		self.context.rectangle(event.area.x, event.area.y,
								event.area.width, event.area.height)
		self.context.clip()
		self.draw(self.context)
		return False
	
	def mouse_scroll(self, widget, event):
		"""Scroll event handler, zooms the minimap"""
		if event.direction == gtk.gdk.SCROLL_UP:
			self.view_radius -= 1
			if self.view_radius < self.min_view_radius:
				self.view_radius = self.min_view_radius
		elif event.direction == gtk.gdk.SCROLL_DOWN:
			self.view_radius += 1
			if self.view_radius > self.max_view_radius:
				self.view_radius = self.max_view_radius
		self.redraw_canvas()
	
	def redraw_canvas(self):
		"""Force a redraw of the canvas"""
		if self.window:
			alloc = self.get_allocation()
			rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
			self.window.invalidate_rect(rect, True)
			self.window.process_updates(True)
	
	def draw(self, context):
		#First some initial calculations
		rect = self.get_allocation()
		center_x = rect.width/2
		center_y = rect.height/2
		radius = min(rect.width/2, rect.height/2)-2
		map_to_screen_ratio = float(radius)/self.view_radius

		#Draw the big circle
		context.arc(center_x, center_y, radius, 0, 2*math.pi)
		context.set_source_rgb(0.2,0.8,0.1)
		context.fill_preserve()
		context.set_source_rgb(0,0,0)
		context.stroke()

		#Now draw all the blips on the map
		for dot in self.dots:
			x = center_x+int((dot.x-self.own_x)*map_to_screen_ratio)
			y = center_y-int((dot.y-self.own_y)*map_to_screen_ratio) #Minus here because EL's y-axis and cairo's y-axis are inverted
			if math.sqrt((dot.x-self.own_x)*(dot.x-self.own_x)+(dot.y-self.own_y)*(dot.y-self.own_y)) <= self.view_radius:
				context.arc(x, y, float(dot.size)/2*map_to_screen_ratio, 0, 2*math.pi)
				context.set_source_rgb(dot.colour[0], dot.colour[1], dot.colour[2])
				context.fill()
	
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

# Copyright 2008 Vegar Storvann
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

import pygtk
pygtk.require('2.0')
import gtk
import math


class MinimapDot:
	"""MinimapDot represents a dot on the minimap"""
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.size = 1 #The size of a dot (in tiles)
		self.colour = (1, 0, 0) #RGB colours
		self.text = None
		self.minimap = None

class Minimap(gtk.DrawingArea):
	def __init__(self):
		gtk.DrawingArea.__init__(self)
		self.add_events(gtk.gdk.SCROLL_MASK)
		self.connect("expose_event", self.expose)
		self.connect("scroll_event", self.mouse_scroll)
		self.dots = []#[MinimapDot(0, 0), MinimapDot(20, 0), MinimapDot(0,-1), MinimapDot(-6,-6)]
		#self.dots[0].colour = (0,0,1)
		#self.dots[0].text = "YOURSELF!"
		self.view_radius = 30 #Number of tiles we see in any direction
		self.max_view_radius = 50 #The maximum number of tiles we can scroll to see
		self.min_view_radius = 3 #Minimum number of tiles we can scroll to see
		self.own_x = 0 #Your own X and Y coordinates
		self.own_y = 0
	
	def expose(self, widget, event):
		"""Expose event handler"""
		self.context = widget.window.cairo_create()
		self.context.rectangle(event.area.x, event.area.y,
								event.area.width, event.area.height)
		self.context.clip()
		self.draw(self.context)
		return False
	
	def mouse_scroll(self, widget, event):
		"""Scroll event handler, zooms the minimap"""
		if event.direction == gtk.gdk.SCROLL_UP:
			self.view_radius -= 1
			if self.view_radius < self.min_view_radius:
				self.view_radius = self.min_view_radius
		elif event.direction == gtk.gdk.SCROLL_DOWN:
			self.view_radius += 1
			if self.view_radius > self.max_view_radius:
				self.view_radius = self.max_view_radius
		self.redraw_canvas()
	
	def redraw_canvas(self):
		"""Force a redraw of the canvas"""
		if self.window:
			alloc = self.get_allocation()
			rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
			self.window.invalidate_rect(rect, True)
			self.window.process_updates(True)
	
	def draw(self, context):
		#First some initial calculations
		rect = self.get_allocation()
		center_x = rect.width/2
		center_y = rect.height/2
		radius = min(rect.width/2, rect.height/2)-2
		map_to_screen_ratio = float(radius)/self.view_radius

		#Draw the big circle
		context.arc(center_x, center_y, radius, 0, 2*math.pi)
		context.set_source_rgb(0.2,0.8,0.1)
		context.fill_preserve()
		context.set_source_rgb(0,0,0)
		context.stroke()

		#Now draw all the blips on the map
		for dot in self.dots:
			x = center_x+int((dot.x-self.own_x)*map_to_screen_ratio)
			y = center_y-int((dot.y-self.own_y)*map_to_screen_ratio) #Minus here because EL's y-axis and cairo's y-axis are inverted
			if math.sqrt((dot.x-self.own_x)*(dot.x-self.own_x)+(dot.y-self.own_y)*(dot.y-self.own_y)) <= self.view_radius:
				context.arc(x, y, float(dot.size)/2*map_to_screen_ratio, 0, 2*math.pi)
				context.set_source_rgb(dot.colour[0], dot.colour[1], dot.colour[2])
				context.fill()
	
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

