# reactset is a structure that contains a reference to a message, and a dictionary of reaction : role to give
# permdict is a dictionary of role : permission role, such that a user cannot get role unless they have permission role
# TODO: Consider shifting back to script file and importing contents from something else eg. csv or json or something

class reactset:
	def __init__(self,link,roles,perms=None):
		linklist = link.split("/")
		self.svr = int(linklist[0])
		self.chnl = int(linklist[1])
		self.msg = int(linklist[2])

		self.reactdict = roles #give as dict
		self.permdict = perms