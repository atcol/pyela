# Copyright 2008-2015 Pyela Project
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

import math
import sys

from pyela.el.net.elconstants import ELNetToServer
from pyela.el.net.connections import ELConnection, DISCONNECTED
from pyela.el.net.packets import ELPacket
from pyela.el.net.packethandlers import ExtendedELPacketHandler
from pyela.el.common.exceptions import ConnectionException
from pyela.el.logic.session import ELSession
from pyela.el.logic.eventmanagers import ELSimpleEventManager
from pyela.el.util.strings import el_colour_char_table, str_to_el_str
from gui.login import LoginGUI
from gui.minimapwidget import Minimap
from gui.networking_error import NetworkingErrorAlert
from gui.locationlbl import LocationLbl
import html

from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout,\
							QLineEdit, QPushButton,\
							QApplication, QWidget, QFrame, QLabel,\
							QTreeWidget, QTreeWidgetItem,\
							QHeaderView, QRadioButton,\
							QMessageBox, QTextBrowser
from PyQt5.QtCore import QSocketNotifier
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt, QTimer

from logic.eventhandler import ChatGUIEventHandler

def launch_gui():
	app = QApplication(sys.argv)
	print(app.style().metaObject().className())
	ChatGUI()
	app.exec_()

class ChatGUI(QMainWindow):
	def __init__(self):
		super().__init__()
		self.elc = None
		self.socket_notifiers = []
		ELSimpleEventManager().add_handler(ChatGUIEventHandler(self))
		# Create window
		self.__setup_gui()
		# Create the el->html colour map
		self.__build_colourtable()

		# show the login gui to get the user credentials
		self.do_login()

		# Add a timer to send the heart beats to the server
		self.keep_alive_timer = QTimer(self)
		self.keep_alive_timer.timeout.connect(self.__keep_alive)
		self.keep_alive_timer.start(15000)

		# Show chat window
		self.show()
		self.setWindowTitle("{elc.session.name}@{elc.host}:{elc.port} - Pyela Chat".format(elc=self.elc))
		welcome_msg = 'Welcome to Pyela-Chat, part of the Pyela toolset. Visit <a href="{url}">{url}</a> for more information.'
		self.append_html(welcome_msg.format(url='http://github.com/atc-/pyela'))
		self.msg_txt.setFocus()
	
	def __setup_gui(self):
		self.elc = None

		super().__init__()
		self.destroyed.connect(self.destroy)
		###self.connect('delete_event', self.destroy)
		self.setMinimumSize(645, 510)
		###self.set_border_width(5)

		# main container
		container = QWidget()
		self.vbox = QVBoxLayout()
		container.setLayout(self.vbox)
		self.setCentralWidget(container)

		# container for chat area | minimap, channel and buddy lists
		self.chat_hbox = QHBoxLayout()

		#Add the chat area
		self.chat_area = QTextBrowser(self)
		self.chat_area.setReadOnly(True)
		self.chat_area.setFrameStyle(QFrame.Panel | QFrame.Plain)
		self.chat_area.setLineWidth(1)
		self.chat_area.setOpenExternalLinks(True)
		self.chat_hbox.addWidget(self.chat_area, 1)

		# add the chat & tool vbox to the chat hbox o,0
		self.tool_vbox = self.__create_tool_vbox()
		self.vbox.addLayout(self.chat_hbox, 1)
		self.chat_hbox.addLayout(self.tool_vbox, 0)

		# setup the chat input & send button
		self.input_hbox = self.__create_chat_input_hbox()
		self.msg_txt.returnPressed.connect(self.send_msg)
		self.send_btn.clicked.connect(self.send_msg)
		self.vbox.addLayout(self.input_hbox)
		
	def __create_chat_input_hbox(self):
		hbox = QHBoxLayout()
		self.msg_txt = ChatInput()
		self.send_btn = QPushButton('Send')
		hbox.addWidget(self.msg_txt, 1)
		hbox.addWidget(self.send_btn, 0) #Keep the size of the send button constant, give extra space to the text input field
		return hbox

	def __create_tool_vbox(self):
		vbox = QVBoxLayout()
		# set-up the channel & buddy list vbox and the buddy list scroll win
		##self.blist_scrolled_win = Gtk.ScrolledWindow()
		##self.blist_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		
		# set up the location string label
		self.location_lbl = LocationLbl(self)
		self.location_lbl.setAlignment(Qt.AlignHCenter)
		vbox.addWidget(self.location_lbl)

		# set-up the minimap
		self.minimap = Minimap()
		self.minimap.setMinimumSize(200, 200)
		vbox.addWidget(self.minimap)

		# Add a digital clock for ingame time
		self.clock_lbl = QLabel("Time: {:d}:{:02d}".format(0,0))
		self.clock_lbl.setAlignment(Qt.AlignHCenter)
		vbox.addWidget(self.clock_lbl)

		self.channel_list = ChannelList(self)
		vbox.addWidget(self.channel_list,1)

		# set-up the buddy list tree view
		self.buddy_list = BuddyList(self)
		vbox.addWidget(self.buddy_list, 1)
		return vbox
	
	def __build_colourtable(self):
		"""Build a table of textbuffer tags, mapping EL colour codes"""
		self.qt_el_colour_table = {}
		for code,rgb in el_colour_char_table.items():
			if rgb == (1.0,1.0,1.0):
				#White is invisible on our white background, so fix that
				rgb = (0, 0, 0)
			else:
				#Calculate the brightness of the colour using the HSP
				#algorithm (http://alienryderflex.com/hsp.html)
				brightness = math.sqrt(0.299*(rgb[0]*255)**2 + 0.587*(rgb[1]*255)**2 + 0.114*(rgb[2]*255)**2)
				threshold = 100#180
				if brightness > threshold:
					#Invert bright colours to make them visible
					diff = (brightness-threshold)/255
					rgb = [max(0, x-diff) for x in rgb]
			hexcode = "#%02x%02x%02x" % (rgb[0]*255,rgb[1]*255,rgb[2]*255)
			self.qt_el_colour_table[code] = hexcode

	def keyPressEvent(self, event):
		if (event.modifiers == Qt.ControlModifier and event.key() == Qt.Key_Q) or \
			(event.modifiers == Qt.AltModifier and event.keyval == Qt.Key_X):
			#Quit on ctrl+q or alt+x
			print("close")
			self.close()
		else:
			super().keyPressEvent(event)

	def do_login(self):
		# Pass current values to the new login dialog, if there are any
		defaults = {}
		if self.elc != None:
			if self.elc.session != None and self.elc.session.name != None:
				defaults['user'] = self.elc.session.name
			defaults['port'] = self.elc.port
			defaults['host'] = self.elc.host
			
		l = LoginGUI(parent=self, defaults=defaults)
		done = False

		# Loop while trying to connect so that we can display error messages
		while not done:
			response = l.exec()
			if response:
				# login credentials entered
				if self.elc == None:
					# Initial login, setup the ELConnection
					session = ELSession(l.user_txt.text(), l.passwd_txt.text())
					self.elc = ELConnection(session, l.host_txt.text(), l.port_spin.value())
					self.elc.packet_handler = ExtendedELPacketHandler(self.elc)
				else:
					self.elc.session = ELSession(l.user_txt.text(), l.passwd_txt.text())
					self.elc.host = l.host_txt.text()
					self.elc.port = l.port_spin.value()
					self.elc.con_tries = 0
				self.minimap.el_session = self.elc.session
				if not self.elc.connect():
					# Connection failed!
					alert = QMessageBox()
					alert.setText("Connection failed")
					alert.setInformativeText(self.elc.error)
					alert.setStandardButtons(QMessageBox.Close)
					alert.setIcon(QMessageBox.Critical)
					alert.exec()
					# Re-run the login dialog
				else:
					done = True
			else:
				# quit
				sys.exit(0)
		self.elc.socket.settimeout(15)
		l.destroy()
		
	def register_socket_notifier(self):
		# Assign the fd of our elconnection to qt
		data_notifier = QSocketNotifier(self.elc.fileno(), QSocketNotifier.Read, self)
		data_notifier.activated.connect(self.__handle_socket_data)
		err_notifier = QSocketNotifier(self.elc.fileno(), QSocketNotifier.Exception, self)
		err_notifier.activated.connect(self.__elc_error)

		self.socket_notifiers.append((data_notifier, err_notifier))
	
	def unregister_socket_notifier(self):
		for dn,en in self.socket_notifiers:
			dn.setEnabled(False)
			en.setEnabled(False)
			del dn
			del en
		self.socket_notifiers = []
		
	def append_html(self, msg):
		cursor = self.chat_area.textCursor()
		cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
		cursor.insertHtml(msg)
		#Get the current scrollbar position and only scroll if the user is looking
		# at the bottom line (to allow scrolling up to read backlog)
		scrollbar = self.chat_area.verticalScrollBar()
		if scrollbar.value() == scrollbar.maximum():
			cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
			self.chat_area.setTextCursor(cursor)

	def append_chat(self, msgs, colour = None):
		for msg in msgs:			
			msg = html.escape(msg)
			msg = msg.replace('\n', '<br>')
			if colour:
				msg = '<font color="{}">{}</font>'.format(colour, msg)
			self.append_html(msg)

	def show_popup_message(self, msg, title="Message"):
		alert = QMessageBox(self)
		alert.setText(msg)
		alert.setStandardButtons(QMessageBox.Close)
		alert.setIcon(QMessageBox.Information)
		alert.setWindowModality(Qt.NonModal)
		alert.setAttribute(Qt.WA_DeleteOnClose, True)
		alert.show()
	
	def send_msg(self, widget=None, data=None):
		msg = self.msg_txt.text()
		if msg != '':
			t = ELNetToServer.RAW_TEXT
			if msg.startswith('/'):
				#PMs should not include the /, but use a special type
				t = ELNetToServer.SEND_PM
				msg = msg[1:]
			
			el_msg = str_to_el_str(str(msg))
			self.elc.send(ELPacket(t, el_msg))
			self.msg_txt.setText('')
			#input text buffer handling
			if self.msg_txt.msgb_idx > 0:
				#Remove any un-sent text from the input buffer
				self.msg_txt.msg_buff.pop(0)
			self.msg_txt.msgb_idx = 0
			if t == ELNetToServer.SEND_PM:
				#Re-add the / that was removed above
				msg = '/'+msg
			if len(self.msg_txt.msg_buff) == 0 or self.msg_txt.msg_buff[0] != msg:
				#Avoid duplicate entries in the backlog
				self.msg_txt.msg_buff.insert(0, msg)
		return True
	
	def __keep_alive(self):
		"""keeps self.elc alive by calling its keep_alive function.
		This is called automatically every 15 seconds by the gobject API"""
		if self.elc.is_connected():
			self.elc.keep_alive()
		return True

	def __elc_error(self, msg = None):
		"""Called by qt when an error with the socket occurs.
		May also be called by self.__process_packets, in which case msg is set"""
		err_str = "A networking error occured, please log in again"
		if msg != None:
			desc_str = msg
		else:
			desc_str = None
		self.append_chat(["\n", err_str])
		if self.elc.status != DISCONNECTED:
			# If .status is not DISCONNECTED, Qt has detected an error.
			# (We set .status to DISCONNECTED when it's detected by us)
			self.elc.disconnect()
		# Display the error message in a popup dialog, asking the user what to do
		alert = NetworkingErrorAlert(self, err_str, desc_str)
		response = alert.exec_()
		if response == QMessageBox.Yes:
			# Log in as other user
			self.do_login()
		elif response == QMessageBox.Retry:
			# Reconnect
			self.elc.reconnect()
		else:
			# Cancel
			sys.exit(0)

	def __handle_socket_data(self):
		try:
			packets = self.elc.recv()
		except ConnectionException as e:
			self.__elc_error(e.value)
			return True
		events = self.elc.process_packets(packets)
		for e in events:
			ELSimpleEventManager().raise_event(e)
		return True

class ChatInput(QLineEdit):
	def __init__(self):
		super().__init__()
		self.msg_buff = [] # list of messages, for CTRL+UP/UP and DOWN
		self.msgb_idx = 0
		self.last_pm_from = None

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Up:
			if self.msgb_idx == 0 and len(self.msg_buff) > 0:
				#This is the first up-keypress, store what's in the input box as the first entry in the buffer
				self.msg_buff.insert(0, self.text())
				self.msgb_idx = 1
				self.setText(self.msg_buff[self.msgb_idx])
			elif self.msgb_idx > 0 and self.msgb_idx < len(self.msg_buff)-1:
				#Further browsing upwards in the buffer
				self.msgb_idx += 1
				self.setText(self.msg_buff[self.msgb_idx])
			#Position the cursor at the end of the input
			self.setCursorPosition(len(self.text()))
		elif event.key() == Qt.Key_Down:
			if self.msgb_idx > 1:
				self.msgb_idx -= 1
				self.setText(self.msg_buff[self.msgb_idx])
			elif self.msgb_idx == 1:
				#We're at the bottom of the buffer, restore what was initially in the input box and remove it from the list of input
				self.setText(self.msg_buff.pop(0))
				self.msgb_idx = 0
			#Position the cursor at the end of the input
			self.setCursorPosition(len(self.text()))
		elif event.key() == Qt.Key_Slash and len(self.text()):
			#Allow "//" input to reply to last person we received a PM from
			old_text = self.text()
			if self.last_pm_from is not None and old_text[0] == '/' and self.cursorPosition() == 1:
				new_text = '/'+self.last_pm_from+' '+old_text[1:]
				self.setText(new_text)
				self.setCursorPosition(1+len(self.last_pm_from)+1)
			else:
				super().keyPressEvent(event)
		else:
			super().keyPressEvent(event)

class ChannelList(QTreeWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.main_win = parent
		self.setColumnCount(2)
		self.setSortingEnabled(False)
		self.setHeaderLabels(['Channels', 'Active'])
		self.header().setStretchLastSection(False)
		self.header().setSectionResizeMode(0,QHeaderView.Stretch)
		self.header().setSectionResizeMode(1,QHeaderView.ResizeToContents)
		self.itemDoubleClicked.connect(self.__insert_chan_num)

	def sizeHint(self):
		"""
		Set width to a small number to allow other widgets to determine the width
		:return:QSize
		"""
		size = super().sizeHint()
		size.setWidth(10)
		return size

	def __set_active_channel(self, active):
		"""User clicked an 'active' radio button in the channel list treeview.
		This is a signal handler for the 'checked' signal of the radiobutton."""
		if not active:
			# Radio button being un-toggled, ignore
			return
		#Find toggled radio button's number
		item = self.topLevelItem(0)
		ch = None
		while item:
			rb = self.itemWidget(item, 1)
			if rb.isChecked():
				ch = item.data(0, Qt.UserRole)
				break
			item = self.itemBelow(item)
		if not ch:
			# No checked items.
			# TODO: This shouldn't happen, find a proper action
			return
		#Update the session's list and the server
		self.main_win.elc.session.set_active_channel(ch)
		#Update the GUI list
		self.rebuild_channel_list(self.main_win.elc.session.channels)

	def __insert_chan_num(self, item, column):
		"""
		User double-clicked a row in the channel list treeview.
		Add @@N if main_win.msg_txt is empty
		"""
		chan = item.data(0, Qt.UserRole)
		if self.main_win.msg_txt.text() == "":
			# add @@N
			self.main_win.msg_txt.setText("@@{} ".format(chan.number))
			self.main_win.msg_txt.setFocus()

	def rebuild_channel_list(self, channels):
		"""Rebuild the channel list to correspond with the list passed as the 'channels' parameter"""
		self.clear()
		for chan in channels:
			if chan.number >= 1000000000:
				c_str = "Guild"
			else:
				c_str = str(chan.number)
			#TODO: #14: Replace element 0 in the below tuple with the channel's text name (if any)
			##self.channel_list.append((c_str, chan.is_active, chan.number))
			list_item = QTreeWidgetItem()
			# Add channel name
			list_item.setText(0, c_str)
			# Try to align radio button
			list_item.setTextAlignment(1, Qt.AlignHCenter)
			# Store channel object
			list_item.setData(0, Qt.UserRole, chan)
			# Add to list view before connecting radio button
			self.addTopLevelItems([list_item])
			# Create radio button
			rb = QRadioButton(self)
			if chan.is_active:
				rb.setChecked(True)
			rb.toggled.connect(self.__set_active_channel)
			self.setItemWidget(list_item, 1, rb)

class BuddyList(QTreeWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.main_win = parent
		self.setColumnCount(1)
		self.setHeaderLabels(['Buddies'])
		self.itemDoubleClicked.connect(self.__insert_buddy_name)
	def sizeHint(self):
		"""
		Set width to a small number to allow other widgets to determine the width
		:return:QSize
		"""
		size = super().sizeHint()
		size.setWidth(10)
		return size
	def append(self, buddy):
		item = QTreeWidgetItem()
		item.setText(0, buddy)
		self.addTopLevelItems([item])
	def __insert_buddy_name(self, item, column):
		"""User double-clicked a row in the buddy list"""
		# add /[name] if self.input_hbox.msg_txt is empty, otherwise append the name
		buddy = item.text(0)
		if self.main_win.msg_txt.text() == "":
			# add /[name]
			self.main_win.msg_txt.setText("/%s " % buddy)
		else:
			self.main_win.msg_txt.setText("%s %s" % (self.main_win.msg_txt.text(), buddy))
		self.main_win.msg_txt.setFocus()