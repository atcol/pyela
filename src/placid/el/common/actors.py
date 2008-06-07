
class ELActor(object):
	"""An actor on the EL server"""
	
	def __init__(self):
		self.id = -1
		self.name = None
		self.guild = None
		self.health = 0
		self.max_health = 100
		self.x_pos = 0
		self.y_pos = 0
		self.z_pos = 0
		self.z_rot = 0
		self.frame = 0
		self.kind_of_actor = -1
	
	def __str__(self):
		return repr("%d - %s (%s)" % (self.id, self.name, self.guild))
