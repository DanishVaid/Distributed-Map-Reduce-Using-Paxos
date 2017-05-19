
class Paxos(object):
	
	def __init__(self, ID):
		self.ID = ID

		self.isLeader = False

		self.ballotNum = {0: 0}	#MAYBE DIFFERENT DATA STRUCTURE
		self.acceptNum = {0: 0}
		self.acceptVal = None


	def prepare(self):
		message = "prepare" + str(ballotNum)	#SPLIT UP TO KEY/VALUE PAIR, +1



	def receive(self):



	def acknowledge(self):



	def accept(self):



	def accepted(self):




