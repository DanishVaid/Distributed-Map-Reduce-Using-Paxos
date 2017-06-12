#!/bin/python3

# import socket 			# To create network connection
# import sys				# For command line arguments
# import Connection		# Makes the Sockets
import Log				# Our Log Class
# import Query
# import queue			# Queue for messages
# from math import floor	# Helps calculate minMajority
# from time import sleep	# Allows for creating sockets in the correct order

class Paxos(object):
	
	def __init__(self, selfID, socketsToPaxos, minMajority, logIndex):
		self.selfID = selfID 				# Index of IP/port pair in config file
		self.minMajority = minMajority
		self.logIndex = logIndex

		self.myProposal = None
		self.ballotNum = (0, 0)				# Tuples storing ballotNum : siteselfID, index of the log to insert into
		self.acceptNum = (0, 0)				# Tuples storing acceptNum : siteselfID
		self.acceptVal = None				# Dictionary to be stored into a log entry

		self.numPromises = 0				# Used to keep track of number of promises, will be compared to minMajority
		self.numVotes = 0					# Used to keep track of number of votes, will be compared to minMajority
		self.numAcceptsReceived = 0			# Used to keep track of number of nodes that have accepted the proposed value

		self.incomingAcceptNums = []		# Used to check if responding nodes' IDs that have sent ballot nums
		self.ackAcceptVals = []				# Used to check if responding nodes have values in their ballot

		self.hasMajorityPromises = False	# Used for checking majority to initiate insertion of a dictionary to the log
		self.isFirstAccept = True			# Nodes should not send more accept messages after the first received accept of a unique value

		self.hasLogged = False

		self.socketsToPaxos = socketsToPaxos


	def prepare(self, fileName):
		print("---START PREPARE---")

		try:
			self.myProposal = self.buildLogEntryFromFile(fileName)

		except FileNotFoundError:
			print("--- Prepare FAILED, File not found:" + fileName + " ---")
			return

		self.ballotNum = (self.ballotNum[0] + 1, self.selfID)
		outMessage = str(self.logIndex) + " prepare " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1])

		for sock in self.socketsToPaxos:
			if sock == None:
				continue

			print("Send prepare from site ID: " + str(self.selfID))
			sock.sendall((outMessage + "%").encode())

		print("---END PREPARE---")


	def acknowledge(self, incomingBallotNum):
		print("---START ACKNOWLEDGE---")

		# If incomingBallotNum does not meet condition, do nothing
		if incomingBallotNum[0] <= self.ballotNum[0]:
			if incomingBallotNum[0] == self.ballotNum[0] and incomingBallotNum[1] < self.ballotNum[1]:
				print("Prepare rejected.")
				return

		self.ballotNum = (incomingBallotNum[0], incomingBallotNum[1])

		# 0		1					2					3				4				5	
		# ack	incBallotNum[0]		incBallotNum[1]		acceptNum[0]	acceptNum[1]	acceptVal
		outMessage = str(self.logIndex) + " ack " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)
		print("Send ack back to siteID (" + str(incomingBallotNum[1]) + ") from own siteID: " + str(self.selfID))
		self.socketsToPaxos[incomingBallotNum[1]].sendall((outMessage + "%").encode())

		print("---END ACKNOWLEDGE---")
		
		
	def accept(self, incomingBallotNum, incomingAcceptNum, incomingAcceptVal):
		print("---START ACCEPT---")

		### Check to make sure you don't start again ###
		if self.hasMajorityPromises:	
			return

		self.numPromises += 1
		print("Received ack, number of Promises: " + str(self.numPromises))

		self.ackAcceptVals.append(incomingAcceptVal)
		self.incomingAcceptNums.append(incomingAcceptNum[0])

		if self.numPromises >= self.minMajority:
			print("Have majority now. This message should not be printed more than once.")
			print("ackAcceptVals contains: " + str(self.ackAcceptVals))
			print("incomingAcceptNums contains: " + str(self.incomingAcceptNums))
			self.hasMajorityPromises = True
			hasReceivedNoOtherValues = True

			for i in self.ackAcceptVals:
				if i != str(None):
					print("Set hasReceivedNoOtherValues to false.")
					hasReceivedNoOtherValues = False

			if hasReceivedNoOtherValues:
				print("Should go here, chose my own value.")
				self.acceptVal = self.myProposal
			else:
				print("Should not go here, chose someone else's value")
				highestAcceptNumIndex = self.incomingAcceptNums.index(max(self.incomingAcceptNums))
				self.acceptVal = self.ackAcceptVals[highestAcceptNumIndex]

			for sock in self.socketsToPaxos:
				if sock == None:
					continue

				#0			1 				2				3
				#accept 	ballotNum[0]	ballotNum[1]	acceptVal
				outMessage = str(self.logIndex) + " accept " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptVal)
				sock.sendall((outMessage + "%").encode())
				self.isFirstAccept = False

		print("---END ACCEPT---")


	def accepted(self, incomingBallotNum, incomingAcceptVal):
		print("---START ACCEPTED---")

		### If incomingBallotNum does not meet condition, do nothing. ###
		if incomingBallotNum[0] <= self.ballotNum[0]:
			if incomingBallotNum[0] == self.ballotNum[0] and incomingBallotNum[1] < self.ballotNum[1]:
				print("Accept rejected.")
				return

		self.acceptNum = incomingBallotNum
		self.acceptVal = incomingAcceptVal

		if self.isFirstAccept:
			print("First accept received. Should not enter here unless accept value changes.")
			self.isFirstAccept = False

			for sock in self.socketsToPaxos:
				if sock == None:
					continue

				# 0			1				2				3
				# accept	acceptNum[0]	acceptNum[1]	acceptVal
				msg = str(self.logIndex) + " accept " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)
				sock.sendall((msg + "%").encode())
		
		self.numAcceptsReceived += 1
		if self.numAcceptsReceived >= self.minMajority and not self.hasLogged:
			self.hasLogged = True
			# self.logIndex = self.log.getSize()
			# self.log.insertAtIndex(self.logIndex, self.acceptVal)
			return self.acceptVal

			print("Accepted", self.acceptVal)

		print("---END ACCEPTED---")
		return None


	# def stop(self):
	# 	print("Stop Called")
	# 	self.isActive = False


	# def resume(self):
	# 	print("Resume Called")
	# 	self.isActive = True


	# def processMessage(self, inMessage):
	# 	inMessage = inMessage.split(" ")

	# 	if inMessage[0] == "prepare":
	# 		if self.isActive:
	# 			incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
	# 			self.acknowledge(incomingBallotNum)

	# 	elif inMessage[0] == "ack":
	# 		if self.isActive:
	# 			incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
	# 			incomingAcceptNum = (int(inMessage[3]), int(inMessage[4]))
	# 			incomingAcceptVal = inMessage[5]
	# 			self.accept(incomingBallotNum, incomingAcceptNum, incomingAcceptVal)
		
	# 	elif inMessage[0] == "accept":
	# 		if self.isActive:
	# 			incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
	# 			incomingAcceptVal = inMessage[3]
	# 			self.accepted(incomingBallotNum, incomingAcceptVal)

	# 	elif inMessage[0] == "replicate":
	# 		if self.isActive:
	# 			# INMESSAG[1] IS A FILE NAME, NEED TO GET CONTENTS FROM FILE AND PUT INTO PROPOSAL
	# 			# INSTEAD OF PUTTING THE FILE NAME INTO PROPOSAL

	# 			fileName = inMessage[1]
	# 			print("File to be replicated:", fileName)
	# 			self.prepare(fileName)

	# 	elif inMessage[0] == "stop":
	# 		self.sockToClient.sendall(("Paxos got stop%").encode())
	# 		self.stop()

	# 	elif inMessage[0] == "resume":
	# 		self.resume()

	# 	elif inMessage[0] == "total":
	# 		indexes = []
	# 		for i in inMessage[1:]:
	# 				indexes.append(int(i))

	# 		Query.total(indexes)

	# 	elif inMessage[0] == "print":
	# 		Query.printFileNames()

	# 	elif inMessage[0] == "merge":
	# 		#SHOULD CHANGE LOG OBJECT/FILE?
	# 		Query.merge(int(inMessage[1]), int(inMessage[2]))

	# 	elif inMessage[0] == "reset":	#TAKE THIS OUT, NEVER RESET, LIST OF PAXOS
	# 		self.reset()

	# 	else:
	# 		print(" --- ERROR, should never reach here --- ")


	# def receiveMessages(self):
	# 	while True:
	# 		# We know this is receiving correctly - IT'S BEEN TESTED
	# 		for stream in self.incomeStreams:
	# 			stream.settimeout(1)

	# 			try:
	# 				data = stream.recv(1024).decode()

	# 				if len(data) > 0:
	# 					if data[-1] == "%":
	# 						data = data[:-1]

	# 					data = data.split("%")

	# 					print(data)
	# 					for i in data:
	# 						if i == "close":
	# 							return

	# 						self.processMessage(i)

	# 			except socket.timeout:
	# 				continue
	

	# def makeConnections(self):
	# 	self.mySock = Connection.createAcceptSocket(self.ipAddrs[int(self.selfID)], self.ports[int(self.selfID)])
	# 	sockFromCLI = Connection.createAcceptSocket("127.0.0.1", 5005)
	# 	sleep(5)

	# 	self.sockToClient = Connection.createConnectSocket("127.0.0.1", 5001)
	# 	for i in range(1, len(self.ipAddrs)):
	# 		IP = self.ipAddrs[i]
	# 		port = self.ports[i]

	# 		# Other Paxos Sockets
	# 		self.socketsToPaxos.append(Connection.createConnectSocket(IP, port))
		
	# 	# To let other programs create their sockets
	# 	sleep(5)
	# 	for i in range(len(self.ipAddrs) - 1):
	# 		self.incomeStreams.append(Connection.openConnection(self.mySock))
	# 	self.incomeStreams.append(Connection.openConnection(sockFromCLI))
	# 	print("--- ALL CONNECTIONS MADE ---")


	# def closeConnections(self):
	# 	Connection.closeSocket(self.mySock)
	# 	for i in range(1, len(self.socketsToPaxos)):
	# 		Connection.closeSocket(self.socketsToPaxos[i])


	# def config(self):
	# 	f = open(self.configFile, 'r')

	# 	for line in f:
	# 		line = line.split()
	# 		self.ipAddrs.append(line[0])
	# 		self.ports.append(line[1])

	# 	self.minMajority = floor((len(self.ipAddrs) - 1) / 2) + 1


	def buildLogEntryFromFile(self, fileName):
		f = open(fileName, 'r')


		lines = f.readlines()

		logEntry = fileName + "="
		for line in lines:
			line = line.rstrip("\n")
			key = line.split(" ")[0]
			value = line.split(" ")[1]

			logEntry += key + ":" + value + ","

		logEntry = logEntry[0:len(logEntry) - 1]	#Remove the trailing comma

		return logEntry


# def main():

# 	if len(sys.argv) != 3:
# 		print("--- ERROR : Please provide the site ID and config file ---\n")
# 		exit(1)

# 	mainPaxos = Paxos(int(sys.argv[1]), sys.argv[2])
# 	mainPaxos.config()

# 	print(str(mainPaxos.ipAddrs))
# 	print(str(mainPaxos.ports))

# 	mainPaxos.makeConnections()

# 	print(str(mainPaxos.incomeStreams))
# 	print(str(mainPaxos.socketsToPaxos))

# 	mainPaxos.receiveMessages()

# 	mainPaxos.closeConnections()	#MAKE CONDITION TO EXIT INFINITE LOOP

# if __name__ == "__main__":
# 	main()