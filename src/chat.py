#!/usr/bin/env python
import os
import sys

from placid.el.gui.login import LoginGUI
from placid.el.gui.chat import ChatGUI
from placid.el.net.connections import ELConnection

elini_path = os.environ['HOME'] + "/.elc/main/el.ini"

print "Loading properties from" , elini_path

def main():
	USERNAME = ""
	PASSWORD = ""
	# check if el.ini is present
	if el_ini_exists():
		print "Found el.ini. Will parse username and password from it"
		usr_pass = get_login_elini()
		USERNAME = usr_pass[0]
		PASSWORD = usr_pass[1]
		print "%s, %s" % (USERNAME, PASSWORD)

	if len(USERNAME) == 0 and len(PASSWORD) == 0:
		print "Login info. not available via el.ini. Showing Login GUI"
		l = LoginGUI()
		if not l.LOG_IN_OK:
			print "Login failed"
			sys.exit(1)
		else:
			USERNAME = l.elc.username
			PASSWORD = l.elc.password
	
	# getting login info went OK
	print "Connecting with username '%s' and password (length) %d" % (USERNAME, len(PASSWORD))
	elc = ELConnection(USERNAME, PASSWORD, host='game.eternal-lands.com', port=2001)
	c = ChatGUI(elc)

def el_ini_exists():
	 return os.path.exists(elini_path)
	
def get_login_elini():
	elini = open(elini_path)
	for line in elini.readlines():
		if line.find("#username = ") != -1:
			USERNAME = line.split('=')[1].replace('"', '').strip()
			if USERNAME != '':
				print "Global username set"
			else:
				print "Username not set in el.ini"
				break
		elif line.find("#password = ") != -1:
			PASSWORD = line.split('=')[1].replace('"', '').strip()
			if USERNAME != '':
				print "Global password set"
			else:
				print "Password not set in el.ini"
				break
	elini.close()
	return (USERNAME, PASSWORD)

if __name__ == '__main__':
	main()
