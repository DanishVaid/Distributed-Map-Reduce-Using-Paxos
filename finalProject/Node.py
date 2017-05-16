
class Node(object):
	
	def __init__(self):
		#INITIALIZE
		self.mappers = []
		self.reducer = None
		self.client = None
		self.paxos = None