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
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import struct
from random import random as rand
import sys

from placid.el.net.connections import ELConnection
from placid.el.net.elconstants import ELConstants, ELNetFromServer, ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.util.strings import strip_chars
from placid.el.net.channel import Channel
from placid.el.gui.login import LoginGUI

class ChatGUI(gtk.Window):
	def __init__(self):
		self.msg_buff = [] # list of messages, for CTRL+UP/UP and DOWN
		self.msgb_idx = 0
		self.last_key = None # for // name completion
		self.last_pm_to = ""
		self.__setup_gui()
	
	def __setup_gui(self):
		self.elc = None

		gtk.Window.__init__(self)
		self.connect('destroy', self.destroy)
		self.connect('delete_event', self.destroy)
		self.set_size_request(645, 510)
		self.set_border_width(5)

		self.input_hbox = gtk.HBox(False, 0)
		self.input_hbox.show()
		self.vbox = gtk.VBox(False, 0)
		self.vbox.show()

		self.chat_hbox = gtk.HBox(False, 0)
		self.chat_hbox.show()

		# set-up the scrollable window
		self.scrolled_win = gtk.ScrolledWindow()
		self.scrolled_win.set_size_request(560, 480)
		self.scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrolled_win.show()

		# setup the chat text area
		self.chat_buff = gtk.TextBuffer()
		self.chat_view = gtk.TextView(self.chat_buff)
		self.chat_view.set_size_request(640, 480)
		self.chat_view.set_editable(False)
		self.chat_view.set_wrap_mode(gtk.WRAP_WORD)
		self.chat_view.show()
		self.scrolled_win.add(self.chat_view)
		self.chat_hbox.pack_start(self.scrolled_win, True, True, 0)

		# set-up the channel & buddy list vbox and the buddy list scroll win
		self.blist_scrolled_win = gtk.ScrolledWindow()
		self.blist_scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.blist_scrolled_win.show()
		self.tool_vbox = gtk.VBox(False, 0)

		# set-up the channel list tree view
		self.channel_list = gtk.ListStore(gobject.TYPE_STRING)
		self.channel_tree = gtk.TreeView(self.channel_list)
		self.channel_tree.set_size_request(self.channel_tree.get_size_request()[0], 85)
		self.channel_tree.set_reorderable(True)
		self.channel_tree.show()
		self.cell_ren = gtk.CellRendererText()
		self.cell_ren.set_property("visible", "TRUE")
		self.channel_col = gtk.TreeViewColumn("Channels", self.cell_ren, markup=0)
		self.channel_col.set_attributes(self.cell_ren, text=0)
		self.channel_tree.append_column(self.channel_col)

		# set-up the buddy list tree view
		self.buddy_list = gtk.ListStore(gobject.TYPE_STRING)
		self.buddy_tree = gtk.TreeView(self.buddy_list)
		self.buddy_tree.connect('row-activated', self.__buddy_list_dclick)
		self.buddy_tree.show()
		self.buddy_cell_ren = gtk.CellRendererText()
		self.buddy_cell_ren.set_property("visible", "TRUE")
		self.buddy_col = gtk.TreeViewColumn("Buddies", self.buddy_cell_ren, markup=0)
		self.buddy_tree.append_column(self.buddy_col)
		self.blist_scrolled_win.add(self.buddy_tree)
		self.tool_vbox.pack_start(self.channel_tree, False, False, 0)
		self.tool_vbox.pack_start(self.blist_scrolled_win, True, True, 0)

		# add the chat & tool vbox to the chat hbox o,0
		self.vbox.pack_start(self.chat_hbox, False, False, 0)
		self.chat_hbox.pack_end(self.tool_vbox, False, False, 0)

		# setup the chat input & send button
		self.msg_txt = gtk.Entry(max=155)
		self.msg_txt.set_size_request(600, self.msg_txt.get_size_request()[1])
		self.msg_txt.connect('key_press_event', self.__keypress)
		self.msg_txt.show()
		self.send_btn = gtk.Button('Send')
		self.send_btn.connect('clicked', self.send_msg)
		self.send_btn.show()
		self.input_hbox.pack_start(self.msg_txt, True, True, 0)# don't expand, but fill the hbox
		self.input_hbox.pack_start(self.send_btn, True, True, 0)
		self.vbox.pack_start(self.input_hbox, False, False, 0)

		# show the login gui to get the user credentials
		self.do_login()

		# assign the fd of our elconnection to gtk
		gobject.io_add_watch(self.elc.fileno(), gobject.IO_IN | gobject.IO_PRI, self.__process_packets)
		gobject.io_add_watch(self.elc.fileno(), gobject.IO_ERR, self.__elc_error)
		gobject.timeout_add(15000, self.__keep_alive)

		self.add(self.vbox)
		self.set_title("%s@%s:%s - Pyela Chat" % (self.elc.username, self.elc.host, self.elc.port))
		self.show_all()
		self.append_chat('Welcome to Pyela-Chat, part of the Pyela toolset. Visit pyela.googlecode.com for more information')
		self.msg_txt.grab_focus()

		# setup the channel list
		self.channels = []
		gtk.main()

	def do_login(self):
		l = LoginGUI(title="Login - Pyela Chat")
		response = l.run()

		if response == 0:
			# login crendials entered
			#self.elc = ELConnection(l.user_txt.get_text(), l.
			self.elc = ELConnection(l.user_txt.get_text(), l.passwd_txt.get_text(), l.host_txt.get_text(), int(l.port_txt.get_text()))
			self.elc.connect()
			l.destroy()
		elif response == 1:
			# quit
			sys.exit(0)

	def append_chat(self, text):
		self.chat_buff.insert(self.chat_buff.get_end_iter(), text)
		self.chat_view.scroll_to_mark(self.chat_buff.get_insert(), 0)


	def __keypress(self, widget, event=None):
		if event.keyval == gtk.keysyms.Return:
			self.send_msg(None, None)
			self.msg_buff.append(self.msg_txt.get_text())
		elif event.keyval == gtk.keysyms.uparrow:
			if self.msgb_idx > 0 and self.msgb_idx < len(self.msg_buff):
				self.msgb_idx -= 1
				self.msg_txt.set_text(self.msg_buff[self.msgb_idx])
		elif event.keyval == gtk.keysyms.downarrow:
			if self.msgb_idx < len(self.msg_buff):
				self.msgb_idx += 1
				self.msg_txt.set_text(self.msg_buff[self.msgb_idx])
		return False
	
	def send_msg(self, widget, data=None):
		msg = self.msg_txt.get_text()
		if msg != '':
			type = ELNetToServer.RAW_TEXT
			if self.msg_txt.get_text().startswith('/'):
				type = ELNetToServer.SEND_PM
				msg = self.msg_txt.get_text()[1:]
				
			self.elc.send(ELPacket(type, msg))
			self.msg_txt.set_text("")
		return True
	
	def __keep_alive(self):
		"""keeps self.elc alive by calling its keep_alive function.
		This is called automatically every 15 seconds by the gobject API"""
		self.elc.keep_alive()
		return True
	
	def __elc_error(self):
		"""Called by gtk when an error with the socket occurs"""
		self.append_chat("A networking error occured. Login again.")
		self.elc.disconnect()
		self.do_login()

	def __buddy_list_dclick(self, buddy_tree, path, col, data=None):
		"""User double-clicked a row in the buddy list treeview"""
		# add /[name] if self.msg_txt is empty, otherwise append the name
		iter = self.buddy_list.get_iter(path)
		buddy = self.buddy_list.get_value(iter, 0)
		if self.msg_txt.get_text() == "":
			# add /[name]
			self.msg_txt.set_text("/%s " % buddy)
		else:
			self.msg_txt.set_text("%s %s" % (self.msg_txt.get_text(), buddy))
		self.msg_txt.grab_focus()


	def __process_packets(self, widget, data=None):
		self.elc.keep_alive()
		packets = self.elc.recv()
		for packet in packets:
			if packet.type == ELNetFromServer.RAW_TEXT:
				if struct.unpack('<b', packet.data[0])[0] in \
					(ELConstants.CHAT_CHANNEL1, ELConstants.CHAT_CHANNEL2, ELConstants.CHAT_CHANNEL3):
					channel = int(struct.unpack('<b', packet.data[0])[0])
					text = strip_chars(packet.data[1:])
					self.append_chat("\n%s" % (text.replace(']', " @ %s]" % \
						self.channels[int(channel - ELConstants.CHAT_CHANNEL1)].number)))
				else:
					self.append_chat("\n%s" % strip_chars(packet.data[1:]))
			elif packet.type == ELNetFromServer.GET_ACTIVE_CHANNELS:
				# active channel, c1, c2, c3
				self.channel_list.clear()
				chans = struct.unpack('<biii', packet.data)
				i = 0
				active = chans[0]
				for c in chans[1:]:
					if c != 0:
						self.channels.append(Channel(c, i == active))
						self.channel_list.append(["%s" % c])
					i += 1
			elif packet.type == ELNetFromServer.BUDDY_EVENT:
				event = ord(packet.data[0])# 1 is online, 0 offline
				if event == 1:
					buddy = str(strip_chars(packet.data[2:]))
					self.append_chat("\n%s logged in" % buddy)
					self.buddy_list.append([buddy])
				else:
					buddy = str(strip_chars(packet.data[1:]))
					self.append_chat("\n%s logged off" % buddy)
					self.buddy_list.remove(self.find_buddy(buddy))
			elif packet.type == ELNetFromServer.LOG_IN_NOT_OK:
				self.append_chat(strip_chars(packet.data))
				self.elc.disconnect()
				self.do_login()
			elif packet.type == ELNetFromServer.YOU_DONT_EXIST:
				self.append_chat('Incorrect username.')
				self.elc.disconnect()
				self.do_login()
		return True
	
	def find_buddy_row(self, buddy):
		"""Get the gtk.Row where buddy is"""
		if not buddy:
			return None
		for row in self.buddy_list:
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

