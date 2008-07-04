import ConfigParser
import os
import logging as log
import signal
import sys

from placid.el.net.connections import get_elconnection_by_config, ELConnection
from placid.el.logic.managers import MultiConnectionManager
from placid.el.logic.session import ELSession
from placid.el.net.packethandlers import ELTestPacketHandler

connections = []

# 18 secs for testing
LAST_ASTRO_MAX_SECS = 60

LAST_ASTRO_MAX_MINS = 1

HEART_BEAT_MAX_SECS = 19

POLL_TIMEOUT_MILLIS = HEART_BEAT_MAX_SECS * 1000

# signal handlers

def sig_cleanup(signal, frame):
	log.info("Caught %s at frame %s, quitting" % (signal, frame))
	log.debug("Closing connections: %s" % connections)
	for con in connections:
		con.disconnect()
	sys.exit(0)

def main():
	signal.signal(signal.SIGHUP, sig_cleanup)
	signal.signal(signal.SIGINT, sig_cleanup)
	signal.signal(signal.SIGTERM, sig_cleanup)
	signal.signal(signal.SIGQUIT, sig_cleanup)
	signal.signal(signal.SIGPIPE, signal.SIG_IGN)

	sys_cfg = ConfigParser.ConfigParser()
	sys_cfg.read('system.ini')

	for file in os.listdir('./bots'):
		if file.endswith(".ini"):
			cfg = ConfigParser.ConfigParser()
			cfg.read("bots/%s" % file)
			con = get_elconnection_by_config(cfg)
			session = ELSession(cfg)
			con.packet_handler = ELTestPacketHandler(session)
			connections.append(con)
	
	log.basicConfig(level=getattr(log, sys_cfg.get('logging', 'level').upper()), format="%(asctime)s %(name)s %(levelname)s: %(message)s", filename=sys_cfg.get('logging', 'filename'))
	elcm = MultiConnectionManager(connections)
	elcm.process()

if __name__ == '__main__':
	main()
