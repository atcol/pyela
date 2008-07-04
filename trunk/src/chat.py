#!/usr/bin/env python
import os
import sys

from placid.el.gui.chat import ChatGUI
from placid.el.net.connections import ELConnection

username = ""
password = ""

print "Loading properties from " , os.environ['HOME'] + ".elc/main/el.ini"

# check if el.ini is present
if os.path.exists(os.environ['HOME'] + "/.elc/main/el.ini"):
	elini = open(os.environ['HOME'] + "/.elc/main/el.ini", 'r')
	for line in elini.readlines():
		if line.find("#username = ") != -1:
			username = line.split('=')[1].replace('"', '').strip()
		elif line.find("#password = ") != -1:
			password = line.split('=')[1].replace('"', '').strip()
	elini.close()

else:
	print "You'll need to provide a username and password in %s/.elc/main/el.ini. A login GUI is in development." % os.environ['HOME']
	sys.exit(1)

print "Connecting with username '%s' and password (length) %d" % (username, len(password))
elc = ELConnection(username, password, host='game.eternal-lands.com', port=2000)
c = ChatGUI(elc)
