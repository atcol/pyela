# Copyright 2008, 2011 Pyela Project
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
import gobject
import struct
import sys

from pyela.el.net.elconstants import ELNetToServer, ELConstants
from pyela.el.net.connections import ELConnection, DISCONNECTED
from pyela.el.net.packets import ELPacket
from pyela.el.net.packethandlers import ExtendedELPacketHandler
from pyela.el.common.exceptions import ConnectionException
from pyela.el.logic.session import ELSession
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.util.strings import el_colour_char_table, el_str_to_str
from gui.login import LoginGUI
from gui.minimapwidget import Minimap
from gui.networking_error import NetworkingErrorAlert

from logic.eventhandler import ChatGUIEventHandler

class ChatGUI(gtk.Window):
	def __init__(self):
		self.msg_buff = [] # list of messages, for CTRL+UP/UP and DOWN
		self.msgb_idx = 0
		self.last_key = None # for // name completion
		self.last_pm_to = ""
		self.elc = None
		self.g_watch_sources = []
		ELSimpleEventManager().add_handler(ChatGUIEventHandler(self))
		self.__setup_gui()
	
	def __setup_gui(self):
		self.elc = None

		gtk.Window.__init__(self)
		self.connect('destroy', self.destroy)
		self.connect('delete_event', self.destroy)
		self.set_size_request(645, 510)
		self.set_border_width(5)

		self.vbox = gtk.VBox(False, 0)

		self.chat_hbox = gtk.HBox(False, 0)

		#Add the chat area and put a frame around it
		self.chat_area = ChatArea()
		self.chat_area_frame = gtk.Frame()
		self.chat_area_frame.add(self.chat_area)
		self.chat_hbox.pack_start(self.chat_area_frame, True, True, 0)

		# add the chat & tool vbox to the chat hbox o,0
		self.tool_vbox = ToolVBox()
		self.tool_vbox.ch_toggle_ren.connect("toggled", self.__set_active_channel)
		self.tool_vbox.channel_tree.connect('row-activated', self.__chan_list_dclick)
		self.tool_vbox.buddy_tree.connect('row-activated', self.__buddy_list_dclick)
		self.vbox.pack_start(self.chat_hbox, True, True, 0)
		self.chat_hbox.pack_start(self.tool_vbox, False, False, 0)

		# setup the chat input & send button
		self.input_hbox = ChatInputHBox()
		self.input_hbox.msg_txt.connect('key_press_event', self.__input_keypress)
		self.input_hbox.send_btn.connect('clicked', self.send_msg)
		self.vbox.pack_start(self.input_hbox, False, False, 0)
		
		#Create the el->gtk colour map
		self.__build_colourtable()

		# show the login gui to get the user credentials
		self.do_login()

		# Add a timer to send the heart beats to the server
		gobject.timeout_add(15000, self.__keep_alive)

		self.chat_hbox.show_all()
		self.vbox.show_all()
		self.add(self.vbox)
		self.show_all()
		self.set_title("%s@%s:%s - Pyela Chat" % (self.elc.session.name, self.elc.host, self.elc.port))
		self.append_chat(['Welcome to Pyela-Chat, part of the Pyela toolset. Visit pyela.googlecode.com for more information'])
		self.input_hbox.msg_txt.grab_focus()
		
		self.connect('key_press_event', self.__main_keypress)

		# setup the channel list
		self.channels = []
		gtk.main()
	
	def __build_colourtable(self):
		"""Build a table of gtk textbuffer tags, mapping EL colour codes"""
		self.gtk_el_colour_table = {}
		for code,rgb in el_colour_char_table.items():
			hexcode = "#%02x%02x%02x" % (rgb[0]*255,rgb[1]*255,rgb[2]*255)
			if hexcode == "#ffffff":
				#White is invisible on our white background, so fix that
				hexcode = "#000000"
			self.gtk_el_colour_table[code] = self.chat_area.chat_buff.create_tag("el_colour_%i"%code, foreground=hexcode)

	def do_login(self):
		# Pass current values to the new login dialog, if there are any
		defaults = {}
		if self.elc != None:
			if self.elc.session != None and self.elc.session.name != None:
				defaults['user'] = self.elc.session.name
			defaults['port'] = self.elc.port
			defaults['host'] = self.elc.host
			
		l = LoginGUI(title="Login - Pyela Chat", parent=self, defaults=defaults)
		done = False

		# Loop while trying to connect so that we can display error messages
		while not done:
			response = l.run()
			if response == gtk.RESPONSE_OK:
				# login credentials entered
				if self.elc == None:
					# Initial login, setup the ELConnection
					session = ELSession(l.user_txt.get_text(), l.passwd_txt.get_text())
					self.elc = ELConnection(session, l.host_txt.get_text(), l.port_spin.get_value_as_int())
					self.elc.packet_handler = ExtendedELPacketHandler(self.elc)
				else:
					self.elc.session = ELSession(l.user_txt.get_text(), l.passwd_txt.get_text())
					self.elc.host = l.host_txt.get_text()
					self.elc.port = l.port_spin.get_value_as_int()
					self.elc.con_tries = 0
				self.tool_vbox.minimap.el_session = self.elc.session
				if not self.elc.connect():
					# Connection failed!
					alert = gtk.MessageDialog(l, 
								gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, 
								gtk.BUTTONS_CLOSE, "Connection failed")
					alert.format_secondary_text(self.elc.error)
					alert.run()
					alert.destroy()
					# Re-run the login dialog
				else:
					done = True
			else:
				# quit
				sys.exit(0)
		self.elc.socket.settimeout(15)
		l.destroy()
	
	def _register_socket_io_watch(self):
		# Assign the fd of our elconnection to gtk
		# 
		# The Windows implementation can only handle one IO watch per socket.
		# See the PyGTK FAQ entry "gobject.io_add_watch doesn't work with non-blocking sockets on win32!":
		# http://faq.pygtk.org/index.py?file=faq20.020.htp&req=show
		source = gobject.io_add_watch(self.elc.fileno(), gobject.IO_IN | gobject.IO_PRI | gobject.IO_ERR | gobject.IO_HUP, self.__socket_event)
		self.g_watch_sources.append(source)
	
	def _unregister_socket_io_watch(self):
		for s in self.g_watch_sources:
			gobject.source_remove(s)
		self.gobject_watch_sources = []

	def append_chat(self, msgs, tag = None):
		for msg in msgs:
			end = self.chat_area.chat_buff.get_end_iter()
			if tag != None:
				self.chat_area.chat_buff.insert_with_tags(end, msg, tag)
			else:
				self.chat_area.chat_buff.insert(end, msg)
		self.chat_area.chat_view.scroll_to_mark(self.chat_area.chat_buff.get_insert(), 0)

	def __input_keypress(self, widget, event=None):
		if event.keyval == gtk.keysyms.Return:
			self.send_msg(None, None)
			return True
		elif event.keyval == gtk.keysyms.Up:
			if self.msgb_idx == 0 and len(self.msg_buff) > 0:
				#This is the first up-keypress, store what's in the input box as the first entry in the buffer
				self.msg_buff.insert(0, self.input_hbox.msg_txt.get_text())
				self.msgb_idx = 1
				self.input_hbox.msg_txt.set_text(self.msg_buff[self.msgb_idx])
			elif self.msgb_idx > 0 and self.msgb_idx < len(self.msg_buff)-1:
				#Further browsing upwards in the buffer
				self.msgb_idx += 1
				self.input_hbox.msg_txt.set_text(self.msg_buff[self.msgb_idx])
			#Position the cursor at the end of the input
			self.input_hbox.msg_txt.set_position(self.input_hbox.msg_txt.get_text_length())
			return True
		elif event.keyval == gtk.keysyms.Down:
			if self.msgb_idx > 1:
				self.msgb_idx -= 1
				self.input_hbox.msg_txt.set_text(self.msg_buff[self.msgb_idx])
			elif self.msgb_idx == 1:
				#We're at the bottom of the buffer, restore what was initially in the input box and remove it from the list of input
				self.input_hbox.msg_txt.set_text(self.msg_buff.pop(0))
				self.msgb_idx = 0
			#Position the cursor at the end of the input
			self.input_hbox.msg_txt.set_position(self.input_hbox.msg_txt.get_text_length())
			return True
		return False
	
	def __main_keypress(self, widget, event=None):
		if event.state == gtk.gdk.CONTROL_MASK and event.keyval == gtk.keysyms.q:
			sys.exit(0)
	
	def send_msg(self, widget, data=None):
		msg = self.input_hbox.msg_txt.get_text()
		if msg != '':
			type = ELNetToServer.RAW_TEXT
			if self.input_hbox.msg_txt.get_text().startswith('/'):
				type = ELNetToServer.SEND_PM
				msg = self.input_hbox.msg_txt.get_text()[1:]
				
			self.elc.send(ELPacket(type, msg))
			self.input_hbox.msg_txt.set_text("")
			#input text buffer handling
			if self.msgb_idx > 0:
				#Remove any un-sent text from the input buffer
				self.msg_buff.pop(0)
			self.msgb_idx = 0
			self.msg_buff.insert(0, msg)
		return True
	
	def __keep_alive(self):
		"""keeps self.elc alive by calling its keep_alive function.
		This is called automatically every 15 seconds by the gobject API"""
		if self.elc.is_connected():
			self.elc.keep_alive()
		return True

	def __socket_event(self, fd, condition):
		if condition&(gobject.IO_ERR | gobject.IO_HUP):
			return self.__elc_error(fd, condition)
		elif condition&(gobject.IO_IN | gobject.IO_PRI):
			return self.__handle_socket_data(fd, condition)

	def __elc_error(self, fd, condition, msg = None):
		"""Called by gtk when an error with the socket occurs.
		May also be called by self.__process_packets, in which case msg is set"""
		err_str = "A networking error occured, please log in again"
		if msg != None:
			desc_str = msg
		else:
			desc_str = None
		self.append_chat(["\n", err_str])
		if self.elc.status != DISCONNECTED:
			# If .status is not DISCONNECTED, GTK has detected an error.
			# (We set .status to DISCONNECTED when it's detected by us)
			self.elc.disconnect()
		# Display the error message in a popup dialog, asking the user what to do
		alert = NetworkingErrorAlert(self, err_str, desc_str)
		response = alert.run()
		alert.destroy()
		if response == gtk.RESPONSE_REJECT:
			# Log in as other user
			self.do_login()
		elif response == gtk.RESPONSE_ACCEPT:
			# Reconnect
			self.elc.reconnect()
		else:
			# Cancel
			sys.exit(0)

	def __handle_socket_data(self, fd, condition):
		try:
			packets = self.elc.recv()
		except ConnectionException as e:
			self.__elc_error(None, None, e.value)
			return True
		events = self.elc.process_packets(packets)
		for e in events:
			ELSimpleEventManager().raise_event(e)
		return True
	
	def __set_active_channel(self, renderer, path):
		"""User clicked an 'active' radio button in the channel list treeview.
		This is a signal handler for the 'toggled' signal."""
		#Update the session's list and the server
		ch = self.elc.session.get_channel_by_num(self.tool_vbox.channel_list[path][2])
		if ch == None:
			#TODO: This shouldn't happen, find a proper action
			return
		self.elc.session.set_active_channel(ch)
		#Update the GUI list
		self.tool_vbox.rebuild_channel_list(self.elc.session.channels)

	def __buddy_list_dclick(self, buddy_tree, path, col, data=None):
		"""User double-clicked a row in the buddy list treeview"""
		# add /[name] if self.input_hbox.msg_txt is empty, otherwise append the name
		iter = self.tool_vbox.buddy_list.get_iter(path)
		buddy = self.tool_vbox.buddy_list.get_value(iter, 0)
		if self.input_hbox.msg_txt.get_text() == "":
			# add /[name]
			self.input_hbox.msg_txt.set_text("/%s " % buddy)
		else:
			self.input_hbox.msg_txt.set_text("%s %s" % (self.input_hbox.msg_txt.get_text(), buddy))
		self.input_hbox.msg_txt.grab_focus()
		self.input_hbox.msg_txt.set_position(self.input_hbox.msg_txt.get_text_length())

	def __chan_list_dclick(self, channel_tree, path, col, data=None):
		"""User double-clicked a row in the channel list treeview"""
		# add @@N if input_hbox.msg_txt is empty
		iter = self.tool_vbox.channel_list.get_iter(path)
		chan = self.tool_vbox.channel_list.get_value(iter, 0)
		if self.input_hbox.msg_txt.get_text() == "":
			# add @@N
			self.input_hbox.msg_txt.set_text("@@%s " % chan)
			self.input_hbox.msg_txt.grab_focus()
			self.input_hbox.msg_txt.set_position(self.input_hbox.msg_txt.get_text_length())
	
	def find_buddy_row(self, buddy):
		"""Get the gtk.Row where buddy is"""
		if not buddy:
			return None
		for row in self.tool_vbox.buddy_list:
			if row[0].upper() == buddy.upper():
				return row
		return None
	
	def find_buddy(self, buddy):
		"""Return the iterator referencing buddy, or None if buddy is not in the buddy_list"""
		if buddy:
			return self.find_buddy_row(buddy).iter
		else:
			return None

	def destroy(self, widget, data=None):
		gtk.main_quit()
		return False

class ChatArea(gtk.ScrolledWindow):
	"""A gtk.ScrolledWindow that contains a chat view and buffer for 
	raw text"""
	def __init__(self):
		# set-up the scrollable window
		super(ChatArea, self).__init__()
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		# setup the chat text area
		self.chat_buff = gtk.TextBuffer()
		self.chat_view = gtk.TextView(self.chat_buff)
		self.chat_view.set_editable(False)
		self.chat_view.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		self.add(self.chat_view)
		self.show_all()

class ToolVBox(gtk.VBox):
	"""A vertical gtk.Box that contains the minimap, clock, channel and buddy list widgets"""

	def __init__(self):
		super(ToolVBox, self).__init__()
		# set-up the channel & buddy list vbox and the buddy list scroll win
		self.blist_scrolled_win = gtk.ScrolledWindow()
		self.blist_scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		# set-up the minimap
		self.minimap = Minimap()
		self.minimap.set_size_request(200, 200)
		self.pack_start(self.minimap, False, False, 0)

		# Add a digital clock for ingame time
		self.clock_lbl = gtk.Label("Time: %d:%02d" % (0,0))
		self.pack_start(self.clock_lbl, False)

		# set-up the channel list tree view
		#  List storage
		self.channel_list = gtk.ListStore(str, bool, int)
		#  Renderers
		#   Text renderer
		self.ch_text_ren = gtk.CellRendererText()
		self.ch_text_ren.set_property("visible", True)
		#   Active channel radio renderer
		self.ch_toggle_ren = gtk.CellRendererToggle()
		self.ch_toggle_ren.set_property("visible", True)
		self.ch_toggle_ren.set_property("activatable", True)
		self.ch_toggle_ren.set_property("radio", True)
		#  Columns containing the renderers
		#   Channel column
		self.channel_col = gtk.TreeViewColumn("Channels")
		self.channel_col.pack_start(self.ch_text_ren, True)
		self.channel_col.add_attribute(self.ch_text_ren, 'text', 0)
		self.channel_col.set_expand(True)
		#   Active channel column
		self.active_ch_col = gtk.TreeViewColumn("Active")
		self.active_ch_col.pack_start(self.ch_toggle_ren, False)
		self.active_ch_col.add_attribute(self.ch_toggle_ren, 'active', 1)
		self.active_ch_col.set_expand(False)
		#  Tree view containing the columns
		self.channel_tree = gtk.TreeView(self.channel_list)
		self.channel_tree.set_size_request(self.channel_tree.size_request()[0], 95) #TODO: Calculate the height so that exactly three elements will fit in the list
		self.channel_tree.set_reorderable(True)
		self.channel_tree.append_column(self.channel_col)
		self.channel_tree.append_column(self.active_ch_col)

		# set-up the buddy list tree view
		self.buddy_list = gtk.ListStore(gobject.TYPE_STRING)
		self.buddy_tree = gtk.TreeView(self.buddy_list)
		self.buddy_cell_ren = gtk.CellRendererText()
		self.buddy_cell_ren.set_property("visible", "TRUE")
		self.buddy_col = gtk.TreeViewColumn("Buddies", self.buddy_cell_ren, markup=0)
		self.buddy_tree.append_column(self.buddy_col)
		self.blist_scrolled_win.add(self.buddy_tree)

		self.pack_start(self.channel_tree, False, False, 0)
		self.pack_start(self.blist_scrolled_win, True, True, 0)
		self.show_all()
	
	def rebuild_channel_list(self, channels):
		"""Rebuild the channel list to correspond with the list passed as the 'channels' parameter"""
		self.channel_list.clear()
		for chan in channels:
			#TODO: #14: Replace element 0 in the below tuple with the channel's text name (if any)
			self.channel_list.append(("%s" % chan.number, chan.is_active, chan.number))

class ChatInputHBox(gtk.HBox):
	"""Extends gtk.HBox to provide an input (gtk.Entry) and send button"""
	def __init__(self):
		super(ChatInputHBox, self).__init__()
		self.msg_txt = gtk.Entry(max=155)
		self.send_btn = gtk.Button('Send')
		self.pack_start(self.msg_txt, True, True, 0)
		self.pack_start(self.send_btn, False, False, 0) #Keep the size of the send button constant, give extra space to the text input field
		self.show_all()
