#!/bin/python3

import Paxos
import Query
import Log
import Connection

import sys
import queue

import socket
from time import sleep

from math import floor

class PRM(object):

	def __init__(self, siteID, configFile):
		self.siteID = siteID				# Index of IP/port pair in config file
		self.configFile = configFile		# File name to read in configurations

		self.paxosRounds = [None]			# List of Paxos for multi-Paxos algorithm
		self.msgQueue = queue.Queue()
		self.log = Log.Log()				# Log object

		self.minMajority = 0				# Minimum number of votes for quorum
		self.isActive = True				# Imitates process failure

		self.ipAddrs = [None]				# Make the first element None. List of IP addresses of all other Paxos nodes
		self.ports = [None]					# Make the first element None. List of port numbers of all other Paxos nodes

		self.mySock = None					# Socket for incoming messages
		self.incomeStreams = []				# Gather all the streams to check for messages
		self.socketsToPaxos = [None]		# Make the first element None. List of sockets of all other Paxos nodes
		self.sockToClient = None

		self.isProposing = False


	def stop(self):
		print("Stop Called")	
		self.isActive = False


	def resume(self):
		print("Resume Called")
		self.isActive = True

		for i in range(len(self.socketsToPaxos)):
			sock = self.socketsToPaxos[i]
			if sock == None or i == self.siteID:
				continue
			
			outMsg = "x ping " + str(self.siteID) + "%"
			sock.sendall(outMsg.encode())
		
		sleep(4)

		highestPRM = None
		highestLogSize = self.log.getSize()
		incomingMsg = []
		for stream in self.incomeStreams:
			stream.settimeout(2)

			try:
				data = self.receiveFromSocket(stream)	#stream.recv(1024).decode()

				if len(data) > 0:
					if data[-1] == "%":
						data = data[:-1]
					
					data = data.split("%")

					print("--IN RESUME: Data is", data)

					for command in data:
						command = command.split(" ")

						if command[0] == "currSize":
							if int(command[1]) > highestLogSize:
								highestLogSize = int(command[1])
								highestPRM = int(command[2])
								print("PRM Chose at:", highestPRM)
						else:
							addingMsg = ' '.join(command)
							incomingMsg.append(addingMsg)
				
			except socket.timeout:
				print("No Size Recevied from stream")
				continue

		print("Largest Size for Updating Log (Resume): size, prm", highestLogSize, highestPRM)


		if highestPRM is not None:
			outMsg = "x GiveLog " + str(self.siteID)
			self.socketsToPaxos[highestPRM].sendall(outMsg.encode())
		sleep(4)

		# Get the Log
		self.updateLog(highestPRM)

		print("--IN RESUME: processing other messages:", incomingMsg)
		for i in incomingMsg:
			if i == "close":
				self.closeConnections()
				exit()

			self.processMessage(i)

	def processMessage(self, inMessage):
		inMessage = inMessage.split(" ")


		if self.isActive:
			try:
				paxosIndex = int(inMessage[0])		#log.getSize()
			except:
				paxosIndex = self.log.getSize()
			print("Paxos Index Working At:", paxosIndex)

			while paxosIndex >= len(self.paxosRounds):
				newPaxos = Paxos.Paxos(self.siteID, self.socketsToPaxos, self.minMajority, paxosIndex, self.sockToClient)
				self.paxosRounds.append(newPaxos)	# MAY NEED MORE PARAMETERS

		inMessage = inMessage[1:]
		
		if inMessage[0] == "replicate":
			if self.isActive:
				fileName = inMessage[1]
				self.isProposing = True
				self.paxosRounds[paxosIndex].prepare(fileName)

		elif inMessage[0] == "prepare":
			if self.isActive:
				incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
				self.paxosRounds[paxosIndex].acknowledge(incomingBallotNum)

		elif inMessage[0] == "ack":
			if self.isActive:
				incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
				incomingAcceptNum = (int(inMessage[3]), int(inMessage[4]))
				incomingAcceptVal = inMessage[5]
				self.paxosRounds[paxosIndex].accept(incomingBallotNum, incomingAcceptNum, incomingAcceptVal)
		
		elif inMessage[0] == "accept":
			if self.isActive:
				incomingBallotNum = (int(inMessage[1]), int(inMessage[2]))
				incomingAcceptVal = inMessage[3]
				decidedLog = self.paxosRounds[paxosIndex].accepted(incomingBallotNum, incomingAcceptVal)

				if decidedLog is not None:
					self.isProposing = False
					self.log.insertAtIndex(paxosIndex, decidedLog)

		elif inMessage[0] == "PrepareRejected":
			self.paxosRounds[int(inMessage[1])].prepareRejected(inMessage[2])

		elif inMessage[0] == "ping":
			if self.isActive:
				outMsg = "currSize " + str(self.log.getSize()) + " " + str(self.siteID) + "%"
				self.socketsToPaxos[int(inMessage[1])].sendall(outMsg.encode())
				print("Ping response sent")
			# Get from siteID
			# PING IS SENT WHEN SOURCE NEEDS TO UPDATE THEIR LOG
			# SEND OVER RELEVANT (GREATER THAN THEIR INDEX) LOG ENTRIES

		elif inMessage[0] == "GiveLog":
			self.sendLog(int(inMessage[1]))

		elif inMessage[0] == "stop":
			self.sockToClient.sendall(("Paxos got stop%").encode())
			self.stop()

		elif inMessage[0] == "resume":
			self.resume()

		elif inMessage[0] == "total":
			indexes = []
			for i in inMessage[1:]:
				indexes.append(int(i))

			Query.total(indexes)

		elif inMessage[0] == "print":
			Query.printFileNames()

		elif inMessage[0] == "merge":
			Query.merge(int(inMessage[1]), int(inMessage[2]))

		else:
			print(" --- ERROR, should never reach here --- ")


	def receiveMessages(self):
		# NEED TO COMPENSATE FOR WHEN MESSAGES ARE BIGGER THAN 1024
		numOfRounds = 0

		while True:
			for stream in self.incomeStreams:
				stream.settimeout(1)

				if self.isProposing and numOfRounds > 3:
					self.sockToClient.sendall(("Previous Replicate Failed - Try Again%").encode())
					self.isProposing = False
					numOfRounds = 0

				try:
					data = self.receiveFromSocket(stream) #stream.recv(1024).decode()

					if len(data) > 0:
						if data[-1] == "%":
							data = data[:-1]

						data = data.split("%")

						print(data)
						for i in data:
							if i == "close":
								return
							numOfRounds = 0
							self.processMessage(i)

				except socket.timeout:
					continue

			numOfRounds = numOfRounds + 1


	def makeConnections(self):
		self.mySock = Connection.createAcceptSocket(self.ipAddrs[int(self.siteID)], self.ports[int(self.siteID)])
		sockFromCLI = Connection.createAcceptSocket("127.0.0.1", 5005)

		sleep(5)

		self.sockToClient = Connection.createConnectSocket("127.0.0.1", 5001)
		for i in range(1, len(self.ipAddrs)):
			IP = self.ipAddrs[i]
			port = self.ports[i]

			# Other PRM Sockets
			self.socketsToPaxos.append(Connection.createConnectSocket(IP, port))
		
		sleep(5)

		for i in range(len(self.ipAddrs) - 1):
			self.incomeStreams.append(Connection.openConnection(self.mySock))
		self.incomeStreams.append(Connection.openConnection(sockFromCLI))
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

		f.close()

		self.minMajority = floor((len(self.ipAddrs) - 1) / 2) + 1


	def updateLog(self, highestPRM):
		if highestPRM == None:
			print("Log is already up to date")
			return

		for stream in self.incomeStreams:
			stream.settimeout(1)

			try:
				data = self.receiveFromSocket(stream)	#stream.recv(1024).decode()

				print("-- UPDATE LOG: Recv Data", data)
				if len(data) > 0:
					if data[-1] == "%":
						data = data[:-1]
					
					data = data.split("%")

					for command in data:
						command = command.split(" ")
						if command[1] == "LogIs":
							print("Log String is:", command[2])
							self.log = Log.buildLogFromString(command[2])
							print("Log Updated")
							print(self.log.toString())
							return

			except socket.timeout:
				continue

		print("Failed to Update Log")
		# Send error message back to CLI

	
	def sendLog(self, prmInNeed):
		print("Sending Log")
		try:
			outMsg = "x LogIs " + self.log.toString()
			self.socketsToPaxos[prmInNeed].sendall(outMsg.encode())
			print("Log Sent")

		except:
			print("Failed to send log -- ERROR")

	
	def receiveFromSocket(self, stream):
		BUFF_SIZE = 4096		#4KB at a time
		data = ""
		while True:
			sleep(0.25)
			thisPart = stream.recv(BUFF_SIZE).decode()
			data += thisPart
			
			if len(thisPart) < BUFF_SIZE:
				break
		return data



############################ END PRM CLASS ##############################

def main():
	args = sys.argv

	multiPaxos = PRM(int(args[1]), args[2])	# ID, port

	multiPaxos.config()
	
	multiPaxos.makeConnections()
	multiPaxos.receiveMessages()
	multiPaxos.closeConnections()


if __name__ == "__main__":
	main()