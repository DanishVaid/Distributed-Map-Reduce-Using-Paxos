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

		self.isActive = True				# Used for resume/stop message from the CLI
		self.isLeader = False				# CURRENTLY NOT USED

		self.configFile = configFile		# File name to read in configurations
		self.log = Log.Log()				# Log object

		self.minMajority = 0				# Minimum number of votes for quorum

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

		self.ipAddrs = [None]				# Make the first element None. List of IP addresses of all other Paxos nodes
		self.ports = [None]					# Make the first element None. List of port numbers of all other Paxos nodes

		self.mySock = None					# Socket for incoming messages
		self.incomeStreams = []				# Gather all the streams to check for messages
		self.socketsToPaxos = [None]		# Make the first element None. List of sockets of all other Paxos nodes

	def prepare(self):
		# CHECK IF I'M LEADER

		# self.myProposal = self.log.getSize()
		self.ballotNum = (self.ballotNum[0] + 1, self.selfID)
		outMessage = "prepare " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1])

		for sock in self.socketsToPaxos:
			if sock == None:
				continue

			sock.sendall(outMessage.encode())


	def acknowledge(self, incomingBallotNum):
		# incomingBallotNum[0] = Sender's ballot number
		# incomingBallotNum[1] = Sender's ID

		# If incomingBallotNum does not meet condition, do nothing
		# CHECK LOGIC, IF THIS IS A WORKING CHECK STATEMENT
		if incomingBallotNum[0] <= self.ballotNum[0]:
			if incomingBallotNum[0] == self.ballotNum[0] and incomingBallotNum[1] < self.ballotNum[1]:
				return

		self.ballotNum = (incomingBallotNum[0], incomingBallotNum[1])

		# 0		1					2					3				4				5	
		# ack	incBallotNum[0]		incBallotNum[1]		acceptNum[0]	acceptNum[1]	acceptVal
		outMessage = "ack " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)
		self.socketsToPaxos[incomingBallotNum[1]].sendall((outMessage).encode())
		
		
	def accept(self, incomingBallotNum, incomingAcceptNum, incomingAcceptVal):
		if self.hasMajorityPromises:	# Check to make sure you don't start again
			return

		self.numPromises += 1

		self.ackAcceptVals.append(incomingAcceptVal)
		self.incomingAcceptNums.append(incomingAcceptNum[0])

		if self.numPromises >= self.minMajority:
			self.hasMajorityPromises = True
			hasReceivedNoOtherValues = True

			for i in self.ackAcceptVals:
				if i != None:
					hasReceivedNoOtherValues = False

			if hasReceivedNoOtherValues:
				self.acceptVal = self.myProposal
			else:
				highestAcceptNumIndex = self.incomingAcceptNums.index(max(self.incomingAcceptNums))
				self.acceptVal = self.ackAcceptVals[highestAcceptNumIndex]

			for sock in self.socketsToPaxos:
				if sock == None:
					continue

				#0			1 				2				3
				#accept 	ballotNum[0]	ballotNum[1]	acceptVal
				outMessage = ("accept " + str(self.ballotNum[0]) + " " + str(self.ballotNum[1]) + " " + str(self.acceptVal))
				sock.sendall(outMessage.encode())


	def accepted(self, incomingBallotNum, incomingAcceptVal):
		# If incomingBallotNum does not meet condition, do nothing
		# CHECK LOGIC, IF THIS IS A WORKING CHECK STATEMENT
		if incomingBallotNum[0] <= self.ballotNum[0]:
			if incomingBallotNum[0] == self.ballotNum[0] and incomingBallotNum[1] < self.ballotNum[1]:
				return

		self.acceptNum = incomingBallotNum
		self.acceptVal = incomingAcceptVal

		if self.isFirstAccept:
			self.isFirstAccept = False

			for sock in self.socketsToPaxos:
				if sock == None:
					continue

				# 0			1				2				3
				# accept	acceptNum[0]	acceptNum[1]	acceptVal
				msg = "accept " + str(self.acceptNum[0]) + " " + str(self.acceptNum[1]) + " " + str(self.acceptVal)
				sock.sendall((msg).encode())
		
		self.numAcceptsReceived += 1
		if self.numAcceptsReceived >= self.minMajority:
			# PUT IT IN THE LOG
			print("Accepted", self.acceptVal)


	def stop(self):
		print("Stop Called")
		self.isActive = False


	def resume(self):
		print("Resume Called")
		self.isActive = True


	def processMessage(self, inMessage):
		inMessage = inMessage.split(" ")

		if inMessage[0] == "prepare":
			if self.isActive:
				incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
				self.acknowledge(incomingBallotNum)

		elif inMessage[0] == "ack":
			if self.isActive:
				incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
				incomingAcceptNum = (int(inMessage[3]), int(inMessage[4]))
				incomingAcceptVal = inMessage[5]
				self.accept(incomingBallotNum, incomingAcceptNum, incomingAcceptVal)
		
		elif inMessage[0] == "accept":
			if self.isActive:
				incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
				incomingAcceptVal = inMessage[3]
				self.accepted(incomingBallotNum, incomingAcceptVal)

		elif inMessage[0] == "replicate":
			if self.isActive:
				# INMESSAG[1] IS A FILE NAME, NEED TO GET CONTENTS FROM FILE AND PUT INTO PROPOSAL
				# INSTEAD OF PUTTING THE FILE NAME INTO PROPOSAL
				self.myProposal = inMessage[1]
				print("My Proposal:", self.myProposal)
				self.prepare()

		elif inMessage[0] == "stop":
			self.stop()

		elif inMessage[0] == "resume":
			self.resume()

		else:
			print(" --- ERROR, should never reach here --- ")


	def receiveMessages(self):
		# We know this is receiving correctly - IT'S BEEN TESTED
		for stream in self.incomeStreams:
			stream.settimeout(1)
			try:
				data = stream.recv(1024).decode()
				if len(data) > 0:
					print(data)
					self.processMessage(data)

			except socket.timeout:
				continue
	

	def makeConnections(self):
		self.mySock = Connection.createAcceptSocket(self.ipAddrs[int(self.selfID)], self.ports[int(self.selfID)])
		sleep(5)
		for i in range(1, len(self.ipAddrs)):
			IP = self.ipAddrs[i]
			port = self.ports[i]

			# Other Paxos Sockets
			self.socketsToPaxos.append(Connection.createConnectSocket(IP, port))
		
		# To let other programs create their sockets
		sleep(5)
		for i in range(len(self.ipAddrs)):
			self.incomeStreams.append(Connection.openConnection(self.mySock))
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

		self.incomingAcceptNums = []
		self.ackAcceptVals = []

		self.hasMajorityPromises = False
		self.isFirstAccept = True
		

############################ END PAXOS CLASS ##############################

def main():
	# recieve function
	# process on receive

	if len(sys.argv) != 3:
		print("--- ERROR : Please provide the site ID and config file ---\n")
		exit(1)

	mainPaxos = Paxos(int(sys.argv[1]), sys.argv[2])
	mainPaxos.config()

	print(str(mainPaxos.ipAddrs))
	print(str(mainPaxos.ports))

	mainPaxos.makeConnections()

	print(str(mainPaxos.incomeStreams))
	print(str(mainPaxos.socketsToPaxos))

	while True:
		mainPaxos.receiveMessages()
		# sleep(.2)

	mainPaxos.closeConnections()	#MAKE CONDITION TO EXIT INFINITE LOOP

if __name__ == "__main__":
	main()