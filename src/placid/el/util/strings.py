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
from placid.el.net.elconstants import ELConstants

def strip_chars(str):
	"""Remove protocol or control characters from the given string"""
	stripped_str = ""

	for char in str:
		if ord(char) < 127+ELConstants.C_LBOUND or ord(char) > 127+ELConstants.C_UBOUND:
			stripped_str += char

	if ord(stripped_str[-1]) == 0:
		stripped_str = stripped_str[:-1]

	return stripped_str

def split_str(str, max_len):
	"""Split the given string into a list of strings small enough for RAW_TEXT messages
		str - the string to split
		max_len - the maximum length of any given string
	"""
	strs = []
	if len(str) < max_len:
		# short enough to send in one message
		return [str]
	else:
		# string is too long, truncate to multiple strings
		idx = 0
		while idx < len(str):
			strs.append(str[idx:idx + max_len])
			idx += max_len
	return strs
