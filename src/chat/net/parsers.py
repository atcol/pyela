import struct
from pyela.el.net.parsers import MessageParser
from pyela.el.net.elconstants import ELNetFromServer, ELNetToServer, ELConstants
from pyela.el.util.strings import is_colour, strip_chars#, split_str, el_colour_to_rgb

class GUIRawTextMessageParser(MessageParser):
	def parse(self, packet):
		if struct.unpack('<b', packet.data[0])[0] in \
			(ELConstants.CHAT_CHANNEL1, ELConstants.CHAT_CHANNEL2, ELConstants.CHAT_CHANNEL3):
			channel = int(struct.unpack('<b', packet.data[0])[0])
			text = strip_chars(packet.data[1:])
			self.session.msg_buf.extend(["\n%s" % (text.replace(']', " @ %s]" % \
				self.session.channels[int(channel - ELConstants.CHAT_CHANNEL1)].number))])
		else:
			if is_colour(packet.data[1]):
				pass
			self.session.msg_buf.extend(["\n%s" % strip_chars(packet.data[1:])])
		return []
	
