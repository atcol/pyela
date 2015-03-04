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

from gi.repository import Gtk as gtk

from pyela.el.net.elconstants import ELConstants, ELNetFromServer
from pyela.el.logic.events import ELEventType
from pyela.logic.eventhandlers import BaseEventHandler
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.util.strings import is_colour
from pyela.logic.event import NetEventType, NET_CONNECTED, NET_DISCONNECTED
from gui.colours import parse_el_colours

class ChatGUIEventHandler(BaseEventHandler):
	def __init__(self, gui):
		self.gui = gui
		self.event_types = [
				ELEventType(ELNetFromServer.RAW_TEXT),
				ELEventType(ELNetFromServer.GET_ACTIVE_CHANNELS),
				ELEventType(ELNetFromServer.BUDDY_EVENT),
				ELEventType(ELNetFromServer.LOG_IN_NOT_OK),
				ELEventType(ELNetFromServer.YOU_DONT_EXIST),
				ELEventType(ELNetFromServer.NEW_MINUTE),
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
				self.gui.append_chat("\n")
				raw_text = event.data['raw']
				coloured_text = parse_el_colours(raw_text, self.gui.gtk_el_colour_table)
				if event.data['channel'] in (ELConstants.CHAT_CHANNEL1, ELConstants.CHAT_CHANNEL2, ELConstants.CHAT_CHANNEL3):
					tag,text = coloured_text.pop(0)
					channel_pos = int(event.data['channel'])
					channel_num = self.gui.elc.session.channels[int(channel_pos - ELConstants.CHAT_CHANNEL1)].number
					channel_str = " @ {}]".format(channel_num)
					self.gui.append_chat([text.replace(']', channel_str, 1)], tag)
				for tag,text in coloured_text:
					self.gui.append_chat([text], tag)
				#Check for PM
				text = event.data['text']
				if len(text) > 12 and text[:9] == "[PM from ":
					name_end = text[9:].find(':')
					if name_end != -1:
						self.gui.last_pm_from = text[9:9+name_end]
			elif event.type.id == ELNetFromServer.GET_ACTIVE_CHANNELS:
				#Just rebuild the GUI channel list
				self.gui.tool_vbox.rebuild_channel_list(event.data['channels'])
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
									gtk.DialogFlags.MODAL, gtk.MessageType.ERROR, 
									gtk.ButtonsType.CLOSE, "Login failed")
				alert.format_secondary_text(msg)
				alert.run()
				alert.destroy()
				self.gui.do_login()
			elif event.type.id == ELNetFromServer.NEW_MINUTE:
				self.gui.tool_vbox.clock_lbl.set_text("Time: %d:%02d" % (int(event.data['time']/60), event.data['time']%60))

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
				actor.dot.name = actor.name
				if actor.guild != None:
					actor.dot.name += " %s" % actor.guild
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
