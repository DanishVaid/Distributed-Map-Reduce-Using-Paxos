
class Log():	# MAY NOT NEED THIS CLASS

	def __init__(self):
		self.fileNames = []		# List of files names
		self.dictionaries = []	# List of dictionaries


	def append(self, fileName, assocDict):
		self.fileNames.append(fileName)
		self.dictionaries.append(assocDict)


	def size(self):
		return len(self.fileNames)
	

	def toString(self):					# FileName1=Key:Val,Key:Val, . . .\n
		finalString = ""				# FileName2=Key:Val,Key:Val, . . . \n ...

		for i in range(len(self.fileNames)):
			finalString += str(self.fileNames[i])
			finalString += "="
			formatBool = True
			for key in self.dictionaries[i]:
				if formatBool:
					formatBool = False
				else:
					finalString += ","
				temp = str(key) + ":" + str(self.dictionaries[i][key])
				finalString += temp
			finalString += "\n"

		return finalString
	

	def buildFromString(self):
		pass


def testing():
	tempObj = Log()
	tempObj.append("file1",{"key1": "value1", "key2": "value2", "randkey":"randval"})
	tempObj.append("file2",{"key3": "value3", "key4": "value4", "randkey":"randval"})
	inStringFormat = tempObj.toString()
	


# Run testing
testing()