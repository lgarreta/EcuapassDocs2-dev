#!/usr/bin/env python3

"""
Class for handle binary settings by "empresa": 
	- Codebin pais:user:password
	- Azure connection string
"""
import os, sys, base64, pickle, json

def main ():
	args = sys.argv
	option	 = args [1]
	filename = args [2]

	runningDir = os.getcwd ()
	settings = EcuSettings (runningDir)

	if option == "--print":
		print ("+++ print binary settings")
		settings.printSettings (filename)
	elif option == "--textToBin":
		print ("+++ Text to bin")
		binFilename = filename.rsplit (".", 1)[0] + ".bin"
		settings.textToBin (filename, binFilename)
	elif option == "--binToText":
		print ("+++ Bin to text")
		txtFilename = filename.rsplit (".", 1)[0] + ".txt"
		settings.binToText (filename, txtFilename)
	elif option == "--connString":
		print ("+++ Get conn string")
		value = settings.getParameter ("azrConnString")
		print (value)
	else:
		print (f"Option '{option}' not known")


class EcuSettings:
	def __init__ (self, runningDir):
		self.runningDir = runningDir
		self.settingsFilepath = os.path.join (runningDir, "settings.bin")

	
	#------------------------------------------------------
	#-- Print settins opened from bin file
	#------------------------------------------------------
	def printSettings (self, settingsFilepath):
		self.settingsFilepath = settingsFilepath
		settings = self.readBinSettings ()
		for k,v in settings.items():
			print (f"{k} : {v}")
	#------------------------------------------------------
	#------------------------------------------------------
	def readBinSettings (self):
		binary_filename = self.settingsFilepath
		""" Get JSON from binary file
		"""
		with open (binary_filename, 'rb') as binary_file:
			base64_dict = binary_file.read ()

		decoded_bytes = base64.b64decode (base64_dict)
		json_string   = decoded_bytes.decode ('utf-8')
		dictionary    = json.loads(json_string)

		return dictionary

	#------------------------------------------------------
	#------------------------------------------------------
	def getParameter (self, parameterName):
		""" Get parameter from settings dictionary
		"""
		dictionary = self.readBinSettings ()
		value = dictionary [parameterName]
		return value

	#------------------------------------------------------
	#------------------------------------------------------
	def textToBin (self, text_filename, binary_filename):
		""" Reads a dictionary from a text file and writes it to a binary file.
		"""
		with open(text_filename, 'r') as text_file:
			dictionary = eval (text_file.read())

		# Convert the dictionary to a JSON string
		json_string = json.dumps (dictionary)
		# Encode the JSON string to bytes with UTF-8 encoding
		encoded_bytes = json_string.encode('utf-8')		
		# Serialize the dictionary and encode it in base64
		base64_encoded_dict = base64.b64encode (encoded_bytes)

		with open(binary_filename, 'wb') as binary_file:
			binary_file.write (base64_encoded_dict)

	#------------------------------------------------------
	#------------------------------------------------------
	def binToText (self, binary_filename, text_filename):
		""" Create binary file from JSON file
		"""
		dictionary = self.readBinSettings ()

		# Write to text file
		with open (text_filename, 'w') as text_file:
			json.dump (dictionary, text_file, indent=4)

		return dictionary

#--------------------------------------------------------------------
# Call main 
#--------------------------------------------------------------------
if __name__ == '__main__':
	main ()
