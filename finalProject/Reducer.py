import Connection
from time import sleep
import socket

class Reducer():
	
	def __init__(self, ID, fileNames):
		self.conjoinedDict = {}

		self.socketFromCLI = None
		self.incomeStream = None


	def reduce(self, fileNames):
		for fileName in fileNames:
			f = open(fileName, 'r')

			for line in f:
				line = line.split(" ")
				word = line[0]
				count = line[1]

				self.conjoinedDict[word] = conjoinedDict.get(word, count) + count 	#CHECK SYNTAX
																				#CHECK INSTRUCTIONS
																				#"IF A WORD IS NOT IN THE DICTIONARY, IT IS INSERTED
																				#WITH A COUNT OF 1 IN ITS FIRST OCCURENCE"
																				#HOW COULD THERE BE A FIRST OCCURENCE?

			f.close()

		originalFileName = str(fileNames[0].split("_")[0])
		outputFileName = originalFileName + "_reduced.txt"
		self.writeToFile(outputFileName)
		

	def writeToFile(self, outputFileName):
		f = open(outputFileName, 'w')

		for key, value in conjoinedDict.items():
			f.write(str(key) + " " + str(value) + "\n")

		f.close()


	def makeConnections(self):
		incomeSock = Connection.createAcceptSocket("127.0.0.1", 5003)

		sleep(5)

		self.socketToCLI = Connection.createConnectSocket("127.0.0.1", 5001)

		sleep(5)

		self.incomeStream = Connection.openConnection(incomeSock)


	def closeConnections(self):
		Connection.closeSocket(self.socketFromCLI)


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
					if message == "Close":
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