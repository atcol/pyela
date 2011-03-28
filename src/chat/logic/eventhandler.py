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

import pygtk
import gtk
import gobject

from pyela.el.net.elconstants import ELConstants, ELNetFromServer
from pyela.el.logic.events import ELEventType
from pyela.logic.eventhandlers import BaseEventHandler
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.util.strings import el_str_to_str, is_colour
from pyela.logic.event import NetEventType, NET_CONNECTED, NET_DISCONNECTED

class ChatGUIEventHandler(BaseEventHandler):
	def __init__(self, gui):
		self.gui = gui
		self.event_types = [
				ELEventType(ELNetFromServer.RAW_TEXT),
				ELEventType(ELNetFromServer.GET_ACTIVE_CHANNELS),
				ELEventType(ELNetFromServer.BUDDY_EVENT),
				ELEventType(ELNetFromServer.LOG_IN_NOT_OK),
				ELEventType(ELNetFromServer.YOU_DONT_EXIST),
				NetEventType(NET_CONNECTED),
				NetEventType(NET_DISCONNECTED)]

	def notify(self, event):
		if isinstance(event.type, NetEventType):
			if event.type.id == NET_DISCONNECTED:
				self.gui._unregister_socket_io_watch()
			elif event.type.id == NET_CONNECTED:
				# assign the fd of our elconnection to gtk
				self.gui._register_socket_io_watch()

		elif isinstance(event.type, ELEventType):
			if event.type.id == ELNetFromServer.RAW_TEXT:
				#TODO: Proper colour handling, see http://python.zirael.org/e-gtk-textview2.html for examples
				self.gui.append_chat("\n")
				text = el_str_to_str(event.data['raw'])
				if is_colour(text[0]):
					colour_code = ord(text[0])-127
					tag = self.gui.gtk_el_colour_table[colour_code]
				else:
					tag = None
				#Get rid of colour codes now that the colour information has been extracted
				text = event.data['text']
				if event.data['channel'] in (ELConstants.CHAT_CHANNEL1, ELConstants.CHAT_CHANNEL2, ELConstants.CHAT_CHANNEL3):
					channel = int(event.data['channel'])
					self.gui.append_chat([text.replace(']', " @ %s]" % self.gui.elc.session.channels[int(channel - ELConstants.CHAT_CHANNEL1)].number)], tag)
				else:
					self.gui.append_chat([event.data['text']], tag)
			elif event.type.id == ELNetFromServer.GET_ACTIVE_CHANNELS:
				self.gui.tool_vbox.channel_list.clear()
				for chan in self.gui.elc.session.channels:
					self.gui.tool_vbox.channel_list.append(["%s" % chan.number])
			elif event.type.id == ELNetFromServer.BUDDY_EVENT:
				self.gui.tool_vbox.buddy_list.clear()
				for buddy in self.gui.elc.session.buddies:
					self.gui.tool_vbox.buddy_list.append([buddy])
			elif event.type.id in (ELNetFromServer.LOG_IN_NOT_OK, ELNetFromServer.YOU_DONT_EXIST):
				if event.type.id == ELNetFromServer.LOG_IN_NOT_OK:
					msg = event.data['text']
				else:
					msg = "Incorrect username."
				self.gui.append_chat([msg])
				self.gui.elc.disconnect()
				alert = gtk.MessageDialog(self.gui, 
									gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, 
									gtk.BUTTONS_CLOSE, "Login failed")
				alert.format_secondary_text(msg)
				alert.run()
				alert.destroy()
				self.gui.do_login()

	def get_event_types(self):
		return self.event_types

from gui.minimapdot import MinimapDot

class MinimapEventHandler(BaseEventHandler):
	"""Event handler for the minimap widget"""
	def __init__(self, minimap):
		self.minimap = minimap
		self.event_types = [ELEventType(ELNetFromServer.ADD_NEW_ACTOR),
				ELEventType(ELNetFromServer.REMOVE_ACTOR),
				ELEventType(ELNetFromServer.KILL_ALL_ACTORS),
				ELEventType(ELNetFromServer.ADD_ACTOR_COMMAND),
				ELEventType(ELNetFromServer.YOU_ARE),
				NetEventType(NET_CONNECTED)]
	
	def notify(self, event):
		if isinstance(event.type, NetEventType):
			if event.type.id == NET_CONNECTED:
				# Reset the minimap when we get a new network connection
				self.minimap.del_all_dots()
		elif isinstance(event.type, ELEventType):
			if event.type.id == ELNetFromServer.ADD_NEW_ACTOR:
				actor = event.data
				if actor.id == self.minimap.el_session.own_actor_id:
					self.minimap.set_own_pos(actor.x_pos, actor.y_pos)
				actor.dot = MinimapDot(actor.x_pos, actor.y_pos)
				actor.dot.colour = actor.name_colour
				self.minimap.add_dot(actor.dot)
			elif event.type.id == ELNetFromServer.REMOVE_ACTOR:
				actor = event.data['actor']
				self.minimap.del_dot(actor.dot)
			elif event.type.id == ELNetFromServer.KILL_ALL_ACTORS:
				self.minimap.del_all_dots()
			elif event.type.id == ELNetFromServer.ADD_ACTOR_COMMAND:
				actor = event.data['actor']
				actor.dot.x = actor.x_pos
				actor.dot.y = actor.y_pos
				if actor.id == self.minimap.el_session.own_actor_id:
					self.minimap.set_own_pos(actor.x_pos, actor.y_pos)
				self.minimap.redraw_canvas()
			elif event.type.id == ELNetFromServer.YOU_ARE:
				actor = event.data
				self.minimap.set_own_pos(actor.x_pos, actor.y_pos)
	
	def get_event_types(self):
		return self.event_types
