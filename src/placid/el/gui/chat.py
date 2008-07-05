import pygtk
pygtk.require('2.0')
import gtk
import gobject
from random import random as rand

from placid.el.net.elconstants import ELNetFromServer, ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.util.strings import strip_chars

class ChatGUI(object):

	def __init__(self, elconnection):
		self.elc = elconnection
		if not self.elc.is_connected():
			self.elc.connect()
		self.__setup_gui()
	
	def __setup_gui(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('destroy', self.destroy)
		self.window.connect('delete_event', self.destroy)
		self.window.set_size_request(645, 510)
		self.window.set_border_width(5)

		# assign the fd of our elconnection to gtk
		gobject.io_add_watch(self.elc.fileno(), gobject.IO_IN | gobject.IO_PRI, self.__process_packets)
		gobject.timeout_add(15000, self.__keep_alive)

		self.chat_hbox = gtk.HBox(False, 0)
		self.chat_hbox.show()
		self.vbox = gtk.VBox(False, 0)
		self.vbox.show()

		# setup the chat text area
		self.chat_buff = gtk.TextBuffer()
		self.chat_view = gtk.TextView(self.chat_buff)
		self.chat_view.set_size_request(640, 480)
		self.chat_view.set_editable(False)
		self.chat_view.set_wrap_mode(gtk.WRAP_WORD)
		self.chat_view.show()
		self.scrolled_win = gtk.ScrolledWindow()
		self.scrolled_win.set_size_request(640, 480)
		self.scrolled_win.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrolled_win.add(self.chat_view)
		self.scrolled_win.show()

		# add the scrollable win to the vbox
		self.vbox.pack_start(self.scrolled_win, False, True, 0)

		# setup the chat input & send button
		self.msg_txt = gtk.Entry(max=155)
		self.msg_txt.set_size_request(600, self.msg_txt.get_size_request()[1])
		self.msg_txt.connect('key_press_event', self.__keypress_send_msg)
		self.msg_txt.show()
		self.send_btn = gtk.Button('Send')
		self.send_btn.connect('clicked', self.send_msg)
		self.send_btn.show()
		self.chat_hbox.pack_start(self.msg_txt, False, True, 0)# don't expand, but fill the hbox
		self.chat_hbox.pack_start(self.send_btn, False, True, 0)
		self.vbox.pack_start(self.chat_hbox, False, False, 0)

		self.window.add(self.vbox)
		self.window.set_title("Pyela Chat - %s@%s:%s" % (self.elc.username, self.elc.host, self.elc.port))
		self.window.show_all()
		self.append_chat('Welcome to Pyela-Chat, part of the Pyela toolset. Visit pyela.googlecode.com for more information')
		self.msg_txt.grab_focus()
		gtk.main()

	def append_chat(self, text):
		self.chat_buff.insert(self.chat_buff.get_end_iter(), text)
		self.chat_view.scroll_to_iter(self.chat_buff.get_end_iter(), 0)

	def __keypress_send_msg(self, widget, event=None):
		if event.keyval == gtk.keysyms.Return:
			self.send_msg(None, None)
		return False
	
	def send_msg(self, widget, data=None):
		msg = self.msg_txt.get_text()
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
		self.elc.keep_alive
		return True

	def __process_packets(self, widget, data=None):
		self.elc.keep_alive()
		packets = self.elc.recv()
		for packet in packets:
			if packet and packet.type == ELNetFromServer.RAW_TEXT:
				self.append_chat("\n%s" % strip_chars(packet.data).replace('\0', ''))
		return True

	def destroy(self, widget, data=None):
		gtk.main_quit()
		return False
