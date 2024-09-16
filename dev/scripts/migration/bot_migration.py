#!/usr/bin/env python3
"""
Bot for migration of CODEBIN documents
"""

import json, time, sys, os

import django
from django.db import connection

os.environ.setdefault ("DJANGO_SETTINGS_MODULE", "app_main.settings") #appdocs_main") #/settings")

APPDOCS_PATH="/home/lg/BIO/iaprojects/ecuapassdocs/EcuapassDocs/EcuapassDocs2-dev/"
sys.path.append (f"{APPDOCS_PATH}")
django.setup ()

from app_cartaporte.models_cpi import Cartaporte, CartaporteDoc
from app_manifiesto.models_mci import Manifiesto, ManifiestoDoc
from app_declaracion.models_dti import Declaracion, DeclaracionDoc
from app_usuarios.models import UsuarioEcuapass


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.resourceloader import ResourceLoader 

from app_cartaporte.models_cpi import Cartaporte, CartaporteDoc

def main ():
	try:
		webdriver = BotMigration.getWaitWebdriver (DEBUG=True)
		bot = BotMigration ("BYZA", "COLOMBIA", "CARTAPORTE", 7485, 7490, webdriver)
		#bot.getDocuments ()
		bot.saveDocFilesToDB ("inouts")
	finally:
		#webdriver.close()  # Close the window with the matching title
		pass


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
			types = {
				"CARTAPORTE" :{"doc":Cartaporte, "form":CartaporteDoc},
				"MANIFIESTO" :{"doc":Manifiesto, "form":ManifiestoDoc},
				"DECLARACION":{"doc":Declaracion, "form":DeclaracionDoc}
			}
			self.DOCMODEL  = types[docType] ["doc"]
			self.FORMMODEL = types[docType] ["form"]

	#-------------------------------------------------------------------
	# Get a list of cartaportes from range of ids
	#-------------------------------------------------------------------
	def getDocuments (self):
		self.enterCodebin ()
		self.loginCodebin (self.pais)
		urlLink = self.settings ["link"]

		for docId in range (self.initialId, self.finalId):
			docLink = urlLink % docId
			print (f"+++ docLink: '{docLink}'")
			self.webdriver.get (docLink)
			docForm = self.webdriver.find_element (By.TAG_NAME, "form")
			params, docNumber = self.extractMigrationFieldsFromCodebinForm (docForm)

			migrationFilename = f"{self.docPrefix}-{self.empresa}-{docNumber}-MIGRATIONFIELDS.json"
			json.dump (params, open (migrationFilename, "w"), indent=4, default=str)

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
			
		params ["txt0a"]["value"] = self.codigoPais

		docNumber = f"{codigo}{params ['numero']['value']}"
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
			#options.add_argument("--headless")
			BotMigration.IS_OPEN = False
			BotMigration.LAST_PAIS = ""
			BotMigration.DOC_FOUND = False
			BotMigration.webdriver = webdriver.Firefox (options=options)
			#BotMigration.webdriver = webdriver.Firefox ()
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
		else:
			print ("Tipo de documento no soportado:", self.docType)
		return settings

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def saveDocFilesToDB (self, inputDir):
		migrationFilesList = [f"{inputDir}/{x}" for x in os.listdir (inputDir) if ".json" in x]
		for migrationFilename in migrationFilesList:
			formFields = Utils.getFormFieldsFromMigrationFieldsFile (migrationFilename)
			usuario    = UsuarioEcuapass.objects.get (username=self.user)
			self.saveNewDocToDB (formFields, self.docType, self.pais, usuario)

	#-------------------------------------------------------------------
	# Save form fields from Ecuapass document to DB
	#-------------------------------------------------------------------
	def saveNewDocToDB (self, formFields, docType, pais, usuario):
		print (">>> Guardando documento nuevo en la BD...")
		FormModel, DocModel = self.getFormAndDocModels (docType)

		# First: save DocModel to get the id
		docNumber = formFields ["numero"]
		docModel  = DocModel (numero=docNumber, pais=pais, usuario=usuario)
		docModel.save ()
		docNumber = docModel.numero

		# Second: set and save values to each field of FormModel
		formModel = FormModel (id=docModel.id, numero=docModel.numero)
		formFields ["txt00"] = formModel.numero
		for key, value in formFields.items():
			#if key not in ["id", "numero", "referencia", "fecha_creacion"]:
			if "txt" in key: 
				setattr (formModel, key, value)
		formModel.save ()

		# Update DocModel with FormModel's values
		docFields	= Utils.getAzureValuesFromInputsValues (docType, formFields)
		docFields ["referencia"] = formFields ["referencia"]
		print (f"+++ DEBUG: docFields '{docFields}'")
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
#-------------------------------------------------------------------
main ()
