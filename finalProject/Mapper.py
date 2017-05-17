
class Mapper(object):

	def __init__(self, port, ID, fileName, offset, size):
		self.port = port
		self.ID = ID

		self.fileName = fileName
		self.offset = offset
		self.size = size

		self.wordCounts = {}


	def map(self):
		f = open(self.fileName, 'r')

		for line in f:
			#SHOULD RE-FORMAT?
			words = line.split(" ") #CHECK DELIMITERS

			for word in words:
				self.wordCounts[word] = wordCounts.get(word, 0) + 1

		writeTofile(str(self.fileName) + "_I_" + str(self.ID))	#IS MAP RESPONSIBLE FOR WRITING TO FILE?


	def writeToFile(self, fileName):
		f = open(fileName, 'w')

		for key, value in wordCounts.items():
			f.write(str(key) + " " + str(value) + "\n")

		f.close()