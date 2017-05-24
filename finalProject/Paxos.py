
class Paxos(object):
	
	def __init__(self, ID):
		self.ID = ID

		self.isLeader = False

		self.ballotNum = {0: 0}	#MAYBE DIFFERENT DATA STRUCTURE
		self.acceptNum = {0: 0}
		self.acceptVal = None


	def prepare(self):
		outMessage = "prepare " + str(ballotNum)	#SPLIT UP TO KEY/VALUE PAIR, +1

		#SEND TO ALL OTHER PRMS


	def acknowledge(self, senderID, proposedNum):
		#CHECK IF PROPOSEDNUM > PREVIOUSLY ACCEPTED NUM
			#IF SO, SEND ACK

			#IF NOT, DON'T KNOW WHAT TO DO YET


	def accept(self):
		outMessage = "accept " + str(acceptNum)		#SPLIT UP TO KEY/VALUE PAIR, +1

		#SEND TO ALL OTHER PRMS


	def accepted(self, senderID, acceptingNum):	#RENAME VARIABLE
		#CHECK IF ACCEPTINGNUM >= PREVIOUS ACCEPTNUM
			#IF SO, SEND ACCEPTED MESSSAGE

			#IF NOT, DON'T KNOW WHAT TO DO YET


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

