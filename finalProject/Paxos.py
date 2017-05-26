#!/bin/python3

import socket
import sys				# For command line arguments
import Connection		# Makes the Sockets
import Log				# Our Log Class
from math import floor
from time import sleep

class Paxos(object):
	
	def __init__(self, selfID, configFile):
		self.selfID = selfID

		self.isActive = True
		self.isLeader = False

		self.configFile = configFile
		self.log = Log.Log()			# Log

		self.ipAddrs = [None]			# Make the first element None
		self.ports = [None]				# Make the first element None

		self.minMajority = 0

		self.ballotNum = (0, 0)			# Tuples storing ballotNum : siteselfID
		self.acceptNum = (0, 0)			# Tuples storing acceptNum : siteselfID
		self.acceptVal = 0

		self.numPromises = 0
		self.numVotes = 0
		self.numAcceptsReceived = 0

		self.incomingBallotNums = []
		self.ackVals = []

		self.hasMajority = False
		self.isFirstAccept = True

		self.mySock = None
		self.incomeStream = None
		self.socketsToPaxos = [None]	# Make the first element None

	def prepare(self):
		# Check if i am leader -- TO DO

		self.myProposal = len(self.log)
		self.ballotNum = (self.ballotNum[0] + 1, self.selfID)
		outMessage = "prepare " + self.ballotNum[0] + " " + self.ballotNum[1]

		#SEND TO ALL OTHER PRMS
		for sock in self.socketsToPaxos:
			if sock == None:
				continue

			sock.sendall(outMessage.encode())


	def acknowledge(self, proposedNum, senderselfID):
		# CHECK IF PROPOSEDNUM > PREVIOUSLY ACCEPTED NUM

		# If equal compare IDs
		if proposedNum == self.ballotNum[0]:
			if senderselfID > self.selfID:
				self.ballotNum = (proposedNum, self.ballotNum[1])
				# 0		1				2			3				4				5	
				# ack	ballotNum		selfID		acceptNum0		acceptID		acceptVal
				outMessage = "ack " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)
				self.socketsToPaxos[senderselfID].sendall((outMessage).encode())
		
		# Else
		elif proposedNum > self.ballotNum[0]:
			self.ballotNum = (proposedNum, self.ballotNum[1])
			self.socketsToPaxos[senderselfID].sendall(("ack " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)).encode())


	def accept(self, incomingAcceptVal, incomingBallotNum):
		if self.hasMajority:			# Check to make sure you don't start again
			return

		self.numPromises += 1

		self.ackVals.append(incomingAcceptVal)
		self.incomingBallotNums.append(incomingBallotNum)

		if self.numPromises >= self.minMajority:
			self.hasMajority = True
			tempCheck = True
			for i in self.ackVals:
				if i != 0:
					tempCheck = False

			if tempCheck:
				self.acceptVal = self.myProposal
			else:
				highestBallotIndex = self.incomingBallotNums.index(max(self.incomingBallotNums))
				self.acceptVal = self.ackVals[highestBallotIndex]

			# SEND TO ALL OTHER PRMS
			for sock in self.socketsToPaxos:
				if sock == None:
					continue

				sock.sendall(("accept " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptVal)).encode())


	def accepted(self, incomingBallotNum, incomingAcceptedValue):	#RENAME VARIABLE
		
		# CHECK IF ACCEPTINGNUM >= PREVIOUS ACCEPTNUM
		checkStatement = (incomingBallotNum[0] > self.ballotNum[0]) or \
				(incomingBallotNum[0] == self.ballotNum[0] and incomingBallotNum[1] > self.ballotNum[1])

		if checkStatement:
			self.acceptNum = incomingBallotNum
			self.acceptVal = incomingAcceptedValue
			if self.isFirstAccept:
				for sock in self.socketsToPaxos:
					if sock == None:
						continue
					# 0			1			2			3
					# accept	accept1		accept2		acceptVal
					msg = "accept " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)
					sock.sendall((msg).encode())
				self.isFirstAccept = False
			
			self.numAcceptsReceived += 1
			if self.numAcceptsReceived >= self.minMajority:
				# put it into the log
				pass

	def stop(self):
		self.isActive = False


	def resume(self):
		self.isActive = True


	def processMessage(self, inMessage):
		#processMessaageprocessMessage MESSAGE
		inMessage = inMessage.split(" ")

		if inMessage[0] == "prepare":
			if self.isActive:
				self.acknowledge(inMessage[1], inMessage[2])

		elif inMessage[0] == "ack":
			if self.isActive:
				self.accept(inMessage[5], inMessage[1])
		
		elif inMessage[0] == "accept":
			if self.isActive:
				pass
				# self.accepted(incomingBallotNum, incomingAcceptedValue)

		elif inMessage[0] == "replicate":
			if self.isActive:
				self.myProposal = inMessage[1]
				self.prepare()

		elif inMessage[0] == "stop":
			self.stop()

		elif inMessage[0] == "resume":
			self.resume()
		#ELIF MORE POSSIBLE CASES
		else:
			print(" --- ERROR, should never reach here --- ")


	def receiveMessages(self):
		try:
			self.incomeStream.settimeout(1)

			data = self.incomeStream.recv(1024)
			if len(data) > 0:
				self.processMessage(data)

		except socket.timeout:
			pass
	

	def makeConnections(self):
		self.mySock = Connection.createAcceptSocket(self.ipAddrs[int(self.selfID)], self.ports[int(self.selfID)])

		for i in range(1, len(self.ipAddrs)):
			IP = self.ipAddrs[i]
			port = self.ports[i]

			# Other Paxos Sockets
			self.socketsToPaxos.append(Connection.createConnectSocket(IP, port))

		self.incomeStream = Connection.openConnection(self.mySock)

		print("--- ALL CONNECTIONS MADE ---")


	def closeConnections(self):
		Connection.closeSocket(self.mySock)
		for i in range(1, len(self.socketsToPaxos)):
			Connection.closeSocket(self.socketsToPaxos[i])


	def config(self):
		f = open(self.configFile, 'r')

		for line in f:
			line = line.split()
			self.ipAddrs.append(line[0])
			self.ports.append(line[1])

		self.minMajority = floor(len(self.ipAddrs) / 2) + 1


	def reset(self):
		self.ballotNum = (0, 0)
		self.acceptNum = (0, 0)
		self.acceptVal = 0

		self.numPromises = 0
		self.numVotes = 0
		self.numAcceptsReceived = 0

		self.incomingBallotNums = []
		self.ackVals = []

		self.hasMajority = False
		self.isFirstAccept = True

############################ END PAXOS CLASS ##############################

def main():
	# recieve function
	# process on receive

	if len(sys.argv) != 3:
		print("--- ERROR : Please provide the site ID and config file ---\n")
		exit(1)

	mainPaxos = Paxos(sys.argv[1], sys.argv[2])
	mainPaxos.config()

	print(str(mainPaxos.ipAddrs))
	print(str(mainPaxos.ports))

	mainPaxos.makeConnections()

	while True:
		mainPaxos.receiveMessages()
		sleep(.2)

	mainPaxos.closeConnections()	#MAKE CONDITION TO EXIT INFINITE LOOP

if __name__ == "__main__":
	main()