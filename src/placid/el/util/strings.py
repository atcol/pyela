# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
#
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

def is_colour(ch):
	"""Returns true if ch is a colour code"""
	return ord(ch) >= 127+ELConstants.C_LBOUND and ord(ch) <= 127+ELConstants.C_UBOUND

def is_special_char(ch):
	"""Return true if ch is a foreign character"""
	#The following greater-than is not a typo
	return ord(ch) > 127+ELConstants.SPECIALCHAR_LBOUND and ord(ch) <= 127+ELConstants.SPECIALCHAR_UBOUND

special_char_table = {127+ELConstants.EACUTE:'é', 127+ELConstants.ACIRC:'â', 127+ELConstants.AGRAVE:'à',
		127+ELConstants.CCEDIL:'ç', 127+ELConstants.ECIRC:'ê', 127+ELConstants.EUML:'ë', 127+ELConstants.EGRAVE:'è',
		127+ELConstants.IUML:'ï', 127+ELConstants.OCIRC:'ô', 127+ELConstants.uGRAVE:'ù', 127+ELConstants.aUMLAUT:'ä',
		127+ELConstants.oUMLAUT:'ö', 127+ELConstants.uUMLAUT:'ü', 127+ELConstants.AUMLAUT:'Ä',
		127+ELConstants.OUMLAUT:'Ö', 127+ELConstants.UUMLAUT:'Ü', 127+ELConstants.DOUBLES:'ß',
		127+ELConstants.aELIG:'æ', 127+ELConstants.oSLASH:'ø', 127+ELConstants.aRING:'å',
		127+ELConstants.AELIG:'Æ', 127+ELConstants.OSLASH:'Ø', 127+ELConstants.ARING:'Å',
		127+ELConstants.EnyE:'ñ', 127+ELConstants.ENYE:'Ñ', 127+ELConstants.aACCENT:'á', 127+ELConstants.AACCENT:'Á',
		127+ELConstants.EACCENT:'É', 127+ELConstants.iACCENT:'í', 127+ELConstants.IACCENT:'Í',
		127+ELConstants.oACCENT:'ó', 127+ELConstants.OACCENT:'Ó', 127+ELConstants.uACCENT:'ú',
		127+ELConstants.UACCENT:'Ú'}

def special_char_to_char(sch):
	return special_char_table[ord(sch)]

def strip_chars(str):
	"""Remove protocol or control characters from the given string"""
	stripped_str = ""

	for char in str:
		if not is_colour(char):
			if is_special_char(char):
				stripped_str += special_char_to_char(char)
			else:
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

el_colour_char_table = {ELConstants.C_RED1:( 1.0000 , 0.7020 , 0.7569 ),
		ELConstants.C_RED2:( 0.9804 , 0.3529 , 0.3529 ),
		ELConstants.C_RED3:( 0.8667 , 0.0078 , 0.0078 ),
		ELConstants.C_RED4:( 0.4941 , 0.0118 , 0.0118 ),
		ELConstants.C_ORANGE1:( 0.9686 , 0.7686 , 0.6235 ),
		ELConstants.C_ORANGE2:( 0.9882 , 0.4784 , 0.2275 ),
		ELConstants.C_ORANGE3:( 0.7490 , 0.4000 , 0.0627 ),
		ELConstants.C_ORANGE4:( 0.5137 , 0.1882 , 0.0118 ),
		ELConstants.C_YELLOW1:( 0.9843 , 0.9804 , 0.7451 ),
		ELConstants.C_YELLOW2:( 0.9882 , 0.9255 , 0.2196 ),
		ELConstants.C_YELLOW3:( 0.9059 , 0.6824 , 0.0784 ),
		ELConstants.C_YELLOW4:( 0.5098 , 0.4353 , 0.0235 ),
		ELConstants.C_GREEN1:( 0.7882 , 0.9961 , 0.7961 ),
		ELConstants.C_GREEN2:( 0.0196 , 0.9804 , 0.6078 ),
		ELConstants.C_GREEN3:( 0.1451 , 0.7686 , 0.0000 ),
		ELConstants.C_GREEN4:( 0.0784 , 0.5843 , 0.0157 ),
		ELConstants.C_BLUE1:( 0.6627 , 0.9373 , 0.9804 ),
		ELConstants.C_BLUE2:( 0.4627 , 0.5922 , 0.9725 ),
		ELConstants.C_BLUE3:( 0.2667 , 0.2824 , 0.8235 ),
		ELConstants.C_BLUE4:( 0.0588 , 0.0588 , 0.7294 ),
		ELConstants.C_PURPLE1:( 0.8235 , 0.7059 , 0.9843 ),
		ELConstants.C_PURPLE2:( 0.8510 , 0.3647 , 0.9569 ),
		ELConstants.C_PURPLE3:( 0.5098 , 0.3294 , 0.9647 ),
		ELConstants.C_PURPLE4:( 0.4157 , 0.0039 , 0.6745 ),
		ELConstants.C_GREY1:( 1.0000 , 1.0000 , 1.0000 ),
		ELConstants.C_GREY2:( 0.6000 , 0.6000 , 0.6000 ),
		ELConstants.C_GREY3:( 0.6196 , 0.6196 , 0.6196 ),
		ELConstants.C_GREY4:( 0.1569 , 0.1569 , 0.1569 )
		}


def el_colour_to_rgb(colour):
	if colour > 127:
		colour -= 127
	return el_colour_char_table[colour]
