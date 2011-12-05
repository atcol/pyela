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

from gi.repository import Gtk

class NetworkingErrorAlert(Gtk.Dialog):
	"""A GTK dialog notifying the user of a networking error.
	The dialog has three buttons: Reconnect, login with another account, quit
	
	Constructor parameters:
	p_msg:	Primary text, displayed in bold with large font
	s_msg:	Optional secondary text, should provide more in-depth description of
			the	problem and suggested action, may also include more info about
			the error
			
	Both strings are parsed as pango markup, so pass them along accordingly."""
	def __init__(self, parent, p_msg, s_msg = ""):
		super(NetworkingErrorAlert, self).__init__("Networking error",
				parent,
				Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
				("_Login as other user", Gtk.ResponseType.REJECT,
				Gtk.STOCK_QUIT, Gtk.ResponseType.CANCEL,
				"_Reconnect", Gtk.ResponseType.ACCEPT)
			)
		self.set_default_response(Gtk.ResponseType.ACCEPT)
		self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		self.set_border_width(6)					#GNOME HIG
		self.set_resizable(False)					#GNOME HIG

		#Add eyecandy

		img = Gtk.Image()
		img.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.DIALOG)
		img.set_alignment(0, 0)						#GNOME HIG
		
		label_str = '<span weight="bold" size="larger">%s</span>\n' % p_msg
		if s_msg != None and len(s_msg) > 0:
			label_str += '\n%s\n' % s_msg
		label = Gtk.Label(label_str)
		label.set_use_markup(True)
		label.set_alignment(0, 0)					#GNOME HIG
		label.set_line_wrap(True)					#GNOME HIG
		label.set_selectable(True)					#GNOME HIG
		
		hbox = Gtk.HBox()
		hbox.set_spacing(12)						#GNOME HIG
		hbox.set_border_width(6)					#GNOME HIG
		hbox.pack_start(img, False, False, 0)
		hbox.pack_start(label, True, True, 0)
		hbox.show_all()
		
		vbox = self.get_content_area()
		vbox.set_spacing(12)						#GNOME HIG
		vbox.pack_start(hbox, False, False, 0)
		vbox.show_all()
