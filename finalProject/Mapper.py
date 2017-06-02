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
		print("filename offset size", fileName, offset, size)
		currLookedAt = 0
		with open(fileName, "r") as f:
			# lines = f.readlines()
			# totalString = ""
			# for line in lines:
			# 	if currLookedAt > size:
			# 		break

			# 	currLookedAt += len(line)
			# 	totalString = totalString + line + " "
			
			# print("Initial total string:", totalString)
			# totalString = totalString[:size]
			# print("Broken total string:", totalString)

			lines = f.readlines()
			totalString = ""
			for line in lines:
				totalString = totalString + line + " "
			print("Intial total string:", totalString)
			print("Size is:", size)
			totalString = totalString[offset:(offset + size + 1)]
			print("Broken total string:", totalString)

			words = totalString.split()
			for word in words:
				self.wordCounts[word] = self.wordCounts.get(word, 0) + 1
			print("Dictionary:", self.wordCounts)


		try:
			outputFileName = (fileName.split("."))[0] + "_I_" + str(self.ID) + "." + (fileName.split("."))[1]

		except IndexError:
			outputFileName = (fileName.split("."))[0] + "_I_" + str(self.ID)

		self.writeToFile(outputFileName)
		print("Finished Writing to file:", outputFileName)


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
						offset = int(message.split(" ")[1])
						size = int(message.split(" ")[2])

						self.map(fileName, offset, size)

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