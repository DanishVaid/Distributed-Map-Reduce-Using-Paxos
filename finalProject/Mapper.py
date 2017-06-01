import Connection
from time import sleep
import socket

class Mapper(object):

	def __init__(self):
		self.ID = None
		self.port = None

		self.fileName = None
		self.offset = None
		self.size = None

		self.wordCounts = {}
		self.outputFileName = str(self.fileName) + "_I_" + str(self.ID) + ".txt"

		self.socketToCLI = None
		self.incomingStream = None


	def map(self):
		f = open(self.fileName, 'r')

		for line in f:
			words = line.split(" ") #CHECK DELIMITERS, RE-FORMAT?

			for word in words:
				self.wordCounts[word] = wordCounts.get(word, 0) + 1


	def writeToFile(self):
		f = open(outputFileName, 'w')

		for key, value in wordCounts.items():
			f.write(str(key) + " " + str(value) + "\n")

		f.close()


	def makeConnections(self):
		incomingSock = Connection.createAcceptSocket("127.0.0.1", 6001)
		sleep(5)

		self.socketToCLI = Connection.createConnectSocket("127.0.0.1", 5001)
		sleep(5)

		self.incomingStream = Connection.openConnection(incomingSock)

	
	def closeConnections(self):
		Connection.closeSocket(self.socketToCLI)

	def takeCommands(self):
		print("Mapper is taking commands")
		while(True):
			self.incomingStream.settimeout(1)
			try:
				data = self.incomingStream.recv(1024).decode()
				if len(data) > 0:
					if data[-1] == "%":
						data = data[:-1]
					data = data.split("%")
					print(data)
					for i in data:
						if i == "messagesSent":
							self.socketToCLI.sendall(("Message to CLI from Mapper%").encode())

			except socket.timeout:
				pass


############################ END CLI CLASS ##############################
def main():
	
	mapper = Mapper()
	mapper.makeConnections()
	mapper.takeCommands()

	mapper.closeConnections()

if __name__ == "__main__":
	main()