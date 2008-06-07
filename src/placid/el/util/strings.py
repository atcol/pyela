from placid.el.net.elconstants import ELConstants

def strip_chars(str):
	"""Remove protocol or control characters from the given string"""
	stripped_str = ""

	for char in str:
		if ord(char) < 127+ELConstants.C_LBOUND or ord(char) > 127+ELConstants.C_UBOUND:
			stripped_str += char

	return stripped_str
