
class Paxos(object):
	
	def __init__(self, ID):
		self.ID = ID

		self.isActive = True
		self.isLeader = False

		self.ballotNum = {0: 0}	#MAYBE DIFFERENT DATA STRUCTURE
		self.acceptNum = {0: 0}
		self.acceptVal = None

		self.socketFromPaxos = None
		self.socketsToPaxos = []

		self.connection = Connection()


	def prepare(self):
		outMessage = "prepare " + str(ballotNum)	#SPLIT UP TO KEY/VALUE PAIR, +1

		#SEND TO ALL OTHER PRMS


	def acknowledge(self, senderID, proposedNum):
		pass
		#CHECK IF PROPOSEDNUM > PREVIOUSLY ACCEPTED NUM
			#IF SO, SEND ACK

			#IF NOT, DON'T KNOW WHAT TO DO YET


	def accept(self):
		outMessage = "accept " + str(acceptNum)		#SPLIT UP TO KEY/VALUE PAIR, +1

		#SEND TO ALL OTHER PRMS


	def accepted(self, senderID, acceptingNum):	#RENAME VARIABLE
		pass
		#CHECK IF ACCEPTINGNUM >= PREVIOUS ACCEPTNUM
			#IF SO, SEND ACCEPTED MESSSAGE

			#IF NOT, DON'T KNOW WHAT TO DO YET


	def stop(self):
		self.isActive = False


	def resume(self):
		self.isActive = True


	def receive(self):
		#RECEIVE MESSAGE
		inMessage = ""	#PLACEHOLDER
		inMessage = inMessage.split(" ")

		if inMessage[0] == "prepare":
			if self.isActive:
				acknowledge(senderID, proposedNum)

		elif inMessage[0] == "accept":
			if self.isActive:
				accept(senderID, proposedNum)

		elif inMessage[0] == "replicate":
			if self.isActive:
				prepare()

		elif inMessage[0] == "stop":
			stop()

		elif inMessage[0] == "resume":
			resume()
		#ELIF MORE POSSIBLE CASES

		else:
			print("ERROR, should never reach here")


	def makeConnection(self):
		pass
		#SHOULD HAVE CONNECTION FROM CLI
		#SHOULD ALSO HAVE INCOMING AND OUTGOING CONNECTION TO ALL OTHER PAXOS