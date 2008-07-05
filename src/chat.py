#!/usr/bin/env python
import os
import sys

from placid.el.gui.login import LoginGUI
from placid.el.gui.chat import ChatGUI
from placid.el.net.connections import ELConnection

elini_path = os.environ['HOME'] + "/.elc/main/el.ini"

def main():
	USERNAME = ""
	PASSWORD = ""
	HOST = 'game.eternal-lands.com'
	PORT = 2001
	elc = None

	# check if el.ini is present
	if el_ini_exists():
		print "Found el.ini. Will parse username and password from it"
		usr_pass = get_login_elini()
		USERNAME = usr_pass[0]
		PASSWORD = usr_pass[1]
		# user may be set, but not pass

	if len(USERNAME) == 0 or len(PASSWORD) == 0:
		print "Login info. not available via el.ini. Showing Login GUI"
		l = LoginGUI()
		if not l.LOG_IN_OK:
			print "Login failed"
			sys.exit(1)
		else:
			elc = l.elc
	
	# getting login info went OK
	if not elc:
		elc = ELConnection(USERNAME, PASSWORD, host=HOST, port=PORT)
	c = ChatGUI(elc)

def el_ini_exists():
	 return os.path.exists(elini_path)
	
def get_login_elini():
	elini = open(elini_path)
	USERNAME = ""
	PASSWORD = ""
	for line in elini.readlines():
		if line.find("#username = ") != -1:
			USERNAME = line.split('=')[1].replace('"', '').strip()
			if len(USERNAME) == 0:
				print "Username not set in el.ini"
				break
		elif line.find("#password = ") != -1:
			PASSWORD = line.split('=')[1].replace('"', '').strip()
			if len(PASSWORD) == 0:
				print "Password not set in el.ini"
				break
	elini.close()
	return (USERNAME, PASSWORD)

if __name__ == '__main__':
	main()
