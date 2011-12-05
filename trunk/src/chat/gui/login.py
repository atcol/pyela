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
from gi.repository import Gtk
import time
import select

from pyela.el.net.connections import ELConnection
from pyela.el.net.elconstants import ELNetFromServer, ELNetToServer
from pyela.el.util.strings import strip_chars

class LoginGUI(Gtk.Dialog):
	"""A simple login GUI that acts as a dialog window of a parent
	
	Parameters:
	title - window title
	parent - parent window
	defaults - dictionary of default values, keys: user, password, host, port
	flags - gtk flags for the window"""
	
	def __init__(self, title=None, parent=None, defaults={}, flags=0, buttons=None):
		super(LoginGUI, self).__init__(title, parent, flags, buttons)
		self.__setup(defaults)

	def __setup(self, defaults={}):
		#TODO: Display green v or red x icon in the entries, indicating valid or invalid input with a mouseover tooltip that provides useful info
		self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.set_border_width(6)

		# create the table
		self.table = Gtk.Table(4, 2)
		self.table.set_col_spacing(0, 12)
		self.table.set_border_width(6)

		# create the labels
		self.login_lbl = Gtk.Label('_Username:')
		self.login_lbl.set_property("use-underline", True)
		self.login_lbl.set_alignment(0.0, 0.5)
		self.login_lbl.show()

		self.passwd_lbl = Gtk.Label('Pass_word:')
		self.passwd_lbl.set_property("use-underline", True)
		self.passwd_lbl.set_alignment(0.0, 0.5)
		self.passwd_lbl.show()

		self.host_lbl = Gtk.Label('_Host:')
		self.host_lbl.set_property("use-underline", True)
		self.host_lbl.set_alignment(0.0, 0.5)
		self.host_lbl.show()

		self.port_lbl = Gtk.Label('_Port:')
		self.port_lbl.set_property("use-underline", True)
		self.port_lbl.set_alignment(0.0, 0.5)
		self.port_lbl.show()

		self.table.attach(self.login_lbl, 0, 1, 0, 1)
		self.table.attach(self.passwd_lbl, 0, 1, 1, 2)
		self.table.attach(self.host_lbl, 0, 1, 2, 3)
		self.table.attach(self.port_lbl, 0, 1, 3, 4)

		# create the input boxes
		self.user_txt = Gtk.Entry()
		self.user_txt.set_max_length(16)
		self.login_lbl.set_mnemonic_widget(self.user_txt)
		#Pressing return in the user input moves focus to the next (password) input
		self.user_txt.connect('activate', self._focus_next)
		if 'user' in defaults:
			self.user_txt.set_text(defaults['user'])
		self.user_txt.connect('changed', self._check_entries_ok)
		self.user_txt.show()
		
		self.passwd_txt = Gtk.Entry()
		self.passwd_lbl.set_mnemonic_widget(self.passwd_txt)
		self.passwd_txt.set_activates_default(True)
		self.passwd_txt.set_visibility(False)
		if 'password' in defaults:
			self.password_txt.set_text(defaults['password'])
		self.passwd_txt.connect('changed', self._check_entries_ok)
		self.passwd_txt.show()
		
		self.host_txt = Gtk.Entry()
		self.host_lbl.set_mnemonic_widget(self.host_txt)
		self.host_txt.set_activates_default(True)
		if 'host' in defaults:
			self.host_txt.set_text(defaults['host'])
		else:
			self.host_txt.set_text('game.eternal-lands.com')
		self.host_txt.set_width_chars(25) #Enough to display the official server's address
		self.host_txt.connect('changed', self._check_entries_ok)
		self.host_txt.show()
		
		self.port_adj = Gtk.Adjustment(value=2001, lower=1, upper=65535, step_increment=1)
		self.port_spin = Gtk.SpinButton(adjustment=self.port_adj)
		self.port_lbl.set_mnemonic_widget(self.port_spin)
		self.port_spin.set_activates_default(True)
		if 'port' in defaults:
			self.port_spin.set_value(int(defaults['port']))
		
		self.table.attach(self.user_txt, 1, 2, 0, 1)
		self.table.attach(self.passwd_txt, 1, 2, 1, 2)
		self.table.attach(self.host_txt, 1, 2, 2, 3)
		self.table.attach(self.port_spin, 1, 2, 3, 4)
		self.get_content_area().pack_start(self.table, False, False, 0)

		# add the components to the action area
		self.login_btn = self.add_button("_Login", Gtk.ResponseType.OK)
		self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		self.set_default_response(Gtk.ResponseType.OK)
		self._check_entries_ok()

		# add the boxes to the window
		self.show_all()
		
		self.user_txt.grab_focus()
		
	def _focus_next(self, widget):
		"""Signal handler for return-key action, moves keyboard focus to
		the next widget."""
		self.do_move_focus(self, Gtk.DIR_TAB_FORWARD)
	
	def _check_entries_ok(self, widget=None, a=None, b=None):
		"""Signal handler for the 'changed' signal that validates the entry inputs, changing the
		login button's sensitivity as required"""
		if len(self.user_txt.get_text()) > 0 and len(self.passwd_txt.get_text()) > 0 \
			and len(self.host_txt.get_text()) > 0:
			self.login_btn.set_sensitive(True)
		else:
			self.login_btn.set_sensitive(False)
