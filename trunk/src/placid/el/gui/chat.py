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
		self.window.set_size_request(645, 500)
		self.window.set_border_width(5)

		# assign the fd of our elconnection to gtk
		gobject.io_add_watch(self.elc.fileno(), gobject.IO_IN | gobject.IO_PRI, self.__process_packets)

		self.chat_hbox = gtk.HBox(True, 0)
		self.chat_hbox.show()
		self.vbox = gtk.VBox(True, 0)
		self.vbox.show()

		# setup the chat text area
		self.chat_buff = gtk.TextBuffer()
		self.append_chat('Welcome to Pyela-Chat, part of the Pyela toolset. Visit pyela.googlecode.com for more information')
		self.chat_view = gtk.TextView(self.chat_buff)
		#self.chat_view.set_single_line_mode(False)
		#self.chat_view.set_max_width_chars(100)
		#self.chat_view.set_line_wrap(True)
		#self.chat_view.set_selectable(True)
		self.chat_view.set_size_request(640, 380)
		self.chat_view.set_editable(False)
		self.chat_view.set_wrap_mode(gtk.WRAP_WORD)
		self.chat_view.show()
		self.scrolled_win = gtk.ScrolledWindow()
		self.scrolled_win.set_size_request(640, 680)
		self.scrolled_win.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		self.scrolled_win.add(self.chat_view)
		self.scrolled_win.show()

		# add the scrollable win to the vbox
		self.vbox.pack_start(self.scrolled_win, False, True, 0)
		#self.vbox.pack_start(self.chat_view, False, False, 0)
		self.window.add(self.scrolled_win)

		# setup the chat input & send button
		self.msg_txt = gtk.Entry(max=155)
		self.msg_txt.set_size_request(200, self.msg_txt.get_size_request()[1])
		self.msg_txt.connect('key_press_event', self.__keypress_send_msg)
		self.msg_txt.show()
		self.send_btn = gtk.Button('Send')
		self.send_btn.connect('clicked', self.send_msg)
		self.send_btn.show()
		self.chat_hbox.pack_start(self.msg_txt, False, True, 0)# don't expand, but fill the hbox
		self.chat_hbox.pack_start(self.send_btn, False, True, 0)
		self.vbox.pack_start(self.chat_hbox, False, False, 0)

		self.window.add(self.vbox)
		self.window.show()
		gtk.main()

	def append_chat(self, text):
		self.chat_buff.insert(self.chat_buff.get_end_iter(), text)

	def __keypress_send_msg(self, widget, event=None):
		print "key press: %s, %s" % (widget, event)
		if event.keyval == gtk.keysyms.Return:
			self.send_msg(None, None)
		return False
	
	def send_msg(self, widget, data=None):
		self.elc.send(ELPacket(ELNetToServer.RAW_TEXT, self.msg_txt.get_text()))
		self.msg_txt.set_text("")
		return True

	def __process_packets(self, widget, data=None):
		self.elc.keep_alive()
		packets = self.elc.recv()
		for packet in packets:
			if packet and packet.type == ELNetFromServer.RAW_TEXT:
				#self.chat_buff.set_text(self.chat_buff.get_text() + "\n" + strip_chars(packet.data).replace('\0', ''))
				self.append_chat("\n%s" % strip_chars(packet.data).replace('\0', ''))
		return True

	def destroy(self, widget, data=None):
		gtk.main_quit()
		return False
