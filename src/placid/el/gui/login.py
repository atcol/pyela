import pygtk
pygtk.require('2.0')
import gtk

from placid.el.net.connections import ELConnection

class LoginGUI(object):
	
	def __init__(self):
		self.__setup()
		pass
	
	def __setup(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect('delete_event', self.destroy)

		# create the boxes
		self.vbox = gtk.VBox(True, 0)
		self.login_box = gtk.HBox(True, 0)
		self.passwd_box = gtk.HBox(True, 0)
		self.buttons_box = gtk.HBox(True, 0)
		self.vbox.show()
		self.login_box.show()
		self.passwd_box.show()
		self.buttons_box.show()

		# create the labels
		self.login_lbl = gtk.Label('Username:')
		self.login_lbl.show()
		self.passwd_lbl = gtk.Label('Password:')
		self.passwd_lbl.show()
		self.login_box.pack_start(self.login_lbl, False, False, 0)
		self.passwd_box.pack_start(self.passwd_lbl, False, False, 0)

		# create the input boxes
		self.user_txt = gtk.Entry(max=15)
		self.user_txt.show()
		self.passwd_txt = gtk.Entry(max=0)
		self.passwd_txt.set_visibility(False)
		self.passwd_txt.show()
		self.login_box.pack_start(self.user_txt, False, False, 0)
		self.passwd_box.pack_start(self.passwd_txt, False, False, 0)

		# create the buttons
		self.login_btn = gtk.Button('Login')
		self.login_btn.connect('clicked', self.login)
		self.cancel_btn = gtk.Button('Cancel')
		self.cancel_btn.connect('clicked', self.destroy)
		self.login_btn.show()
		self.cancel_btn.show()

		# add the buttons to their rows
		self.buttons_box.pack_start(self.login_btn, False, False, 0)
		self.buttons_box.pack_start(self.cancel_btn, False, False, 0)

		# add the hbox instances to the vbox
		self.vbox.pack_start(self.login_box, False, False, 0)
		self.vbox.pack_start(self.passwd_box, False, False, 0)
		self.vbox.pack_start(self.buttons_box, False, False, 0)

		# add the boxes to the window
		self.window.add(self.vbox)

		self.window.show()
	
	def login(self, widget, data=None):
		"""Check the username & pass textboxes. If not empty, create a new ELConnection"""
		if len(self.user_txt.get_text()) >= 3 and len(self.passwd_txt.get_text()) > 0:
			self.elc = ELConnection(self.user_txt.get_text(), self.passwd_txt.get_text(), host='game.eternal-lands.com', port=2001)
			self.elc.connect()
			if not self.elc.is_connected():
				self.show_error('Login failed!')
		else:
			self.show_error('Please enter a valid password and username')

	def destroy(self, widget, data=None):
		print "Closing GUI"
		gtk.main_quit()
		return False
	
	def run(self):
		gtk.main()
	
	def show_error(self, msg):
		if self.error_box == None:
			self.error_box = gtk.HBox(True, 0)
			self.error_box.show()
			self.error_lbl = gtk.Label(msg)
			self.error_lbl.show()
			self.error_box.pack_start(self.error_lbl, False, False, 0)
			self.vbox.pack_start(self.error_box, False, False, 0)
		else:
			self.error_lbl.set_text(msg)

