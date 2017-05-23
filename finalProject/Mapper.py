
class Mapper(object):

	def __init__(self, ID, port, fileName, offset, size):
		self.ID = ID
		self.port = port

		self.fileName = fileName
		self.offset = offset
		self.size = size

		self.wordCounts = {}
		self.outputFileName = str(self.fileName) + "_I_" + str(self.ID) + ".txt"


	def map(self):
		f = open(self.fileName, 'r')

		for line in f:
			words = line.split(" ") #CHECK DELIMITERS, RE-FORMAT?

			for word in words:
				self.wordCounts[word] = wordCounts.get(word, 0) + 1

		writeTofile()	#IS MAP RESPONSIBLE FOR WRITING TO FILE?


	def writeToFile(self):
		f = open(outputFileName, 'w')

		for key, value in wordCounts.items():
			f.write(str(key) + " " + str(value) + "\n")

		f.close()