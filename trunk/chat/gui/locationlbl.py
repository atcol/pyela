# Copyright 2011 Vegar Storvann
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

from gi.repository import Gtk, Pango
from pyela.el.net.elconstants import ELNetToServer, ELNetFromServer, ELConstants
from pyela.el.net.packets import ELPacket
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.logic.events import ELEventType
from pyela.logic.eventhandlers import BaseEventHandler

class LocationLbl(Gtk.Label):
	def __init__(self, main_window):
		super(LocationLbl, self).__init__("??")
		self.main_window = main_window
		self.set_line_wrap(True)
		self.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
		self.set_max_width_chars(10)
		ELSimpleEventManager().add_handler(LocationLblEventHandler(self))
	def update(self):
		self.main_window.elc.send(ELPacket(ELNetToServer.LOCATE_ME, None))

class LocationLblEventHandler(BaseEventHandler):
	def __init__(self, label):
		self.label = label
		self.event_types = [ELEventType(ELNetFromServer.CHANGE_MAP), ELEventType(ELNetFromServer.RAW_TEXT)]

	def notify(self, event):
		if event.type.id == ELNetFromServer.RAW_TEXT:
			if event.data['raw'][0] == ELConstants.C_GREEN1+127 and event.data['text'][:11] == 'You are in ':
				location = event.data['text'][11:]
				location = location.replace("  ", " ") #remove double spaces
				self.label.set_text(location)
		elif event.type.id == ELNetFromServer.CHANGE_MAP:
			self.label.update()

	def get_event_types(self):
		return self.event_types
