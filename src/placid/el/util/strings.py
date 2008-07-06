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
