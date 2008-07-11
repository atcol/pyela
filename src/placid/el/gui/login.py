import pygtk
pygtk.require('2.0')
import gtk
import time
import select

from placid.el.net.connections import ELConnection
from placid.el.net.elconstants import ELNetFromServer, ELNetToServer
from placid.el.util.strings import strip_chars

class LoginGUI(gtk.Dialog):
	"""A simple login GUI that acts as a dialog window of a parent"""
	
	def __init__(self, title=None, parent=None, flags=0, buttons=None):
		super(LoginGUI, self).__init__(title, parent, flags, buttons)
		self.__setup()
	
	def __setup(self):
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		#self.connect('destroy', self.destroy)
		#self.connect('delete_event', self.destroy)

		# create the boxes
		self.v_box = gtk.VBox(True, 0)
		self.login_box = gtk.HBox(True, 0)
		self.passwd_box = gtk.HBox(True, 0)
		self.host_box = gtk.HBox(True, 0)
		self.port_box = gtk.HBox(True, 0)
		self.buttons_box = gtk.HBox(True, 0)
		self.v_box.show()
		self.login_box.show()
		self.passwd_box.show()
		self.host_box.show()
		self.port_box.show()
		self.buttons_box.show()
		self.error_box = None

		# create the labels
		self.login_lbl = gtk.Label('Username:')
		self.login_lbl.show()
		self.passwd_lbl = gtk.Label('Password:')
		self.passwd_lbl.show()
		self.host_lbl = gtk.Label('Host:')
		self.host_lbl.show()
		self.port_lbl = gtk.Label('Port:')
		self.port_lbl.show()

		self.login_box.pack_start(self.login_lbl, False, False, 0)
		self.passwd_box.pack_start(self.passwd_lbl, False, False, 0)
		self.host_box.pack_start(self.host_lbl, False, False, 0)
		self.port_box.pack_start(self.port_lbl, False, False, 0)

		# create the input boxes
		self.user_txt = gtk.Entry(max=15)
		self.user_txt.show()
		self.passwd_txt = gtk.Entry(max=0)
		self.passwd_txt.set_visibility(False)
		self.passwd_txt.show()
		self.host_txt = gtk.Entry(max=30)
		self.host_txt.show()
		self.host_txt.set_text('game.eternal-lands.com')
		self.port_txt = gtk.Entry(max=5)
		self.port_txt.set_text('2001')
		self.port_txt.show()
		self.login_box.pack_start(self.user_txt, False, False, 0)
		self.passwd_box.pack_start(self.passwd_txt, False, False, 0)
		self.host_box.pack_start(self.host_txt, False, False, 0)
		self.port_box.pack_start(self.port_txt, False, False, 0)
		#self.passwd_txt.connect('key_press_event', self._keypress)
		#self.host_txt.connect('key_press_event', self._keypress)
		#self.port_txt.connect('key_press_event', self._keypress)

		# add the hbox instances to the v_box
		self.vbox.pack_start(self.login_box, False, False, 0)
		self.vbox.pack_start(self.passwd_box, False, False, 0)
		self.vbox.pack_start(self.host_box, False, False, 0)
		self.vbox.pack_start(self.port_box, False, False, 0)
		self.vbox.pack_start(self.buttons_box, False, False, 0)

		# add the components to the action area
		self.add_button("Login", 0)
		self.add_button("Cancel", 1)

		# add the boxes to the window
		self.show_all()
		self.user_txt.grab_focus()
