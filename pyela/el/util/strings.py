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
from pyela.el.net.elconstants import ELConstants

def is_colour(ch):
	"""Returns true if ch is a colour code"""
	if type(ch) == str:
		return ord(ch) >= 127+ELConstants.C_LBOUND and ord(ch) <= 127+ELConstants.C_UBOUND
	else:
		return ch >= 127+ELConstants.C_LBOUND and ch <= 127+ELConstants.C_UBOUND

def is_special_char(ch):
	"""Return true if ch is a foreign character"""
	#The following greater-than is not a typo
	if type(ch) in (bytearray,bytes):
		return ch[0] > ELConstants.SPECIALCHAR_LBOUND and ch[0] <= ELConstants.SPECIALCHAR_UBOUND
	else:
		return ch > ELConstants.SPECIALCHAR_LBOUND and ch <= ELConstants.SPECIALCHAR_UBOUND

special_char_table = {ELConstants.EACUTE:'é', ELConstants.ACIRC:'â', ELConstants.AGRAVE:'à',
		ELConstants.CCEDIL:'ç', ELConstants.ECIRC:'ê', ELConstants.EUML:'ë', ELConstants.EGRAVE:'è',
		ELConstants.IUML:'ï', ELConstants.OCIRC:'ô', ELConstants.uGRAVE:'ù', ELConstants.aUMLAUT:'ä',
		ELConstants.oUMLAUT:'ö', ELConstants.uUMLAUT:'ü', ELConstants.AUMLAUT:'Ä',
		ELConstants.OUMLAUT:'Ö', ELConstants.UUMLAUT:'Ü', ELConstants.DOUBLES:'ß',
		ELConstants.aELIG:'æ', ELConstants.oSLASH:'ø', ELConstants.aRING:'å',
		ELConstants.AELIG:'Æ', ELConstants.OSLASH:'Ø', ELConstants.ARING:'Å',
		ELConstants.EnyE:'ñ', ELConstants.ENYE:'Ñ', ELConstants.aACCENT:'á', ELConstants.AACCENT:'Á',
		ELConstants.EACCENT:'É', ELConstants.iACCENT:'í', ELConstants.IACCENT:'Í',
		ELConstants.oACCENT:'ó', ELConstants.OACCENT:'Ó', ELConstants.uACCENT:'ú',
		ELConstants.UACCENT:'Ú'}

def special_char_to_char(sch):
	"""Convert an EL special character (integer value > 127) to a regular string-compatible character"""
	if type(sch) == str:
		sch = bytes([ord(sch)])
	elif type(sch) == int:
		sch = bytes([sch])
	return str(sch, 'iso8859')

def char_to_special_char(ch):
	"""Convert a non-ascii character (integer value > 127) to an EL-compatible special character"""
	#reverse_table = dict([(v, k) for (k, v) in special_char_table.iteritems()])
	#if ch in reverse_table:
	#	return reverse_table[ch]
	#else:
	#	return None
	
	ch = ch.encode('iso8859', 'replace')
	if is_special_char(ch):
		return ch
	else:
		return None

def strip_chars(s):
	"""Remove protocol and control characters from the given string"""
	stripped_str = ""

	for char in s:
		if not is_colour(char):
			if is_special_char(char):
				stripped_str += special_char_to_char(char)
			elif char < 127 and char > 0:
				# Skip non-ascii characters
				stripped_str += str(chr(char))
	return stripped_str

def str_to_el_str(s):
	"""Convert the special characters in a string to EL format and discard invalid characters"""
	out_str = bytearray()
	for char in s:
		if ord(char) > 127:
			elch = char_to_special_char(char)
			if elch != None:
				out_str.append(ord(elch))
		else:
			out_str += char.encode('ascii', 'replace')
	return out_str

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

def bytes_find(arr, needle):
	"""Search for needle in bytearray"""
	for i in range(0,len(arr)):
		if arr[i] == needle:
			return i
	return -1

def bytes_rfind(arr, needle):
	"""Search for needle in bytearray"""
	for i in reversed(range(0,len(arr))):
		if arr[i] == needle:
			return i
	return -1
