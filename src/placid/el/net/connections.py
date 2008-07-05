import socket
import os
import logging
import struct
import time
import ConfigParser
import collections

from placid.net.connections import BaseConnection
from placid.el.net.elconstants import ELConstants
from placid.el.net.elconstants import ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.net.packethandlers import BasePacketHandler
from placid.el.common.exceptions import ConnectionException
from placid.el.logic.session import ELSession, get_elsession_by_config

CONNECTED, CONNECTING, DISCONNECTED = range(3)

log = logging.getLogger('placid.el.net.connections')

def get_elconnection_by_config(config):
	"""Create a connection by using the ConfigParser instance, config."""
	elc = ELConnection(
		config.get('login', 'username'), config.get('login', 'password'), \
		host=config.get('login', 'host'), port=config.getint('login', 'port') \
	)
	elc.set_properties(config)
	return elc 

class ELConnection(BaseConnection):
	"""This class provides an easy to use way of communicating with an Eternal Lands
	server. 

	Attributes:
		host		- the hostname to connect to
		port		- the port to connect to on self.host
		username	- the EL username to use when logging in
		password	- the plaintext password to use to log in
		status		- the status of this connection, at construction this is 
					  set to DISCONNECTED. See placid.el.net.connections
		last_send	- the time.time() of our last packet transmission
		con_tries	- how many times we've tried to connect
		MAX_CON_TRIES - the maximum amount of [re]connection attempts
		MAX_LAST_SEND_SECS - the maximum amount of wait in seconds, 
							that we can send a packet
		packet_handler - the packet handler instance used to process input and generated output
							from the underlying connection. By default, this is assigned to 
							BasePacketHandler
	"""

	def __init__(self, username, password, host='game.eternal-lands.com', port=2001,\
		packet_handler=BasePacketHandler(), MAX_CON_TRIES=3, MAX_LAST_SEND_SECS=18):
		"""Create an instance with the given username and password, 
		as well as the hostname and port.
		This constructor will assume default values for attributes 
		for all but the username and password
		
		Parameters:
			username - the EL username
			password - the password
			host	 - the hostname, default 'game.eternal-lands.com'
			port	 - the port, default 2001
			packet_handler - the packet/message handler, defaults to BasePacketHandler()
			MAX_CON_TRIES - the maximum amount of connection attempts, default 3
			MAX_LAST_SEND_SECS - the maximum amount of seconds allowed between 
								 messages to the server, default 18
			incomplete_msgs - list of ELPacket instances who are incomplete
		"""
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.status = DISCONNECTED
		self.socket = None
		self.last_send = None #property(fset=__set_last_send)
		self.con_tries = 0
		self.MAX_CON_TRIES = MAX_CON_TRIES
		self.MAX_LAST_SEND_SECS = MAX_LAST_SEND_SECS
		self.packet_handler = packet_handler
		self._inp = ""# this is temporary

	def set_properties(self, config):
		"""Load the configuration parameters from config.
		config must be an instance of ConfigParser.
		self.config is set to config before parsing
		"""
		self.config = config
		self.username = self.config.get('login', 'username')
		self.password = self.config.get('login', 'password')
		self.host = self.config.get('login', 'host')
		self.port = self.config.getint('login', 'port')
		self.MAX_CON_TRIES = config.getint('actions', 'max_recon')
		self.MAX_LAST_SEND_SECS = config.getint('actions', 'max_send_secs')
		self.session = get_elsession_by_config(config)
		self._inp = "" # input buffer, for incomplete messages
	
	def fileno(self):
		"""Allows this object to be used with poll() etc"""
		if not self.is_connected():
			raise ConnectionException("Instance not connected to remote server, no fileno available")
		return self.socket.fileno()

	def is_connected(self):
		return self.status == CONNECTED

	def connect(self):
		"""Connects to the EL server specified at construction"""
		if self.is_connected():
			raise ConnectionException("Already connected")
		self.__setup_socket()
		self.con_tries += 1
		return self._send_login()

	def reconnect(self):
		"""Shuts down the socket, then reinitialises and reopens the connection."""
		if self.con_tries >= self.MAX_CON_TRIES:
			raise ConnectionException("Max connection retries has been exceeded")
		self.disconnect()
		return self.connect()

	def disconnect(self):
		"""Closes our socket gracefully"""
		self.send(ELPacket(ELNetToServer.BYE, None))
		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket = None
		self.status = DISCONNECTED

	def _send_login(self):
		if self.socket is None:
			self.__setup_socket()

		login_str = '%s %s\0' % (self.username, self.password)
		try:
			log.debug("port: %s" % type(self.port))
			log.info('Connecting to %s:%d' % (self.host, self.port))
			ret = self.socket.connect_ex((self.host, self.port))
			if ret == 0:
				self.send(ELPacket(ELNetToServer.LOG_IN, login_str))	
				self.status = CONNECTED
				self.socket.setblocking(1)
				self.__set_last_send(time.time())
				return True
			else:
				log.error("Error %d connecting - %s" % (ret, os.strerror(ret)))
				self.status = DISCONNECTED
				self.err = os.strerror(ret)
				return False
		except (socket.error, socket.herror, socket.gaierror), why:
			self.error = "Connection failed: %i - %s" % (why[0], why[1])
			self.socket = None
			self.status = DISCONNECTED
			return False


	def __setup_socket(self):
		if self.socket is None:
			#log.info('Connecting to %s:%s' % (self.host, self.port))
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			except (socket.error, socket.herror, socket.gaierror), why:
				log.error('Failed to create socket: %i: %s' % tuple(why))
				self.socket = None
				return False
	
	def keep_alive(self):
		"""Calls ping if last_send exceeds MAX_LAST_SEND_SECS"""
		diff = int(time.time() - self.last_send)
		if self.is_connected() and diff >= self.MAX_LAST_SEND_SECS:
			self.send(ELPacket(ELNetToServer.HEART_BEAT, None))
	
	def send(self, packet):
		"""Constructs the type and data in the ELPacket instance, packet and transmits"""
		log.debug("Sending %s, %s" % (packet.type, packet.data))
		if packet.data is not None:
			length = len(packet.data) + 1
		else:
			length = 1
		to_send = struct.pack('<BH', packet.type, length)
		if packet.data is not None:
			to_send += packet.data
		self.socket.send(to_send)
		self.__set_last_send(time.time())
		log.debug("Packet sent")
	
	def send_all(self, packets):
		for packet in packets:
			self.send(packet)

	def recv(self, length=2048):
		"""Return the contents of the socket. length is optional, defaults to 2048"""
		packets = []
		def parse_message():
			"""Return the packet type (see ELConstants) and its data as a tuple"""
			while len(self._inp) >= 3:
				header = struct.unpack('<BH', self._inp[:3])
				msg_len = header[1]-1
				if len(self._inp) >= msg_len+3:
					yield ELPacket(header[0], self._inp[3:3+msg_len])
					#Get rid of the message we just returned
					self._inp = self._inp[3+msg_len:] 
				else:
					#We don't have the entire message, abort
					return
		self._inp += self.socket.recv(length)
		for packet in parse_message():
			if packet:
				packets.append(packet)
		return packets

	def __set_last_send(self, t):
		self.last_send = t

	def __str__(self):
		return "%s @ %s:%d" % (self.username, self.host, self.port)

#class QueuedELConnection(ELConnection):
	#"""Derived from ELConnection. 
	#Replaces the send method to force use of _opt, the packet
	#output queue.
	#The queue method has been introduced for appending packets that
	#do not need to be sent immediately
	#"""
	
	#def __init__(self, username, password, host='game.eternal-lands.com', port=2001, MAX_CON_TRIES=3, MAX_LAST_SEND_SECS=18):
		#"""Same as ELConnection, apart from the new _opt list for
		#queuing packets
		#"""
		#self.host = host
		#self.port = port
		#self.username = username
		#self.password = password
		#self.status = DISCONNECTED
		#self.socket = None
		#self.last_send = None #property(fset=__set_last_send)
		#self.con_tries = 0
		#self.MAX_CON_TRIES = MAX_CON_TRIES
		#self.MAX_LAST_SEND_SECS = MAX_LAST_SEND_SECS
		#self._opt = []

	#def send(self, packet):
		#"""Overrides send() in ELConnection. Appends packet to
		#the output queue then sends all in that queue.
		#"""
		#self._opt.append(packet)
		#self.flush_queue()
		
	#def queue(self, packet):
		#"""Place the given packet in the queue ready to be sent"""
		#self._opt.append(packet)
	
	#def flush_queue(self):
		#"""send all the packets in the output queue"""
		#for packet in self.packets:
			#self.packets.remove(packet)
			#super(QueuedELConnection, self).send(packet)
