
class Paxos(object):
	
	def __init__(self, ID):
		self.ID = ID

		self.isLeader = False

		self.ballotNum = {0: 0}	#MAYBE DIFFERENT DATA STRUCTURE
		self.acceptNum = {0: 0}
		self.acceptVal = None


	def prepare(self):
		outMessage = "prepare" + str(ballotNum)	#SPLIT UP TO KEY/VALUE PAIR, +1


	def acknowledge(self, senderID, proposedNum):



	def accept(self):



	def accepted(self):



	def receive(self):
		#RECEIVE MESSAGE
		inMessage = ""	#PLACEHOLDER
		inMessage = inMessage.split(" ")

		if inMessage[0] == "prepare":
			acknowledge(senderID, proposedNum)

		elif inMessage[0] == "accept":
			accept(senderID, proposedNum)

		else:
			print "ERROR, should never reach here"

