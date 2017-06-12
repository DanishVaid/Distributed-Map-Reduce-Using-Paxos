#!/bin/python3

import sys
import Query
import Connection
import socket
from time import sleep
import threading

class CLI(object):
	
	def __init__(self, configFile):
		self.configFile = configFile	# File name of config file for CLI

		self.mapper1Port = None			# Port number to other processes in same node
		self.mapper2Port = None
		self.reducerPort = None
		self.paxosPort = None

		self.sockToMapper1 = None		# Sockets to other processes in same node
		self.sockToMapper2 = None
		self.sockToReducer = None
		self.sockToPaxos = None

		self.incomingStream = []		# Stream to receive incoming messages


	def takeCommand(self):
		sleep(2)						# For initial start up messages from other processes
		print("")

		print("List of data processing commands:")
		print("map\t\tfilename")
		print("reduce\t\tfilename1 filename2 ...")
		print("replicate\tfilename")
		print("stop")
		print("resume")
		print("status")

		print("")

		print("List of data query commands:")
		print("total\t\tpos1 pos2 ...")
		print("print")
		print("merge\t\tpos1 pos2 ...")

		print("")

		while True:
			consoleInput = input("Command (enter 'exit' to quit):")
			consoleInput = consoleInput.split()

			command = consoleInput[0]
			args = consoleInput[1:]

			### Ends the program. Send exit to all processes. ###
			if command == "exit":
				self.sockToMapper1.sendall(("close%").encode())
				self.sockToMapper2.sendall(("close%").encode())
				self.sockToReducer.sendall(("close%").encode())
				self.sockToPaxos.sendall(("close%").encode())
				break

			### Initiate map command to both Mapper processes ###
			elif command == "map":
				try:
					print("Mapping File")
					filenameToMapper = args[0]
					offset1, size1, offset2, size2 = getMappingProperties(filenameToMapper)
					msgToMapper1 = filenameToMapper + " " + str(offset1) + " " + str(size1) + "%"
					msgToMapper2 = filenameToMapper + " " + str(offset2) + " " + str(size2) + "%"
					self.sockToMapper1.sendall((msgToMapper1).encode())
					self.sockToMapper2.sendall((msgToMapper2).encode())
					print("Mapping message sent")
					
				except FileNotFoundError:
					print(" --- File", filenameToMapper, "Not Found --- ")

			### Initiate reduce command to Reducer process ###
			elif command == "reduce":
				msgToReducer = ""
				for fileName in args:
					msgToReducer = msgToReducer + fileName + " "
				msgToReducer = msgToReducer[:-1]
				msgToReducer += "%"
				print(msgToReducer)	# DO WE WANT THIS PRINT STATEMENT?
				self.sockToReducer.sendall((msgToReducer).encode())

			### Initiate Paxos to replicate a log ###
			elif command == "replicate":	#part1
				self.sockToPaxos.sendall(("x replicate " + str(args[0]) + "%" ).encode())

			### Stops the Paxos, imitates an offline node. ###
			elif command == "stop":			#part1
				print("Sending Stop")
				print(self.sockToPaxos)
				self.sockToPaxos.sendall(("x stop%").encode())

			### Resumes the Paxos, imitates a node coming online. ###
			elif command == "resume":		#part1
				print("Sending Resume")
				self.sockToPaxos.sendall(("x resume%").encode())

			### Look for received messages ###
			elif command == "status":
				print("Checking messages/status")
				continue

			### Prints total amount of words ###
			elif command == "total":		#part1
				indexes = ""
				for i in args:
					indexes += (" " + str(i))
				
				self.sockToPaxos.sendall(("x total" + indexes + "%").encode())

			### Prints all file names ###
			elif command == "print":		#part1
				self.sockToPaxos.sendall(("x print%").encode())

			### Merges two log entries and prints ###
			elif command == "merge":		#part1
				self.sockToPaxos.sendall(("x merge " + str(args[0]) + " " + str(args[1]) + "%").encode())

			else:
				print("Not a recognizable command")

		print("Program exitted.")


	def config(self):
		f = open(self.configFile, 'r')
		lines = f.readlines()
		
		self.mapper1Port = lines[0]
		self.mapper2Port = lines[1]
		self.reducerPort = lines[2]
		self.paxosPort = lines[3]


	def makeConnections(self):
		incomingSock = Connection.createAcceptSocket("127.0.0.1", 5001)

		sleep(5)

		self.sockToMapper1 = Connection.createConnectSocket("127.0.0.1", self.mapper1Port)
		self.sockToMapper2 = Connection.createConnectSocket("127.0.0.1", self.mapper2Port)
		self.sockToReducer = Connection.createConnectSocket("127.0.0.1", self.reducerPort)
		self.sockToPaxos = Connection.createConnectSocket("127.0.0.1", self.paxosPort)

		sleep(5)

		for i in range(4):
			self.incomingStream.append(Connection.openConnection(incomingSock))


	def closeConnections(self):
		Connection.closeSocket(self.sockToPaxos)
		Connection.closeSocket(self.sockToMapper1)
		Connection.closeSocket(self.sockToMapper2)
		Connection.closeSocket(self.sockToReducer)


def receiveMessages(cliUnit):
	while True:
		for i in range(len(cliUnit.incomingStream)):
			stream = cliUnit.incomingStream[i]
			stream.settimeout(1)

			try:
				data = stream.recv(1024).decode()

				if len(data) > 0:
					if data[-1] == "%":
						data = data[:-1]

					data = data.split("%")
					print("Stream", i, "Message Recevied:", data)

			except socket.timeout:
				continue



############################ END CLI CLASS ##############################

def getMappingProperties(filenameToMapper):
	offset1 = 0
	offset2 = 0
	size1 = 0
	size2 = 0

	with open(filenameToMapper, "r") as f:
		lines = f.readlines()

		totalFile = ""
		numChars = 0
		for line in lines:
			numChars += len(line)
			numChars += 1
			totalFile = totalFile + line + " "
		
		size1 = int(numChars / 2)
		while True:
			if totalFile[size1] != " ":
				size1 += 1
			else:
				break
		
		size2 = numChars - size1
		offset2 = size1

		print("numChars is:", numChars)

		return offset1, size1, offset2, size2
		

def main():
	if(len(sys.argv) != 2):
		print("--- ERROR: Please pass in config file ---")
		exit(1)

	client = CLI(sys.argv[1])
	client.config()

	client.makeConnections()

	# Listening Thread
	listen_thread = threading.Thread(target=receiveMessages, args=(client,))
	listen_thread.daemon = True
	listen_thread.start()

	client.takeCommand()

	# Join Thread
	listen_thread.join()

	client.closeConnections()

if __name__ == "__main__":
	main()
