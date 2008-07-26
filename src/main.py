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
import ConfigParser
import os
import logging as log
import signal
import sys

from placid.el.net.connections import get_elconnection_by_config, ELConnection
from placid.el.logic.managers import MultiConnectionManager
from placid.el.logic.session import ELSession, get_elsession_by_config
from placid.el.net.packethandlers import ELTestPacketHandler

connections = []

# signal handlers
def sig_cleanup(signal, frame):
	log.info("Caught %s at frame %s, quitting" % (signal, frame))
	log.debug("Closing connections: %s" % connections)
	for con in connections:
		con.disconnect()
	sys.exit(0)

def sig_hup(signal, frame):
	for con in connections:
		con.disconnect()
	main()

def main():
	signal.signal(signal.SIGHUP, sig_cleanup)
	signal.signal(signal.SIGINT, sig_cleanup)
	signal.signal(signal.SIGTERM, sig_cleanup)
	signal.signal(signal.SIGQUIT, sig_cleanup)
	signal.signal(signal.SIGPIPE, signal.SIG_IGN)

	sys_cfg = ConfigParser.ConfigParser()# system-wide settings
	sys_cfg.read('system.ini')

	for file in os.listdir('./bots'):
		if file.endswith(".ini"):
			cfg = ConfigParser.ConfigParser()
			cfg.read("bots/%s" % file)
			con = get_elconnection_by_config(cfg)
			con.packet_handler = ELTestPacketHandler(con.session)
			connections.append(con)
	
	log.basicConfig(level=getattr(log, sys_cfg.get('logging', 'level').upper()), format="%(asctime)s %(name)s %(levelname)s: %(message)s", filename=sys_cfg.get('logging', 'filename'))
	elcm = MultiConnectionManager(connections)
	elcm.process()

if __name__ == '__main__':
	main()
