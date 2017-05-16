
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


	def getWordCounts(self):
		return self.wordCounts