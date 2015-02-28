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
import socket
import os
import logging
import struct
import time
import collections

from pyela.net.connections import BaseConnection
from pyela.el.net.elconstants import ELConstants
from pyela.el.net.elconstants import ELNetToServer
from pyela.el.net.packets import ELPacket
from pyela.el.net.packethandlers import BasePacketHandler
from pyela.el.common.exceptions import ConnectionException
from pyela.el.logic.session import ELSession, get_elsession_by_config
from pyela.logic.event import NetEvent, NetEventType, NET_CONNECTED, NET_DISCONNECTED
from pyela.el.logic.eventmanagers import ELSimpleEventManager

CONNECTED, CONNECTING, DISCONNECTED = range(3)

log = logging.getLogger('pyela.el.net.connections')

def get_elconnection_by_config(config):
	"""Create a connection by using the ConfigParser instance, config."""
	session = get_elsession_by_config(config)
	elc = ELConnection(
		session, \
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
					  set to DISCONNECTED. See pyela.el.net.connections
		last_send	- the time.time() of our last packet transmission
		con_tries	- how many times we've tried to connect
		MAX_CON_TRIES - the maximum amount of [re]connection attempts
		MAX_LAST_SEND_SECS - the maximum amount of wait in seconds, 
							that we can send a packet
		packet_handler - the packet handler instance used to process input and generated output
							from the underlying connection. By default, this is assigned to 
							BasePacketHandler
	"""

	def __init__(self, session, host='game.eternal-lands.com', port=2001,\
		packet_handler=None, MAX_CON_TRIES=3, MAX_LAST_SEND_SECS=18):
		"""Create an instance with the given username and password, 
		as well as the hostname and port.
		This constructor will assume default values for attributes 
		for all but the username and password
		
		Parameters:
			session  - The session object for this connection, must have username and password set
			host	 - the hostname, default 'game.eternal-lands.com'
			port	 - the port, default 2001
			packet_handler - the packet/message handler, defaults to BasePacketHandler()
			MAX_CON_TRIES - the maximum amount of connection attempts, default 3
			MAX_LAST_SEND_SECS - the maximum amount of seconds allowed between 
								 messages to the server, default 18
			incomplete_msgs - list of ELPacket instances who are incomplete
			error	 - String containing an error message for the last error that was encountered
		"""
		self.host = host
		self.port = port
		self.session = session
		self.status = DISCONNECTED
		self.socket = None
		self.last_send = None #property(fset=__set_last_send)
		self.con_tries = 0
		self.MAX_CON_TRIES = MAX_CON_TRIES
		self.MAX_LAST_SEND_SECS = MAX_LAST_SEND_SECS
		if packet_handler == None:
			self.packet_handler = BasePacketHandler() #TODO: Should this be BasePacketHandler or BaseELPacketHandler?
		else:
			self.packet_handler = packet_handler
		self._inp = bytearray()
		self.error = ""

	def set_properties(self, config):
		"""Load the configuration parameters from config.
		config must be an instance of ConfigParser.
		self.config is set to config before parsing
		"""
		self.config = config #TODO: Should this be stored here? It's never used after this
		self.session = get_elsession_by_config(config)
		self.host = self.config.get('login', 'host')
		self.port = self.config.getint('login', 'port')
		self.MAX_CON_TRIES = config.getint('actions', 'max_recon')
		self.MAX_LAST_SEND_SECS = config.getint('actions', 'max_send_secs')
		self._inp = bytearray() # input buffer, for incomplete messages
	
	def fileno(self):
		"""Allows this object to be used with poll() etc"""
		#This will break poll() in MultiConnectionManager because it must know the fileno to unregister a socket
		#if not self.is_connected():
		#	raise ConnectionException("Instance not connected to remote server, no fileno available")
		return self.socket.fileno()

	#TODO: Reconsider this status scheme. Currently CONNECTING is never used.
	def is_connected(self):
		return self.status == CONNECTED

	def connect(self):
		"""Connects to the EL server specified at construction"""
		if self.is_connected():
			raise ConnectionException("Already connected")
		self.con_tries += 1
		if not self.__setup_socket():
			return False
		self._inp = bytearray() #Discard old data
		return self._send_login()

	def reconnect(self):
		"""Shuts down the socket, then reinitialises and reopens the connection."""
		if self.con_tries >= self.MAX_CON_TRIES:
			raise ConnectionException("Max connection retries has been exceeded")
		self.disconnect()
		return self.connect()

	def disconnect(self):
		"""Closes our socket gracefully"""
		if self.status != DISCONNECTED:
			self.send(ELPacket(ELNetToServer.BYE, None)) #This is not really necessary, but d
			self.socket.shutdown(socket.SHUT_RDWR)
		event = NetEvent(NetEventType(NET_DISCONNECTED), self)
		ELSimpleEventManager().raise_event(event)
		if self.socket != None:
			self.socket.close()
		self.socket = None
		self.status = DISCONNECTED

	def _send_login(self):
		if self.session == None or self.session.name == None or self.session.password == None or \
			self.session.name == "" or self.session.password == "":
			self.error = "Username or password not set"
			return False
		login_str = ('%s %s\0' % (self.session.name, self.session.password)).encode('iso8859')
		try:
			log.info('Connecting to %s:%d' % (self.host, self.port))
			ret = self.socket.connect_ex((self.host, self.port))
			if ret == 0:
				self.send(ELPacket(ELNetToServer.LOG_IN, login_str))	
				self.status = CONNECTED
				self.socket.setblocking(1)
				event = NetEvent(NetEventType(NET_CONNECTED), self)
				ELSimpleEventManager().raise_event(event)
				return True
			else:
				log.error("Error %d connecting - %s" % (ret, os.strerror(ret)))
				self.status = DISCONNECTED
				self.disconnect()
				self.error = os.strerror(ret)
				return False
		except (socket.error, socket.herror, socket.gaierror) as why:
			self.error = "%s (%i)" % (why[1], why[0])
			self.status = DISCONNECTED
			self.disconnect()
			return False


	def __setup_socket(self):
		if self.socket is None:
			#log.info('Connecting to %s:%s' % (self.host, self.port))
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			except (socket.error, socket.herror, socket.gaierror) as why:
				self.error = 'Failed to create socket: %i: %s' % tuple(why)
				log.error('Failed to create socket: %i: %s' % tuple(why))
				self.socket = None
				return False
		return True
	
	def keep_alive(self):
		"""Sends a heartbeat to the server so that it knows we're still alive"""
		if self.is_connected():
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
		sent = 0
		while sent < len(to_send):
			#TODO: This may block
			ret = self.socket.send(to_send[sent:])
			if ret == 0 or ret == -1:
				self.status = DISCONNECTED
				self.disconnect()
				raise ConnectionException("Other end disconnected")
			sent += ret
		self.__set_last_send(time.time())
		log.debug("Packet sent")
	
	def send_all(self, packets):
		for packet in packets:
			self.send(packet)

	def recv(self, length=2048):
		"""
			Return the contents of the socket. length is optional, defaults to 2048
			Raises ConnectionException on errors
		"""
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
		ret = self.socket.recv(length)
		if not ret:
			#recv failed, connection dead
			#TODO: Store the error somewhere?
			self.status = DISCONNECTED
			self.disconnect()
			raise ConnectionException("Other end terminated the connection")
		# When python 3 is required: self._inp += bytearray(ret)
		self._inp += ret
		for packet in parse_message():
			packets.append(packet)
		return packets

	def __set_last_send(self, t):
		self.last_send = t

	def __str__(self):
		return "%s @ %s:%d" % (self.session.name, self.host, self.port)
