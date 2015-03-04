# Copyright 2015 Pyela Project
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

from pyela.el.util.strings import is_colour, special_char_to_char

def parse_el_colours(text, tag_table):
	"""
	Parses the raw text from EL and translates color codes into tags 
	appropriate for GTK colouring. Returns a list of tuples: (tag, text).
	"""

	tagged_text = []
	current_tag = None
	current_text = ""
	for ch in text:
		if is_colour(ch):
			if len(current_text):
				tagged_text.append((current_tag, current_text))
			current_text = ""
			current_tag = tag_table[ch-127]
		else:
			current_text += special_char_to_char(ch)
	if len(current_text):
		tagged_text.append((current_tag, current_text))

	return tagged_text
