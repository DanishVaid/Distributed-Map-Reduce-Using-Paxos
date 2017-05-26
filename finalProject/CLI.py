#!/bin/python3

import Query
import Connection

class CLI(object):
	
	def __init__(self, configFile):
		self.configFile = configFile	#File name of config file for CLI

		self.mapper1Port = None			#Port number to other processes in same node
		self.mapper2Port = None
		self.reducerport = None
		self.paxosPort = None

		self.sockToMapper1 = None		#Sockets to other processes in same node
		self.sockToMapper2 = None
		self.sockToReducer = None
		self.sockToPaxos = None


	def takeCommand(self):
		print("List of data processing commands:")
		print("map\t\t\tfilename")
		print("reduce\t\tfilename1 filename2 ...")
		print("replicate\tfilename")
		print("stop")
		print("resume")
		print("")

		print("List of data query commands:")
		print("total\t\tpos1 pos2 ...")
		print("print")
		print("merge\t\tpos1 pos2 ...")

		while True:
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
				self.sockToPaxos.send(("replicate " + str(args[0])).encode())
			elif command == "stop":			#part1
				self.sockToPaxos.send(("stop").encode())
			elif command == "resume":		#part1
				self.sockToPaxos.send(("resume").encode())
			elif command == "total":		#part1
				Query.total(args[0], args[1])
			elif command == "print":		#part1
				Query.printFileNames()
			elif command == "merge":		#part1
				Query.merge(args[0], args[1])
			else:
				print("Not a recognizable command")

		print("Program exitted.")


	def config(self):
		# f = open(self.configFile, 'r')

		# for line in f:
		# 	#do something

		# #READ FROM CONFIG FILE FOR IP/PORT OF PROCESSES IN NODE

		# #INITIALIZE CONNECTIONS WITH CONNECTION OBJECT

		self.paxosPort = 5005


	def makeConnections(self):
		#SHOULD HAVE OUTGOING CONNECTIONS TO MAP1, MAP2, REDUCE, AND PAXOS
		# self.sockToMapper1 = connection.createConnectSock("127.0.0.1", self.mapper1Port)
		# self.sockToMapper2 = connection.createConnectSock("127.0.0.1", self.mapper2Port)
		# self.sockToReducer = connection.createConnectSock("127.0.0.1", self.reducerport)
		self.sockToPaxos = Connection.createConnectSocket("127.0.0.1", self.paxosPort)


############################ END CLI CLASS ##############################

def main():
	client = CLI("nonexistent.txt")

	client.config()
	client.makeConnections()
	client.takeCommand()

if __name__ == "__main__":
	main()