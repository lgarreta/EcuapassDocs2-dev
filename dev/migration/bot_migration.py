#!/usr/bin/env python3
"""
Bot for migration of CODEBIN documents
"""

import json, time, sys, os, random

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

#----------------------------------------------------------
import django
from django.db import connection

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "app_main.settings") #appdocs_main") #/settings")

APPDOCS_PATH="/home/lg/BIO/iaprojects/ecuapassdocs/EcuapassDocs/EcuapassDocs2-dev/"
sys.path.append (f"{APPDOCS_PATH}")
django.setup ()

from app_cartaporte.models_cpi import Cartaporte, CartaporteDoc
from app_cartaporte.models_cpi import Cartaporte, CartaporteDoc
from app_manifiesto.models_mci import Manifiesto, ManifiestoDoc
from app_declaracion.models_dti import Declaracion, DeclaracionDoc
from app_usuarios.models import UsuarioEcuapass

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.resourceloader import ResourceLoader
#----------------------------------------------------------
from bot_migration_docs import docs

#----------------------------------------------------------
# main
#----------------------------------------------------------
def main ():
	args = sys.argv
	option   = args [1]
	inputDir = args [2]
	try:
		if option == "--save":
			saveDocs (inputDir)
		elif option == "--download":
			downloadDocs (inputDir)
		else:
			print ("Opción desconocida")
	except:
		Utils.printException ()

def saveDocs (inputDir):
		webdriver = BotMigration.getWaitWebdriver (DEBUG=True)
		#bot = BotMigration ("LOGITRANS", "COLOMBIA", "DECLARACION", 0, 0, webdriver)
		bot = BotMigration ("BYZA", "COLOMBIA", "DECLARACION", 0, 0, webdriver)
		bot.saveDocFilesToDB (inputDir)

def downloadDocs (inputDir):
		webdriver = BotMigration.getWaitWebdriver (DEBUG=False)
		#------------------------ SETTINGS --------------------#
		empresa, doctype, prefix, year, pais, code = "LOGITRANS", "CARTAPORTE", "CPI", "2023", "COLOMBIA", "CO"
		#empresa, doctype, prefix, year, pais, code = "BYZA", "CARTAPORTE", "CPI", "2019", "COLOMBIA", "CO"
		#empresa, doctype, prefix, year, pais, code = "BYZA", "MANIFIESTO", "MCI", "2019", "COLOMBIA", "CO"
		INI = docs [f"{empresa}"][f"{year}-{code}-{prefix}"]["ini"]["id"]
		END = docs [f"{empresa}"][f"{year}-{code}-{prefix}"]["end"]["id"]
		bot = BotMigration (f"{empresa}", f"{pais}", f"{doctype}", INI, END, webdriver)
		#------------------------------------------------------#
		bot.enterCodebin ()
		bot.loginCodebin (bot.pais)
		bot.downloadDocuments (inputDir)
		webdriver.close()  # Close the window with the matching title

#--------------------------------------------------------------------
# Class with properties and functios for migration: dowload/save docs
#--------------------------------------------------------------------
class BotMigration:
	def __init__ (self, empresa, pais, docType, initialId, finalId, webdriver):
			self.empresa	= empresa
			self.pais	    = pais
			self.codigoPais = Utils.getCodigoPaisFromPais (pais)
			self.docType	= docType
			self.initialId	= initialId
			self.finalId	= finalId
			self.webdriver	= webdriver
			self.settings	= self.getCodebinSettingsForEmpresa ()
			self.user		= self.settings [pais]["user"]
			self.password	= self.settings [pais]["password"]
			self.docPrefix	= self.settings ["docPrefix"]
			
#			types = {
#				"CARTAPORTE" :{"doc":Cartaporte, "form":CartaporteDoc},
#				"MANIFIESTO" :{"doc":Manifiesto, "form":ManifiestoDoc},
#				"DECLARACION":{"doc":Declaracion, "form":DeclaracionDoc}
#			}
#			self.DOCMODEL  = types[docType] ["doc"]
#			self.FORMMODEL = types[docType] ["form"]

	#-------------------------------------------------------------------
	# Get a list of cartaportes from range of ids
	#-------------------------------------------------------------------
	def downloadDocuments (self, outDir):
		try:
			os.system (f"mkdir {outDir}")
			urlLink = self.settings ["link"]

			failingDocs = []
			successDocs = []
			blankDocs   = []
			# Download from latest id to old id (reverse order)
			for docId in range (self.initialId, self.finalId - 1,  -1):
			#for docId in range (self.initialId, self.finalId+1):
				try:
					docLink = urlLink % docId
					print (f"+++ docId: '{docId}'. docLink: '{docLink}'")
					self.webdriver.get (docLink)
					docForm = self.webdriver.find_element (By.TAG_NAME, "form")
					params, docNumber = self.extractMigrationFieldsFromCodebinForm (docForm)

					migrationFilename = f"{outDir}/{self.docPrefix}-{self.empresa}-{docNumber}-MIGRATIONFIELDS.json"
					print (f"+++ migrationFilename:  '{migrationFilename}'")
					json.dump (params, open (migrationFilename, "w"), indent=4, default=str)
					successDocs.append (f"{docId}\t{docNumber}")

					# Check blank docs
					print (f"+++ docNumber:  '{docNumber}'")
					if docNumber == None or docNumber == "":
						print (f"+++ BLANK ({len(blankDocs)}) : {docId}")
						blankDocs.append (docId)
						if len (blankDocs) > 5:
							break

					# Wait for the download to complete
					time.sleep (random.uniform(2, 4))  # Random delay to simulate human behavior

				except:
					Utils.printException ()
					failingDocs.append (str(docId))
				# Introduce random delay between requests
				#time.sleep (random.uniform(2, 5))

			failingDocsFilename = f"{outDir}/{self.docType}-FAILINGDOCS-{self.initialId}-{self.finalId}.txt"
			print (f"+++ DEBUG: failingDocsFilename '{failingDocsFilename}'")
			with open (failingDocsFilename, "w") as fp:
				for string in failingDocs:
					fp.write (string + "\n")

			successDocsFilename = f"{outDir}/{self.docType}-SUCCESSDOCS-{self.initialId}-{self.finalId}.txt"
			print (f"+++ DEBUG: successDocsFilename '{successDocsFilename}'")
			with open (successDocsFilename, "w") as fp:
				for string in successDocs:
					fp.write (string + "\n")


		except:
			Utils.printException ()

	#-------------------------------------------------------------------
	# Codebin enter session: open URL and click into "Continuar" button
	#-------------------------------------------------------------------
	def enterCodebin (self):
		print ("+++ CODEBIN: ...Ingresando URL ...")
		#self.webdriver.get ("https://www.google.com/")
		self.webdriver.get (self.settings ["urlCodebin"])
		#self.webdriver.get ("https://byza.corebd.net")
		submit_button = self.webdriver.find_element(By.XPATH, "//input[@type='submit']")
		submit_button.click()

		# Open new window with login form, then switch to it
		time.sleep (2)
		winMenu = self.webdriver.window_handles [-1]
		self.webdriver.switch_to.window (winMenu)

	#----------------------------------------------------
	# Create params file: 
	#	{paramsField: {ecudocField, codebinField, value}}
	#   Only works for Cartaporte
	#----------------------------------------------------
	def extractMigrationFieldsFromCodebinForm (self, docForm):
		params	= self.getParamsMigrationFields () 
		for key in params.keys():
			codebinField = params [key]["codebinField"]
			try:
				elem = docForm.find_element (By.NAME, codebinField)
				params [key]["value"] = elem.get_attribute ("value")
			except NoSuchElementException:
				#print (f"...Elemento '{codebinField}'	no existe")
				pass

#		pais, codigo = "NONE", "NO" 
#		textsWithCountry = [params[x]["value"] for x in ["txt02"]]
#		if any (["COLOMBIA" in x.upper() for x in textsWithCountry]):
#			pais, codigo = "COLOMBIA", "CO"
#		elif any (["ECUADOR" in x.upper() for x in textsWithCountry]):
#			pais, codigo = "ECUADOR", "EC"
#		elif any (["PERU" in x.upper() for x in textsWithCountry]):
#			pais, codigo = "PERU", "PE"
			
		codigo = self.codigoPais
		params ["txt0a"]["value"] = codigo     # e.g. CO, EC, PE

		codebinNumber = params ['numero']['value']
		if codebinNumber == "" or codebinNumber is None:
			docNumber = ""
		else:
			docNumber = f"{codigo}{codebinNumber}"

		params ["numero"]["value"] = docNumber
		params ["txt00"]["value"]  = docNumber

		return params, docNumber

	#----------------------------------------------------------------
	#-- Create CODEBIN fields from document fields using input parameters
	#-- Add three new fields: idcpic, cpicfechac, ref
	#----------------------------------------------------------------
	def getParamsMigrationFields (self):
		try:
			inputsParamsFile = Utils.getInputsParametersFile (self.docType)
			inputsParams	 = ResourceLoader.loadJson ("docs", inputsParamsFile)
			fields			 = {}
			for key in inputsParams:
				ecudocsField  = inputsParams [key]["ecudocsField"]
				codebinField = inputsParams [key]["codebinField"]
				fields [key] = {"ecudocsField":ecudocsField, "codebinField":codebinField, "value":""}

			if self.docType == "CARTAPORTE":
				fields ["id"]			  = {"ecudocsField":"id", "codebinField":"idcpic", "value":""}
				fields ["numero"]		  = {"ecudocsField":"numero", "codebinField":"nocpic", "value":""}
				fields ["fecha_creacion"] = {"ecudocsField":"fecha_creacion", "codebinField":"cpicfechac", "value":""}
				fields ["referencia"]	  = {"ecudocsField": "referencia", "codebinField":"ref", "value":""}
			elif self.docType == "MANIFIESTO":
				fields ["id"]			  = {"ecudocsField":"id", "codebinField":"idmci", "value":""}
				fields ["numero"]		  = {"ecudocsField":"numero", "codebinField":"no", "value":""}
				fields ["fecha_creacion"] = {"ecudocsField":"fecha_creacion", "codebinField":"mcifechac", "value":""}
				fields ["referencia"]	  = {"ecudocsField": "referencia", "codebinField":"ref", "value":""}
			elif self.docType == "DECLARACION":
				fields ["id"]			  = {"ecudocsField":"id", "codebinField":"iddtai", "value":""}
				fields ["numero"]		  = {"ecudocsField":"numero", "codebinField":"no", "value":""}
				fields ["fecha_creacion"] = {"ecudocsField":"fecha_creacion", "codebinField":"dtaifechac", "value":""}
				fields ["referencia"]	  = {"ecudocsField": "referencia", "codebinField":"ref", "value":""}

			return fields
		except: 
			raise Exception ("Obteniendo campos de CODEBIN")
			Utils.printException ()

	#------------------------------------------------------
	# Get waitdriver (Open browser)
	#------------------------------------------------------
	@staticmethod
	def getWaitWebdriver (DEBUG=False):
		Utils.printx ("Getting webdriver...")
		if DEBUG:
			BotMigration.webdriver = None

		while not hasattr (BotMigration, "webdriver"):
			Utils.printx ("...Loading webdriver...")
			options = Options()

			#-- For chrome
			#options.add_argument(f"user-agent={user_agent}")
			#service = Service (ChromeDriverManager().install())
			#BotMigration.webdriver = webdriver.Chrome (service=service, options=options)
			#BotMigration.webdriver = webdriver.Chrome ()
			
			#-- For firefox
			#options.add_argument("--headless")
			#GECKOPATH = "/home/lg/.local/bin/geckodriver"
			#GECKOPATH = "./geckodriver"
			#service = Service(executable_path=GECKOPATH)
			#BotMigration.webdriver = webdriver.Firefox (service=service, options=options)
			BotMigration.webdriver = webdriver.Firefox (options=options)

			# Initialize Firefox WebDriver service
			#service = Service(GeckoDriverManager().install())
			#BotMigration.webdriver = webdriver.Firefox(service=service, options=options)
			Utils.printx ("...Webdriver Loaded")


		return BotMigration.webdriver

	#-------------------------------------------------------------------
	# Returns the web driver after login into CODEBIN
	#-------------------------------------------------------------------
	def loginCodebin (self, pais):
		pais = pais.lower ()
		print (f"+++ CODEBIN: ...AutenticAndose con paIs : '{pais}'")
		# Login Form : fill user / password
		loginForm = self.webdriver.find_element (By.TAG_NAME, "form")
		userInput = loginForm.find_element (By.NAME, "user")
		#userInput.send_keys ("GRUPO BYZA")
		userInput.send_keys (self.user)
		pswdInput = loginForm.find_element (By.NAME, "pass")
		#pswdInput.send_keys ("GrupoByza2020*")
		pswdInput.send_keys (self.password)

		# Login Form:  Select pais (Importación or Exportación : Colombia or Ecuador)
		docSelectElement = self.webdriver.find_element (By.XPATH, "//select[@id='tipodoc']")
		docSelect = Select (docSelectElement)
		docSelect.select_by_value (pais)
		submit_button = loginForm.find_element (By.XPATH, "//input[@type='submit']")
		submit_button.click()

		return self.webdriver

	#-------------------------------------------------------------------
	# Return settings for acceding to CODEBIN by "empresa"
	#-------------------------------------------------------------------
	def getCodebinSettingsForEmpresa (self):
		settings = {}
		prefix = None
		if self.empresa == "BYZA":
			prefix = "byza"
			settings ["COLOMBIA"] = {"user":"GRUPO BYZA", "password":"GrupoByza2020*"}
			settings ["ECUADOR"]  = {"user":"GRUPO BYZA", "password":"GrupoByza2020*"}
			settings ["PERU"]	  = {"user":"", "password":"*"}
		elif self.empresa == "NTA":
			prefix = "nta"
			settings ["COLOMBIA"] = {"user":"MARCELA", "password":"NTAIPIALES2023"}
			settings ["ECUADOR"]  = {"user":"KARLA", "password":"NTAIPIALES2023"}
			settings ["PERU"]	  = {"user":"CARLOS", "password":"NTAHUAQUILLAS"}
		elif self.empresa == "LOGITRANS":
			prefix = "logitrans"
			settings ["COLOMBIA"] = {"user":"LUIS FERNANDO", "password":"LuisLogitrans"}
			settings ["ECUADOR"]  = {"user":"PATO", "password":"Patologitrans"}
			settings ["PERU"]	  = {"user":"", "password":""}
		else:
			raise Exception ("Empresa desconocida")
		
		settings ["urlCodebin"] = f"https://{prefix}.corebd.net"
		if self.docType == "CARTAPORTE":
			settings ["link"]	 = f"https://{prefix}.corebd.net/1.cpi/nuevo.cpi.php?modo=3&idunico=%s"
			settings ["menu"]	 = "Carta Porte I"
			settings ["submenu"] = "1.cpi/lista.cpi.php?todos=todos"
			settings ["docPrefix"]	= "CPI"

		elif self.docType == "MANIFIESTO":
			settings ["link"]	 = f"https://{prefix}.corebd.net/2.mci/nuevo.mci.php?modo=3&idunico=%s"
			settings ["menu"]	 = "Manifiesto de Carga"
			settings ["submenu"] = "2.mci/lista.mci.php?todos=todos"
			settings ["docPrefix"]	= "MCI"

		elif self.docType == "DECLARACION":
			settings ["link"]	 = f"https://{prefix}.corebd.net/3.dtai/nuevo.dtai.php?modo=3&idunico=%s"
			settings ["menu"]	 = "Declaración de Transito"
			settings ["submenu"] = "3.dtai/lista.dtai.php?todos=todos"
			settings ["docPrefix"]	= "DTI"
		else:
			print ("Tipo de documento no soportado:", self.docType)
		return settings

	#-------------------------------------------------------------------
	# Save docs files (JSON) in input dir to DB
	#-------------------------------------------------------------------
	def saveDocFilesToDB (self, inputDir):
		migrationFilesList = [f"{inputDir}/{x}" for x in self.getSortedFiles (inputDir)]
		for migrationFilename in migrationFilesList:
			formFields = Utils.getFormFieldsFromMigrationFieldsFile (migrationFilename)
			usuario    = UsuarioEcuapass.objects.get (username=self.user)
			self.saveNewDocToDB (formFields, self.docType, self.pais, usuario)

	#-- Get doc files from dir sorted by number : CO#####, EC#####, PE#####
	def getSortedFiles (self, inputDir):
		filesAll = [x for x in os.listdir (inputDir) if ".json" in x]
		dicFiles = {}
		for file in filesAll:
			docNumber = file.split("-")[2][2:]
			dicFiles [docNumber] = file

		sortedFiles = [x[1] for x in sorted (dicFiles.items())]
		return sortedFiles

	#-------------------------------------------------------------------
	# Save form fields from Ecuapass document to DB
	#-------------------------------------------------------------------
	def saveNewDocToDB (self, formFields, docType, pais, usuario):
		FormModel, DocModel = self.getFormAndDocModels (docType)

		# First: save DocModel to get the id
		docNumber = formFields ["numero"]
		print ("\n\n------------------------------------------")
		print (f"+++ Guardando documento '{docNumber}' nuevo en la BD...")
		print ("------------------------------------------")
		docModel  = DocModel (numero=docNumber, pais=pais, usuario=usuario)
		docModel.save ()
		docNumber = docModel.numero

		# Second: set and save values to each field of FormModel
		formModel = FormModel (id=docModel.id, numero=docModel.numero)
		formFields ["txt00"] = formModel.numero
		#print (f"+++ formFields: ", formFields)
		for key, value in formFields.items():
			#if key not in ["id", "numero", "referencia", "fecha_creacion"]:
			if "txt" in key: 
				print (f"+++ key:value '{key}':'{value}'")
				setattr (formModel, key, value)
		formModel.save ()

		# Update DocModel with FormModel's values
		docFields	= Utils.getAzureValuesFromInputsValues (docType, formFields)
		#print (f"+++ docFields: ", docFields)
		docFields ["referencia"] = formFields ["referencia"]
		#print (f"+++ DEBUG: docFields '{docFields}'")
		docModel.setValues (formModel, docFields, pais,  usuario)
		docModel.save ()

		return docModel.id, docModel.numero, formModel, docModel

	#-------------------------------------------------------------------
	# Return form document class and register class from document type
	#-------------------------------------------------------------------
	def getFormAndDocModels (self, docType):
		FormModel, DocModel = None, None
		if docType.upper() == "CARTAPORTE":
			FormModel, DocModel = CartaporteDoc, Cartaporte
		elif docType.upper() == "MANIFIESTO":
			FormModel, DocModel = ManifiestoDoc, Manifiesto
		elif docType.upper() == "DECLARACION":
			FormModel, DocModel = DeclaracionDoc, Declaracion 
		else:
			print (f"Error: Tipo de documento '{docType}' no soportado")
			sys.exit (0)

		return FormModel, DocModel

#-------------------------------------------------------------------
# Utils for migration
#-------------------------------------------------------------------
#-- Postgress env vars
def checkDBVars ():
	PGUSER     = os.environ.get ("PGUSER")
	PGPASSWORD = os.environ.get ("PGPASSWORD")
	PGDATABASE = os.environ.get ("PGDATABASE")
	PGHOST     = os.environ.get ("PGHOST")
	PGPORT     = os.environ.get ("PGPORT")

	print ("Postgres DB vars:")
	print ("\t",PGUSER)
	print ("\t",PGPASSWORD)
	print ("\t",PGDATABASE)
	print ("\t",PGHOST)
	print ("\t",PGPORT)
	print ("")

	if input ("Desea continuar (yes/no): ")!="yes":
		return True
	return False

#-------------------------------------------------------------------
#--main
#-------------------------------------------------------------------
main ()