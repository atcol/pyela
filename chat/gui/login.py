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

from PyQt5.QtWidgets import QDialog,QDesktopWidget,QGridLayout,\
							QLabel,QLineEdit,QSpinBox,\
							QDialogButtonBox							
from PyQt5.QtCore import QSize

class LoginGUI(QDialog):
	"""
	A simple login GUI that acts as a dialog window of a parent
	
	Parameters:
	parent - parent window
	defaults - dictionary of default values, keys: user, password, host, port
	"""
	
	def __init__(self, parent=None, defaults=None):
		super().__init__(parent)
		if defaults is None:
			defaults = {}
		self.setWindowTitle("Login - Pyela Chat")
		self.__setup(defaults)

	def __setup(self, defaults):
		#TODO: Display green v or red x icon in the entries, indicating valid or invalid input with a mouseover tooltip that provides useful info

		# create the table
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.grid.setVerticalSpacing(0)
		self.grid.setHorizontalSpacing(12)
		###self.table.set_col_spacing(0, 12)
		###self.table.set_border_width(6)

		# create the labels
		self.user_lbl = QLabel('&Username:')
		self.passwd_lbl = QLabel('Pass&word:')
		self.host_lbl = QLabel('&Host:')
		self.port_lbl = QLabel('&Port:')
		
		self.grid.addWidget(self.user_lbl,   0, 0)
		self.grid.addWidget(self.passwd_lbl, 1, 0)
		self.grid.addWidget(self.host_lbl,   2, 0)
		self.grid.addWidget(self.port_lbl,   3, 0)

		# create the input boxes
		self.user_txt = QLineEdit()
		self.user_txt.setMaxLength(16)
		self.user_lbl.setBuddy(self.user_txt)
		#Pressing return in the user input moves focus to the next (password) input
		self.user_txt.returnPressed.connect(self.focusNextChild)
		if 'user' in defaults:
			self.user_txt.setText(defaults['user'])
		self.user_txt.textChanged.connect(self._validate_entries)
		
		self.passwd_txt = QLineEdit()
		self.passwd_lbl.setBuddy(self.passwd_txt)
		self.passwd_txt.setEchoMode(QLineEdit.Password)
		if 'password' in defaults:
			self.password_txt.setText(defaults['password'])
		self.passwd_txt.textChanged.connect(self._validate_entries)
		
		self.host_txt = QLineEdit()
		self.host_lbl.setBuddy(self.host_txt)
		if 'host' in defaults:
			self.host_txt.setText(defaults['host'])
		else:
			self.host_txt.setText('game.eternal-lands.com')
		#Set minimum size to a little wider than official server host
		font_metrics = self.host_txt.fontMetrics()
		min_width = font_metrics.width('game.eternal-lands.com____')
		min_height = font_metrics.height()
		self.host_txt.minimumSizeHint = lambda: QSize(min_width, min_height)
		self.host_txt.textChanged.connect(self._validate_entries)
		
		self.port_spin = QSpinBox()
		self.port_spin.setRange(1,65535)
		self.port_lbl.setBuddy(self.port_spin)
		if 'port' in defaults:
			self.port_spin.setValue(int(defaults['port']))
		else:
			self.port_spin.setValue(2001)
		self.grid.addWidget(self.user_txt,   0, 1)
		self.grid.addWidget(self.passwd_txt, 1, 1)
		self.grid.addWidget(self.host_txt,   2, 1)
		self.grid.addWidget(self.port_spin,  3, 1)

		# create buttons
		self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok \
										| QDialogButtonBox.Cancel)
		
		self.buttonbox.button(QDialogButtonBox.Ok).setText('Log in')
		self.buttonbox.accepted.connect(self.accept)
		self.buttonbox.rejected.connect(self.reject)
		self.grid.addWidget(self.buttonbox, 4, 0, 1, 2)
		
		# set OK button state depending on input
		self._validate_entries()
	
	def _validate_entries(self, widget=None, a=None, b=None):
		"""
		Signal handler for the textChanged signal that validates the
		entry inputs, changing the login button's sensitivity as required
		"""
		if len(self.user_txt.text()) > 0 \
			and len(self.passwd_txt.text()) > 0 \
			and len(self.host_txt.text()) > 0:
			self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(True)
		else:
			self.buttonbox.button(QDialogButtonBox.Ok).setEnabled(False)

	def center(self):
		rect = self.frameGeometry()
		center_point = QDesktopWidget().availableGeometry().center()
		rect.moveCenter(center_point)
		self.move(rect.topLeft())