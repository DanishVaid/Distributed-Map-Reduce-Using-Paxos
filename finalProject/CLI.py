#!/bin/python3

import sys
import Query
import Connection
import socket
from time import sleep

class CLI(object):
	
	def __init__(self, configFile):
		self.configFile = configFile	#File name of config file for CLI

		self.mapper1Port = None			#Port number to other processes in same node
		self.mapper2Port = None
		self.reducerPort = None
		self.paxosPort = None

		self.sockToMapper1 = None		#Sockets to other processes in same node
		self.sockToMapper2 = None
		self.sockToReducer = None
		self.sockToPaxos = None
		self.incomingStream = []


	def takeCommand(self):
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
			self.receiveMessages()

			consoleInput = input("Command (enter 'exit' to quit):")
			consoleInput = consoleInput.split(" ")

			command = consoleInput[0]
			args = consoleInput[1:]

			if command == "exit":
				break

			elif command == "map":
				pass				# Not needed for part 1
				#SEND MESSAGE TO BOTH MAPPERS

			elif command == "reduce":
				pass				# Not needed for part 1
				#SEND MESSAGE TO REDUCER

			elif command == "replicate":	#part1
				self.sockToPaxos.sendall(("replicate " + str(args[0]) + "%" ).encode())

			elif command == "stop":			#part1
				print("Sending Stop")
				print(self.sockToPaxos)
				self.sockToPaxos.sendall(("stop%").encode())

			elif command == "resume":		#part1
				print("Sending Resume")
				self.sockToPaxos.sendall(("resume%").encode())

			elif command == "status":
				print("Checking messages/status")
				continue

			elif command == "total":		#part1
				Query.total(args[0])

			elif command == "print":		#part1
				Query.printFileNames()

			elif command == "merge":		#part1
				Query.merge(args[0], args[1])

			elif command == "maptest":
				self.sockToMapper1.sendall(("messagesSent%").encode())

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

		# self.sockToMapper1 = connection.createConnectSock("127.0.0.1", self.mapper1Port)
		# self.sockToMapper2 = connection.createConnectSock("127.0.0.1", self.mapper2Port)
		# self.sockToReducer = connection.createConnectSock("127.0.0.1", self.reducerPort)
		self.sockToPaxos = Connection.createConnectSocket("127.0.0.1", self.paxosPort)

		sleep(5)

		for i in range(1):
			self.incomingStream.append(Connection.openConnection(incomingSock))


	def closeConnections(self):
		# Connection.closeSocket(self.sockToMapper1)
		# Connection.closeSocket(self.sockToMapper2)
		# Connection.closeSocket(self.sockToReducer)
		Connection.closeSocket(self.sockToPaxos)


	def receiveMessages(self):
		numStream = 0
		for stream in self.incomingStream:
			stream.settimeout(1)
			try:
				data = stream.recv(1024).decode()
				if len(data) > 0:
					if data[-1] == "%":
						data = data[:-1]
					data = data.split("%")
					print(data)
			except socket.timeout:
				print("No message received for stream", numStream)
				numStream += 1



############################ END CLI CLASS ##############################

def main():
	if(len(sys.argv) != 2):
		print("--- ERROR: Please pass in config file ---")
		exit(1)

	client = CLI(sys.argv[1])
	client.config()

	client.makeConnections()
	client.takeCommand()
	client.closeConnections()

if __name__ == "__main__":
	main()
