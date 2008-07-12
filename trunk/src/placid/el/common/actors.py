from placid.el.net.elconstants import ELConstants

class ELActor(object):
	"""An actor on the EL server"""
	
	def __init__(self):
		self.id = -1
		self.name = None
		self.name_colour = 0
		self.guild = None
		self.health = 0
		self.max_health = 0
		self.x_pos = 0
		self.y_pos = 0
		self.z_pos = 0
		self.z_rot = 0
		self.kind_of_actor = -1
		self.dead = False
		self.fighting = False
	
	def __str__(self):
		return repr("%d - %s (%s)" % (self.id, self.name, self.guild))
	
	def clamp_z_rot(self):
		"""Makes sure z_rot is between 0 and 360"""
		while self.z_rot >= 360:
			z_rot -= 360
		while self.z_rot < 0:
			self.z_rot += 360
	
	def handle_command(self, cmd):
		"""Applies the actor command cmd to the actor"""
		#Movement tracking:
		if cmd == ELConstants.MOVE_N:
			self.y_pos += 1
			self.z_rot = 0
		elif cmd == ELConstants.MOVE_NE:
			self.x_pos += 1
			self.y_pos += 1
			self.z_rot = 45
		elif cmd == ELConstants.MOVE_E:
			self.x_pos += 1
			self.z_rot = 90
		elif cmd == ELConstants.MOVE_SE:
			self.x_pos += 1
			self.y_pos -= 1
			self.z_rot = 135
		elif cmd == ELConstants.MOVE_S:
			self.y_pos -= 1
			self.z_rot = 180
		elif cmd == ELConstants.MOVE_SW:
			self.x_pos -= 1
			self.y_pos -= 1
			self.z_rot = 225
		elif cmd == ELConstants.MOVE_W:
			self.x_pos -= 1
			self.z_rot = 270
		elif cmd == ELConstants.MOVE_NW:
			self.x_pos -= 1
			self.y_pos += 1
			self.z_rot = 315
		#Rotation tracking:
		elif cmd == ELConstants.TURN_LEFT:
			self.z_rot += 45
			self.clamp_z_rot()
		elif cmd == ELConstants.TURN_RIGHT:
			self.z_rot -= 45
			self.clamp_z_rot()
		#Death tracking
		elif cmd in (ELConstants.DIE1, ELConstants.DIE2):
			self.dead = True
		#Fight tracking
		elif cmd == ELConstants.ENTER_COMBAT:
			self.fighting = True
		elif cmd == ELConstants.LEAVE_COMBAT:
			self.fighting = False

