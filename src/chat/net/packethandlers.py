from pyela.el.net.packethandlers import ExtendedELPacketHandler
from pyela.el.net.elconstants import ELNetFromServer, ELNetToServer
from net.parsers import GUIRawTextMessageParser

class ChatGUIPacketHandler(ExtendedELPacketHandler):
	def __init__(self, session):
		self.session = session
		self.CALLBACKS = {}
		self.__setup_callbacks()

	def __setup_callbacks(self):
		self.CALLBACKS[ELNetFromServer.RAW_TEXT] = GUIRawTextMessageParser(self.session)
	
	def process_packets(self, packets):
		return super(ChatGUIPacketHandler, self).process_packets(packets)
		# create event objects if any of the packets match 
		# relevant criteria
