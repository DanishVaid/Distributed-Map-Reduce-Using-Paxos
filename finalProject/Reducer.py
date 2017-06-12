import Connection
from time import sleep
import socket

class Reducer():
	
	def __init__(self):
		self.conjoinedDict = {}

		self.socketToCLI = None
		self.incomeStream = None


	def reduce(self, fileNames):
		### Read contents from input files ###
		for fileName in fileNames:
			f = None
			try:
				f = open(fileName, 'r')

			except FileNotFoundError:
				print("--- File", fileName, "Not Found --- ")
				return

			for line in f:
				line = line.split(" ")
				word = line[0]
				count = int(line[1])

				self.conjoinedDict[word] = self.conjoinedDict.get(word, 0) + count

			f.close()

		### Build name of output file ###
		originalFileName = str(fileNames[0].split("_")[0])
		try:
			outputFileName = (originalFileName.split("."))[0] + "_reduced" + "." + (fileNames[0].split("."))[1]

		except IndexError:
			outputFileName = (originalFileName.split("."))[0] + "_reduced"

		### Print out to the output file ###
		self.writeToFile(outputFileName)
		self.socketToCLI.sendall(("Finished Reducing File - wrote out to: " + outputFileName).encode())
		

	def writeToFile(self, outputFileName):
		f = open(outputFileName, 'w')

		for key, value in self.conjoinedDict.items():
			f.write(str(key) + " " + str(value) + "\n")		# Writes "key value", split by line per entry

		f.close()


	def makeConnections(self):
		incomeSock = Connection.createAcceptSocket("127.0.0.1", 5004)
		sleep(5)
		self.socketToCLI = Connection.createConnectSocket("127.0.0.1", 5001)
		sleep(5)
		self.incomeStream = Connection.openConnection(incomeSock)


	def closeConnections(self):
		Connection.closeSocket(self.socketToCLI)


	def receiveMessages(self):
		print("Reducer is receiving messages.")

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

						fileNames = message.split(" ")
						self.reduce(fileNames)

			except socket.timeout:
				pass



############################ END MAPPER CLASS ##############################

def main():
	reducer = Reducer()
	
	reducer.makeConnections()
	reducer.receiveMessages()
	reducer.closeConnections()


if __name__ == "__main__":
	main()