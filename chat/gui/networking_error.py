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

from PyQt5.QtWidgets import QMessageBox

class NetworkingErrorAlert(QMessageBox):
	"""A dialog notifying the user of a networking error.
	The dialog has three buttons: Reconnect, login with another account, quit
	
	Constructor parameters:
	p_msg:	Primary text, displayed in bold with large font
	s_msg:	Optional secondary text, should provide more in-depth description of
			the	problem and suggested action, may also include more info about
			the error
			
	Both strings are parsed as html, so pass them along accordingly."""
	def __init__(self, parent, p_msg, s_msg=""):
		title = "Networking error"
		icon = QMessageBox.Critical
		super().__init__(icon,
						title,
						p_msg,
						QMessageBox.NoButton,
						parent,
						)
		self.setInformativeText(s_msg)

		self.setStandardButtons(QMessageBox.Yes|QMessageBox.Cancel|QMessageBox.Retry)
		self.button(QMessageBox.Yes).setText("&Login as other user")
		self.button(QMessageBox.Cancel).setText("Quit")
		self.button(QMessageBox.Retry).setText("Reconnect")

		self.setDefaultButton(QMessageBox.Retry)