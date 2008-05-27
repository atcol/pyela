import socket
import os
import logging as log
import struct
import time
import ConfigParser

from placid.el.net.elconstants import ELConstants
from placid.el.net.elconstants import ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.common.exceptions import ConnectionException

CONNECTED, DISCONNECTED = range(2)

def get_elconnection_by_config(config):
	"""Create a connection by using the ConfigParser instance, config."""
	elc = ELConnection(
		config.get('login', 'username'), config.get('login', 'password'), \
		host=config.get('login', 'host'), port=config.getint('login', 'port') \
	)
	elc.set_properties(config)
	return elc

class BaseConnection(object):
	"""Base connection class that defines common functionality for TCP connections"""

	def fileno(self):
		"""Return the fileno for this connection's socket?"""
		pass
	
	def is_connected(self):
		"""Are we connected?"""
		pass

	def connect(self):
		"""Connects to a remote server"""
		pass
	
	def reconnect(self):
		"""Disconnects then reconnects"""
		pass

	def disconnect(self):
		"""Closes the connection gracefully"""
		pass

	def keep_alive(self):
		"""Should call ping() if connection state deems necessary"""
		pass

	def ping(self):
		"""send a packet to the server to keep this connection alive
		Entirely implementation specific - some protocols may not need it
		"""
		pass

	def send(self, packet):
		"""sends the given packet to the remote server"""
		pass
	
	def recv(self, length=2048):
		"""process input and convert to an instance of placid.el.net.packets.Packet"""
		pass


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
	"""

	def __init__(self, username, password, host='game.eternal-lands.com', port=2001, MAX_CON_TRIES=3, MAX_LAST_SEND_SECS=18):
		"""Create an instance with the given username and password, 
		as well as the hostname and port.
		This constructor will assume default values for attributes 
		for all but the username and password
		
		Attributes:
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

	
	def fileno(self):
		"""Allows this object to be used with poll() etc"""
		return self.socket.fileno()

	def is_connected(self):
		return self.status == CONNECTED

	def connect(self):
		"""Connects to the EL server specified at construction"""
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
		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket = None

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
				#An actual error, pass handling to the except block
				log.error("Error connecting: %s" % ret)
				log.error("\t%d = %s" % (ret, os.strerror(ret)))
				self.status = DISCONNECTED
				raise socket.error, (ret, os.strerror(ret))
		except (socket.error, socket.herror, socket.gaierror), why:
			log.error('Connecting to %s:%i failed: %i: %s' % (self.host, self.port, why[0], why[1]))
			self.socket = None
			self.status = DISCONNECTED
			raise ConnectionException('Socket error during connection: %s' % why[1])
			return False


	def __setup_socket(self):
		if self.socket is None:
			#log.info('Connecting to %s:%s' % (self.host, self.port))
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				#Set non-blocking while connecting
				#self.socket.setblocking(0)
			except (socket.error, socket.herror, socket.gaierror), why:
				log.error('Failed to create socket: %i: %s' % tuple(why))
				self.socket = None
				return False
	
	def keep_alive(self):
		"""Calls ping if last_send exceeds MAX_LAST_SEND_SECS"""
		if int(time.time() - self.last_send) >= self.MAX_LAST_SEND_SECS:
			self.ping()
	
	def ping(self):
		"""send a HEART_BEAT packet"""
		self.send(ELPacket(ELNetToServer.HEART_BEAT, '\0'))

	def send(self, packet):
		"""Constructs the type and data in the ELPacket instance, packet and transmits"""
		log.debug("Sending %s, %s" % (packet.type, packet.data))
		length = len(packet.data) + 1
		to_send = struct.pack('<BH', packet.type, length)
		if packet.data is not None:
			to_send += packet.data
		self.socket.send(to_send)
		self.__set_last_send(time.time())
		log.debug("Packet sent")

	def recv(self, length=2048):
		"""Return the contents of the socket. length is optional, defaults to 2048"""
		packets = []
		def parse_message(raw_data):
			"""Return the packet type (see ELConstants) and its data as a tuple"""
			pos = 0
			while pos < len(raw_data):
				if len(raw_data[pos:]) >= 3:
					header = struct.unpack('<BH', raw_data[pos:pos+3])
					msg_len = header[1]
					yield ELPacket(header[0], raw_data[pos+3:pos+2+msg_len])
					pos += 2+msg_len
				else:
					#We don't have the entire header, return what we have
					yield ELPacket(-1, raw_data[pos:])
					break
			return
		data = self.socket.recv(length)
		for packet in parse_message(data):
			packets.append(packet)
		return packets

	def __set_last_send(self, t):
		self.last_send = t

	def __str__(self):
		return "%s @ %s:%d" % (self.username, self.host, self.port)

