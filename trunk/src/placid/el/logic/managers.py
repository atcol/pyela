import time
import select
import struct
import sys
import datetime
import logging as log
import ConfigParser

from placid.el.net.connections import ELConnection
from placid.el.net.elconstants import ELConstants
from placid.el.net.elconstants import ELNetFromServer, ELNetToServer
from placid.el.net.packets import ELPacket
from placid.el.logic.session import ELSession
from placid.el.common.exceptions import ConnectionException, ManagerException

LAST_ASTRO_MAX_SECS = 60

LAST_ASTRO_MAX_MINS = 1

HEART_BEAT_MAX_SECS = 19

POLL_TIMEOUT_MILLIS = HEART_BEAT_MAX_SECS * 1000

class ConnectionManager(object):
	"""A manager for a Connection object"""
	def __init__(self):
		pass

	def __init__(self, connection):
		self.connection = connection

	def process(self):
		"""Process the connection's input"""
		pass

class MultiConnectionManager(ConnectionManager):
	"""A derived class from ConnectionManager.
	This implementation can handle multiple instances of 
	placid.el.net.connections.Connection

	Attributes:
		_p 			- instance of select.poll(); leave it alone
		connection  - the placid.el.net.Connection instance passed
				 	  to init
		config		- the instance of ConfigParser, passed to init
		_opt		- the packet output buffer; leave it alone
		_inp		- the packet input buffer; leave it alone
		session		- the ELSession instance, representing the data
					  for this connection
	"""

	def __init__(self, connections):
		"""Creates an instane with the given config, and the given connections"""
		self._p = select.poll()
		if None not in connections:
			self.connections = connections
		else:
			raise ManagerException('None cannot be a connection')
		#self.connection.MAX_CON_TRIES = config.getint('actions', 'max_recon')
		#self._opt = {}
		#self._inp = {}


	def __set_opt(self, val):
		log.info("Something's trying to set my output queue. Blocked!")
		pass

	def add_connection(self, con):
		"""Appends the given connection to the connection list, and calls connect"""
		con.connect()
		self.connections.append(con)
		self.__register_connections()

	def process(self):
		"""Overrides super's process impl to govern all the connections """
		#if not self.connection.is_connected():
			#self.connection.connect()
			#if self.config.get('actions', 'send_login'):
				#self._opt.append(ELPacket(ELNetToServer.RAW_TEXT, self.session.get_login_messages()[0]))

		self.__connect_all()

		if len(self.connections) > 0:
			self.__register_connections()
		else:
			raise ManagerException('Cannot register connections. None provided')

		# the contents of each NEW_MINUTE packet
		el_mins = -1
		# the amount of EL minutes since our last astro send
		min_count = 0
		
		while len(self.connections) > 0:
			#log.debug("Got %s from poll()" % p_opt)
			#log.debug("Last packet diff: %d" % int(time.time() - self.connection.last_send))

			poll_time = self.__calc_poll_time()
			log.debug("Setting poll with timeout %d" % poll_time)
			p_opt = self._p.poll(poll_time)
			log.debug("Poll ended: %s" % p_opt)


			# p_opt may be empty, which means the timeout occured
			if len(p_opt) == 0:
				# no input from our connections
				log.debug("Poll returned nothing. Processing connection opt queue")
				# check if we need to send a keep-alive
				for con in self.connections:
					con.keep_alive()# send a keep-alive packet if we need to
				# process output queue??
			else:
				# 
				# data received in a connection, find which
				# get the connection poll is referring to

				p_event = None
				for p in p_opt:
					p_event = p
					p_fileno = p[0] # the file descriptor and poll event
					con = self.get_connection_by_id(p_fileno)
					if p[1] & select.POLLIN or p[1] & select.POLLPRI:
						# found the con poll's referring to
						log.info("Got data for connection '%s'" % con)
						packets = con.recv(length=2048)
						#log.debug("Bytes (%d): %s" % (len(bytes), bytes))
						if len(packets) != 0:
							log.debug("Received %d packets" % len(packets))
							for packet in packets:
								log.info("Message: %s?, %d, type=%s" % \
								(ELNetFromServer.to_identifier(ELNetFromServer(), int(packet.type)), packet.type, type(packet)))
								
								"""deal with the packets outside of here, using an event handler?"""
								#self._inp.extend(packets)
						else:
							log.error("Empty packets returned. Connection down? Reconnecting... (con=%s)" % con)
							self.__reconnect(con)
							self.__register_connections()
					elif p[1] & select.POLLERR:
						log.error("Pol returned an error for %s" % con)



			
			"""Process output queue?"""
			self.__process_opt_queue()

	def __reconnect(self, con):
		if not con.is_connected():
			log.info("Reconnect failed. Sleeping...")
			# connection retries sleep
			time.sleep(self.config.getint('actions', 'reconnect_secs'))
			try:
				return con.reconnect()
			except ConnectionException, ce:
				log.error("Exception when reconnecting: %s" % ce)

	def get_connection_by_id(self, id):
		for con in self.connections:
			if con.fileno() == id:
				return con
		return None

	def __calc_poll_time(self):
		"""Calculate the poll time from all the connections in milliseconds, 
		based on their MAX_LAST_SEND_SECS and their last_send value
		"""
		poll_time = 20
		for con in self.connections:
			this_pt = int(con.MAX_LAST_SEND_SECS - int(time.time() - con.last_send))
			log.debug("Calc'd poll time for %s is %d" % (con, int(this_pt)))
			if this_pt < poll_time:
				poll_time = this_pt

		return int(poll_time * 1000)

	def __process_opt_queue(self):
		pass
		#for packet in self._opt:
			#self.connection.send(packet)
			#self._opt.remove(packet)
		#for con in self.connections:
			#con.process_queue()

	def __connect_all(self):
		"""call connect on all the connections if con.is_connected() yields False"""
		for con in self.connections:
			if not con.is_connected():
				con.connect()

	def __register_connections(self):
		for con in self.connections:
			log.debug("Registering %s" % con)
			if con.is_connected():
				self._p.register(con, select.POLLIN | select.POLLPRI | select.POLLERR)
