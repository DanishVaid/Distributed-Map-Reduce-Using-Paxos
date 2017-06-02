import sys

import Connection
from time import sleep
import socket

class Mapper(object):

	def __init__(self, ID, port):
		self.ID = ID
		self.port = port

		self.wordCounts = {}

		self.socketToCLI = None
		self.incomeStream = None


	def map(self, fileName, offset, size):
		f = open(fileName, 'r')

		for line in f:
			words = line.split(" ") #CHECK DELIMITERS, RE-FORMAT?

			for word in words:
				self.wordCounts[word] = wordCounts.get(word, 0) + 1

		f.close()

		outputFileName = str(fileName) + "_I_" + str(self.ID) + ".txt"
		self.writeToFile(outputFileName)


	def writeToFile(self, outputFileName):
		f = open(outputFileName, 'w')

		for key, value in self.wordCounts.items():
			f.write(str(key) + " " + str(value) + "\n")

		f.close()


	def makeConnections(self):
		incomeSock = Connection.createAcceptSocket("127.0.0.1", self.port)

		sleep(5)

		self.socketToCLI = Connection.createConnectSocket("127.0.0.1", 5001)

		sleep(5)

		self.incomeStream = Connection.openConnection(incomeSock)

	
	def closeConnections(self):
		Connection.closeSocket(self.socketToCLI)


	def receiveMessages(self):
		print("Mapper is receiving messages.")

		while(True):
			self.incomeStream.settimeout(1)

			try:
				data = self.incomeStream.recv(1024).decode()

				if len(data) > 0:
					if data[-1] == "%":
						data = data[:-1]

					data = data.split("%")
					print(data)

					for message in data:
						if message == "Close":
							return

						fileName = message.split(" ")[0]
						offset = message.split(" ")[1]
						size = message.split(" ")[2]

						self.map(message, offset, size)

			except socket.timeout:
				pass


############################ END MAPPER CLASS ##############################

def main():
	args = sys.argv

	mapper = Mapper(args[1], args[2])	#ID, port
	
	mapper.makeConnections()
	mapper.receiveMessages()
	mapper.closeConnections()


if __name__ == "__main__":
	main()