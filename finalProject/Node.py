
class Node(object):	#MAY NOT NEED THIS CLASS
	
	def __init__(self):
		self.mappers = [Mapper(), Mapper()]
		self.reducer = Reducer()
		self.client = CLI()
		self.paxos = Paxos()