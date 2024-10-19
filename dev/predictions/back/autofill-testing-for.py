#!/usr/bin/env python3

import os, sys
import csv
import pandas as pd
import psycopg2

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza

def main ():
	start_doc	  = "CO7405"

	# Set db vars
	pg       = readCheckDBVars ()
	filename = "data-byza-cartaportes.csv"
#
#	#-- Step 01: Get data
#	getDataFromDB (pg, start_doc, 100, dataFilename)
	
	filename  = renameColumns (filename, "SHORTNAMES")

	filename  = preprocessData (filename)

	filename  = cleanData (filename)

	filename  = renameColumns (filename, "DOCNAMES")

	filename, encoders = encodeData (filename)

	models = trainModels (filename)

	testModels (models, encoders)

#----------------------------------------------------------
#----------------------------------------------------------
def testModels (models, encoders):
	value     = "891401705-8"
	value     = "901473190-9"
	print ("+++ 02:", value)
	enc       = encoders ["02"]
	encValue  = enc.transform ([value])[0]
	inputsDic = {"02":encValue}     

	colnames  = models.keys()
	for name in colnames:
		inputs            = pd.DataFrame ([inputsDic])
		mdl               = models [name]
		prdEncValue       = mdl.predict (inputs)
		enc               = encoders [name]
		prdValue          = enc.inverse_transform (prdEncValue)
		print (f" Column '{name}': '{prdValue}'")

		inputsDic [name]  = prdEncValue
	
#----------------------------------------------------------
#----------------------------------------------------------
def encodeData (dataFilename):
	df = pd.read_csv (dataFilename)

	colnames = df.columns[:4]
	encoders = {}
	for name in colnames:
		encoders [name] = LabelEncoder()

	dfe = pd.DataFrame (columns=colnames)
	for name in colnames:
		dfe [name] = encoders [name].fit_transform (df [name])		

	outFilename  = dataFilename.split (".")[0] + "-ENC.csv"
	dfe.to_csv (outFilename, index=False, header=True)
	return outFilename, encoders

#----------------------------------------------------------
#----------------------------------------------------------
def trainModels (dataFilename):
	df = pd.read_csv (dataFilename)

	colnames = df.columns

	models = {}
	xCols = []
	for i in range (len(colnames)-1):
		xCols.append (colnames [i])
		yCol = colnames [i+1]
		print (f"+++ Creating model y:{yCol} : X:{xCols}")

		X = df [xCols]
		y = df [yCol]
		mdl = RandomForestClassifier ()
		mdl.fit (X, y)
		models [yCol] = mdl
	return models

#----------------------------------------------------------
# Preprocess data by organizing/joining columns
#----------------------------------------------------------
def preprocessData (dataFilename):
	def selectColumns (df):
		cols = map (str, [12,18,23,26,29,30,32,33,35,36,37,38,39,46,49,60,61,62,63,64,65,68,69,79])
		mainCols = []
		for col in cols:
			for colname in df.columns:
				if colname.startswith (col):
					mainCols.append (colname)
		return df.filter (mainCols)

	def joinColumns (df):
		df ["30"] = df ["30"] + "-" +  df ["29"]   # Ciudad-Pais Recepcion
		df ["33"] = df ["33"] + "-" +  df ["32"]   # Ciudad-Pais Embarque
		df ["36"] = df ["36"] + "-" +  df ["35"]   # Ciudad-Pais Entrega
		df ["49"] = df ["49"] + "-" +  df ["48"]   # Ciudad-Pais Mercancia
		df ["63"] = df ["63"] + "-" +  df ["62"]   # Ciudad-Pais Emision
		return df

	df = pd.read_csv (dataFilename)
	df = joinColumns (df)
	df = selectColumns (df)

	outFilename  = dataFilename.split (".")[0] + "-PRP.csv"
	df.to_csv (outFilename, index=False, header=True)
	return (outFilename)

#----------------------------------------------------------
# Clean data colums 
#----------------------------------------------------------
def cleanData (dataFilename):
	# Select main columns
	# Remove columns with low variance (mostly the same values)
	def filterLowVarianceCols (df):
		threshold = 0.80         # Set a threshold for low variance (e.g., 80%)
		low_variance_cols = [col for col in df.columns if df[col].value_counts(normalize=True).max() > threshold]
		single_value_cols = [col for col in df.columns if df[col].nunique() == 1]
		cols_to_drop = list (set(low_variance_cols + single_value_cols))
		return df.drop (cols_to_drop, axis=1)

	# Filter columns
	df          = pd.read_csv (dataFilename)
#	df          = filterMainCols (df)
	df          = filterLowVarianceCols (df)
	outFilename = dataFilename.split (".")[0] + "-CLN.csv"
	df.to_csv (outFilename, index=False, header=True)
	return (outFilename)

#----------------------------------------------------------
#-- Export document DB instances to a table
#----------------------------------------------------------
def getDataFromDB (pg, start_doc, limit, dataFilename):
	try:
		# Connect to the PostgreSQL database using environment variables
		conn = psycopg2.connect (dbname=pg ["db"], host= pg ["host"], 
						   port= pg ["port"], user= pg ["user"], password = pg ["pswd"])
		cursor = conn.cursor()

		# Query the database
		query = """ SELECT * FROM cartaportedoc WHERE numero <= %s
			        ORDER BY numero LIMIT %s; """
		cursor.execute (query, (start_doc, limit))

		# Fetch all results
		records = cursor.fetchall ()
		# Get column names from cursor.description
		column_names = [desc[0] for desc in cursor.description]		
		print (column_names)

		# Write to the CSV file
		with open (dataFilename, 'w', newline='', encoding='utf-8') as csvfile:
			writer = csv.writer (csvfile, quoting=csv.QUOTE_MINIMAL)

			# Write data rows
			HEADERS_FLAG = True
			for record in records:
				formFields     = dict (zip (column_names, record))
				runningDir     = os.getcwd ()
				ecudocFields   = Utils.getEcudocFieldsFromFormFields ("CARTAPORTE", formFields)
				cartaporteInfo = CartaporteByza (None, runningDir, ecudocFields)
				ecuapassFields = cartaporteInfo.extractEcuapassFields ()
				keys           = ecuapassFields.keys ()

				# Write the header row (column names)
				if HEADERS_FLAG:
					writer.writerow (keys)
					HEADERS_FLAG = False

				writer.writerow ([ecuapassFields[key] for key in keys])

		return (dataFilename)

		print(f"Data exported to {dataFilename}")

	except Exception as e:
		Utils.printException()

	finally: # Close the database connection
		if conn:
			cursor.close()
			conn.close()


#----------------------------------------------------------
#-- Rename columns to short names
#----------------------------------------------------------
def renameColumns (dataFilename, type="SHORTNAMES"):
	df = pd.read_csv (dataFilename)

	newColnames = {}
	for i, colname in enumerate (df.columns):
		if type == "SHORTNAMES":
			newColnames [colname] = colname [:2]
			outFilename  = dataFilename.split (".")[0] + "-RNMs.csv"
		else:
			newColnames [colname] = str (i+2).zfill(2)
			outFilename  = dataFilename.split (".")[0] + "-RNMd.csv"

	df = df.rename (columns=newColnames)
#		"12_NroIdRemitente": "12",
#		"18_NroIdDestinatario": "18",
#		"23_NroIdConsignatario":"23",
#		"26_NombreNotificado": "26"})

	df.to_csv (outFilename, index=False, header=True)
	return outFilename

#----------------------------------------------------------
#-- Postgress env vars
#----------------------------------------------------------
def readCheckDBVars ():
	pg = {}
	pg ["user"] = os.environ.get ("PGUSER")
	pg ["pswd"] = os.environ.get ("PGPASSWORD")
	pg ["db"]	= os.environ.get ("PGDATABASE")
	pg ["host"] = os.environ.get ("PGHOST")
	pg ["port"] = os.environ.get ("PGPORT")

	print ("Postgres DB vars:")
	for k,v in pg.items ():
		print (f"\t{k}:{v}")
	print ("")

	#if input ("Desea continuar (yes/no): ")!="yes":
	#	sys.exit (0) 
	return pg

#----------------------------------------------------------
# Example usage
if __name__ == "__main__":
	main ()

