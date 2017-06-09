import sys

from time import sleep
import Connection
import socket

class Mapper(object):

	def __init__(self, ID, port):
		self.ID = ID 				# Used to differentiate between multiple mappers
		self.port = port			# Because we will have more than one

		self.wordCounts = {}		# Dictionary for (word, count) pairing

		self.socketToCLI = None		# Socket to send messages back to the client
		self.incomeStream = None	# Stream to receive from the client


	def map(self, fileName, offset, size):
		print("filename offset size", fileName, offset, size)	# Print input

		currLookedAt = 0	# NOT USED
		### Read contents from input file ###
		with open(fileName, "r") as f:	# Parse file
			lines = f.readlines()

			totalString = ""
			for line in lines:
				totalString = totalString + line + " "

			# DO WE WANT THESE PRINT STATEMENTS?
			print("Intial total string:", totalString)
			print("Size is:", size)
			totalString = totalString[offset:(offset + size + 1)]			# Choose segment of the file
			print("Broken total string:", totalString)

			words = totalString.split()
			for word in words:
				self.wordCounts[word] = self.wordCounts.get(word, 0) + 1 	# Build word counts into dictionary

			print("Dictionary:", self.wordCounts)

		### Build name of output file ###
		try:
			outputFileName = (fileName.split("."))[0] + "_I_" + str(self.ID) + "." + (fileName.split("."))[1]

		except IndexError:
			outputFileName = (fileName.split("."))[0] + "_I_" + str(self.ID)

		### Print out to an output file ###
		self.writeToFile(outputFileName)
		print("Finished Writing to file:", outputFileName)


	def writeToFile(self, outputFileName):
		f = open(outputFileName, 'w')

		for key, value in self.wordCounts.items():
			f.write(str(key) + " " + str(value) + "\n")		# Writes "key value", split by line per entry

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
						if message == "close":
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

	mapper = Mapper(args[1], args[2])	# ID, port
	
	mapper.makeConnections()
	mapper.receiveMessages()
	mapper.closeConnections()


if __name__ == "__main__":
	main()