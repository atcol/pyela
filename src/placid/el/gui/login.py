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
	
	#def __init__(self, host='game.eternal-lands.com', port=2001):
		#self.host = host
		#self.port = port
		#self.LOG_IN_OK = False
		#self.__setup()
		#pass
#	self
	
	def __init__(self, title=None, parent=None, flags=0, buttons=None):
		super(LoginGUI, self).__init__(title, parent, flags, buttons)
		self.__setup()
	
	def __setup(self):
		#gtk.Dialog.__init__(self)
		#self.set_title('Pyela Chat - Login')
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.connect('destroy', self.destroy)
		self.connect('delete_event', self.destroy)

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
		self.passwd_txt.connect('key_press_event', self._keypress)
		self.host_txt.connect('key_press_event', self._keypress)
		self.port_txt.connect('key_press_event', self._keypress)

		# create the buttons
		#self.login_btn = gtk.Button('Login')
		#self.login_btn.set_size_request(75, 40)
		#self.login_btn.connect('clicked', self.login)
		#self.cancel_btn = gtk.Button('Cancel')
		#self.cancel_btn.set_size_request(75, 40)
		#self.cancel_btn.connect('clicked', self.destroy)
		#self.login_btn.show()
		#self.cancel_btn.show()

		# add the buttons to their rows
		#self.buttons_box.pack_start(self.login_btn, False, False, 0)
		#self.buttons_box.pack_start(self.cancel_btn, False, False, 0)

		# add the hbox instances to the v_box
		self.vbox.pack_start(self.login_box, False, False, 0)
		self.vbox.pack_start(self.passwd_box, False, False, 0)
		self.vbox.pack_start(self.host_box, False, False, 0)
		self.vbox.pack_start(self.port_box, False, False, 0)
		self.vbox.pack_start(self.buttons_box, False, False, 0)

		# add the components to the action area
		#self.vbox.pack_start(self.login_lbl, True, True, 0)
		#self.vbox.pack_start(self.user_txt, True, True, 0)
		#self.action_area.pack_start(self.login_btn, True, True, 0)
		#self.action_area.pack_start(self.cancel_btn, True, True, 0)
		self.add_button("Login", 0)
		self.add_button("Cancel", 1)

		# add the boxes to the window
		#self.add(self.v_box)
		self.show_all()
		self.user_txt.grab_focus()
	
	#def login(self, widget, data=None):
		#"""Check the username & pass textboxes. If not empty, create a new ELConnection"""
		#print "Logging in"
		#if len(self.user_txt.get_text()) >= 3 and len(self.passwd_txt.get_text()) > 0:
			#if self.__login_check(self.user_txt.get_text(), self.passwd_txt.get_text()):
				#self.LOG_IN_OK = True
				#self.hide()
				#self.destroy(None)
		#else:
			#self.show_error('Please enter a valid password and username')
			#self.LOG_IN_OK = False

	#def __login_check(self, user, passwd):
		#"""Login to the EL server and wait for LOG_IN_OK packet or otherwise.
		#If LOG"""
		#self.elc = ELConnection(self.user_txt.get_text(), self.passwd_txt.get_text(), self.host_txt.get_text(), int(self.port_txt.get_text()))
		#self.elc.connect()
		#poll = select.poll()
		#poll.register(self.elc, select.POLLIN | select.POLLPRI | select.POLLERR)
		#while True:
			#p_opt = poll.poll(5000)# poll for maximum 5 secs
			#print "poll: %s" % p_opt
			#if len(p_opt) != 0:
				#if p_opt[0][1] == select.POLLIN or p_opt[0][1] == select.POLLPRI:# check we received data
					#packets = self.elc.recv()
					#for packet in packets:
						#if packet.type == ELNetFromServer.LOG_IN_NOT_OK:
							#self.show_error(strip_chars(packet.data))
							#self.elc.disconnect()
							#return False
						#elif packet.type == ELNetFromServer.YOU_DONT_EXIST:
							#self.show_error('Incorrect username.')
							#self.elc.disconnect()
							#return False
						#elif packet.type == ELNetFromServer.LOG_IN_OK:
							#return True
				#else:
					#self.show_error("Error connecting. Check your username and password is correct and that you're connected to the internet")
					#return False
			#else:
				#self.show_error("Timeout occured whilst attempting to log in. Please check your internet connection")
				#return False
			
	def _keypress(self, widget, event=None):
		if event.keyval == gtk.keysyms.Return:
			self.login(None, None)
		return False

	#def destroy(self, widget, data=None):
		#print "Closing GUI"
		#gtk.main_quit()
		#return False
	
	#def run(self):
		#gtk.main()
		
	#def __create_error_box(self, msg):
		#self.error_box = gtk.HBox(True, 0)
		#self.error_box.show()
		#self.error_lbl = gtk.Label(msg)
		#self.error_lbl.show()
		#self.error_box.pack_start(self.error_lbl, False, False, 0)
		#self.v_box.pack_start(self.error_box, False, False, 0)
#	
	#def show_error(self, msg):
		#if self.error_box == None:
			#self.__create_error_box(msg)
		#self.error_lbl.set_text(msg)
#
	#def hide_error(self):
		#self.error_box.hide()

