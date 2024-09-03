
import json, os, re, sys
from os.path import join

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from django.contrib import messages
from django.forms.models import model_to_dict

# For CSRF protection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# For login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import resolve   # To get calling URLs

# Own imports
from ecuapassdocs.info.ecuapass_utils import Utils 
from ecuapassdocs.info.ecuapass_data import EcuData 
from ecuapassdocs.info.resourceloader import ResourceLoader 

from app_cartaporte.models_cpi import Cartaporte, CartaporteDoc
from app_manifiesto.models_mci import Manifiesto, ManifiestoDoc
from app_declaracion.models_dti import Declaracion, DeclaracionDoc

from app_usuarios.models import UsuarioEcuapass

from .pdfcreator import CreadorPDF 


#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de manifiesto
#--------------------------------------------------------------------
LAST_SAVED_VALUES = None
class EcuapassDocView (LoginRequiredMixin, View):

	def __init__(self, docType, background_image, parameters_file, *args, **kwargs):
		super().__init__ (*args, **kwargs)
		self.cliente          = "BYZA"
		self.pais	            = None				 
		self.docType	        = docType
		self.template_name    = "forma_documento.html"
		self.background_image = background_image
		self.parameters_file  = parameters_file
		self.inputParams      = ResourceLoader.loadJson ("docs", self.parameters_file)
		self.inputValues      = Utils.getInputValuesFromInputParams (self.inputParams)

	#-------------------------------------------------------------------
	# Usado para llenar una forma (manifiesto) vacia
	# Envía los parámetros o restricciones para cada campo en la forma de HTML
	#-------------------------------------------------------------------
	def get (self, request, *args, **kwargs):
		self.initDocumentValues (request)
		print ("\n\n+++ GET : EcuapassDocView +++")
		print ("+++ URL :", request.path_info)
		command = resolve(request.path_info).url_name
		print ("+++ URL name:", command)

		response = self.getResponseForCommand (command, request, *args, **kwargs)
		return response

	#-------------------------------------------------------------------
	# Used to receive a filled manifiesto form and create a response
	# Get doc number and create a PDF from document values.
	#-------------------------------------------------------------------
	@method_decorator(csrf_protect)
	def post (self, request, *args, **kwargs):
		self.initDocumentValues (request)
		print ("\n\n+++ POST : EcuapassDocView +++")
		print ("+++ URL :", request.path_info)
		print ("+++ PAIS :", self.pais)
		print ("+++ USER :", self.usuario)

		self.inputValues = self.getInputValuesFromForm (request)		  # Values without CPI number
		commandButton    = request.POST.get('boton_seleccionado', '').lower()
		docId            = self.inputValues ["id"]

		# Handle commandButton actions from doc menu
		if "guardar" in commandButton:
			docId = self.onSaveCommand (request) 
			return redirect (f"editar/{docId}")
		elif "pdf" in commandButton:
			return self.onPdfCommand (commandButton, request, *args, **kwargs)
		elif "clonar" in commandButton:
			return self.onClonCommand (commandButton, request, *args, **kwargs)
		else:
			text = f"ERROR: Opción '{commandButton}' no existe"
			print (text)
			messages.add_message (request, messages.ERROR, text)
			return render (request, 'messages.html')

	#-------------------------------------------------------------------
	# Get response for document command (save, original, copia, clon, ...)
	#-------------------------------------------------------------------
	def getResponseForCommand (self, command, request, *args, **kwargs):
		response = None
		documentParams = self.getDocumentParams (request, *args, **kwargs)
		pk = documentParams ["pk"]

		# Check if new or existing document
		if pk and "clon" not in command:
			self.inputParams = self.copySavedValuesToInputs (pk)
			self.inputValues = Utils.getInputValuesFromInputParams (self.inputParams)
	
		if "editar" in command or "nuevo" in command:
			return self.onEditCommand (command, request, *args, **kwargs)

		elif "clonar" in command:
			return self.onClonCommand (command, request, *args, **kwargs)
		elif "pdf" in command:
			return self.onPdfCommand (command, request, *args, **kwargs)

		else:
			messages.add_message (request, messages.ERROR, f"ERROR: Opción '{command}' no existe")
			response = render (request, 'messages.html')

		return response

	#-------------------------------------------------------------------
	# Edit existing, new, or clon doc
	#-------------------------------------------------------------------
	def onEditCommand  (self, command, request, *args, **kwargs):
		print ("+++ onEditCommand:", command)
		documentParams = self.getDocumentParams (request, *args, **kwargs)
		pk = documentParams ["pk"]

		# Check if new or existing document
		if pk:
			self.inputParams = self.copySavedValuesToInputs (pk)
			self.inputValues = Utils.getInputValuesFromInputParams (self.inputParams)

		self.initDocumentValues (request)

		# Send input fields parameters (bounds, maxLines, maxChars, ...)
		docUrl = self.docType.lower()
		contextDic = {
			"docType"          : self.docType, 
			"pais"             : documentParams ["pais"],
			"input_parameters" : self.inputParams, 
			"background_image" : self.background_image,
			"document_url"	   : docUrl
		}
		return render (request, self.template_name, contextDic)

	#-------------------------------------------------------------------
	# Updates current document to DB so "redirect" takes it from DB
	#-------------------------------------------------------------------
	def onClonCommand  (self, command, request, *args, **kwargs):
		print ("+++ onClonCommand:", command)
		url = request.path_info

		documentParams = self.getDocumentParams (request, *args, **kwargs)
		pk             = documentParams ["pk"]
		username       = documentParams ["user"] 
		docType        = documentParams ["docType"] 

		if request.POST:
			self.inputValues = self.getInputValuesFromForm (request)
			self.inputParams = Utils.setInputValuesToInputParams (self.inputValues, self.inputParams)
		else:
			self.inputParams = self.copySavedValuesToInputs (pk)
			self.inputValues = Utils.getInputValuesFromInputParams (self.inputParams)

		##self.setInitialValuesToInputs (documentParams)
		#self.initDocumentValues (request)
		docId, docNumber, formModel, docModel = self.saveNewDocToDB (self.inputValues)

		url = f"/{docType.lower()}/editar/{docId}"
		return redirect (url)

	#-------------------------------------------------------------------
	# Save document to DB checking max docs for user
	#-------------------------------------------------------------------
	def onSaveCommand (self, request, *args, **kwargs):
		print ("+++ Save command")
		documentParams    = self.getDocumentParams (request, *args, **kwargs)

		# Check if user has reached his total number of documents
		if self.checkLimiteDocumentos (documentParams ["user"], self.docType):
			messages.add_message (request, messages.ERROR, "Límite alcanzado para crear nuevos documentos.")
			return render (request, 'messages.html')
		else:
			docId, docNumber = self.saveDocumentToDB (self.inputValues, documentParams)
			return docId

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def onPdfCommand (self, pdfType, request, *args, **kwargs):
		print ("+++ onPdfCommand...")
		documentParams    = self.getDocumentParams (request, *args, **kwargs)
		
		self.saveDocumentToDB (self.inputValues, documentParams)

		# Create a single PDF or PDF with child documents (Cartaporte + Manifiestos)
		if "paquete" in pdfType:
			pdfResponse = self.createResponseForMultiDocument (self.inputValues)
		else:
			pdfResponse = self.createPdfResponseOneDocument (self.inputValues, pdfType)
		return pdfResponse

	#-------------------------------------------------------------------
	# Create PDF for 'Cartaporte' plus its 'Manifiestos'
	#-------------------------------------------------------------------
	def createResponseForMultiDocument (self, inputValues):
		creadorPDF = CreadorPDF ("MULTI_PDF")

		# Get inputValues for Cartaporte childs
		id = inputValues ["id"]
		valuesList, typesList = self.getInputValuesForDocumentChilds (self.docType, id)
		inputValuesList		  = [inputValues] + valuesList
		docTypesList		  = [self.docType] + typesList

		# Call PDFCreator 
		outPdfPath = creadorPDF.createMultiPdf (inputValuesList, docTypesList)

		# Respond with the output PDF
		with open(outPdfPath, 'rb') as pdf_file:
			pdfContent = pdf_file.read()

		# Prepare and return HTTP response for PDF
		pdfResponse = HttpResponse (content_type='application/pdf')
		pdfResponse ['Content-Disposition'] = f'inline; filename="{outPdfPath}"'
		pdfResponse.write (pdfContent)

		return pdfResponse

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def getInputValuesForDocumentChilds (self, docType, docId):
		outInputValuesList = []
		outDocTypesList    = []
		try:
			regCartaporte	= Cartaporte.objects.get (id=docId)
			regsManifiestos = Manifiesto.objects.filter (cartaporte=regCartaporte)

			for reg in regsManifiestos:
				docManifiesto  = ManifiestoDoc.objects.get (id=reg.id)
				inputValues = model_to_dict (docManifiesto)
				inputValues ["txt41"] = "COPIA"

				outInputValuesList.append (inputValues)
				outDocTypesList.append ("MANIFIESTO")
		except Exception as ex:
			Utils.printException ()
			#print (f"'No existe {docType}' con id '{id}'")

		return outInputValuesList, outDocTypesList

	#-------------------------------------------------------------------
	#-- Create a PDF from document
	#-------------------------------------------------------------------
	def createPdfResponseOneDocument (self, inputValues, button_type):
		try:
			pdfResponse = None

			print (">>> Creando respuesta PDF...")
			creadorPDF = CreadorPDF ("ONE_PDF")

			outPdfPath, outJsonPath = creadorPDF.createPdfDocument (self.docType, inputValues, button_type)

			# Respond with the output PDF
			with open(outPdfPath, 'rb') as pdf_file:
				pdfContent = pdf_file.read()

			# Prepare and return HTTP response for PDF
			pdfResponse = HttpResponse (content_type='application/pdf')
			pdfResponse ['Content-Disposition'] = f'inline; filename="{outPdfPath}"'
			pdfResponse.write (pdfContent)

			return pdfResponse
		except Exception as ex:
			print ("EXCEPCION: creando PDF de respuesta")
			Utils.printException ()

	#-------------------------------------------------------------------
	# Check if document has changed
	#-------------------------------------------------------------------


	def hasChangedDocument (self, inputValues):
		global LAST_SAVED_VALUES
		if LAST_SAVED_VALUES == None:
			return True

		for k in inputValues.keys ():
			try:
				current, last = inputValues [k], LAST_SAVED_VALUES [k]

				if current != last:
					print (f"+++ Documento ha cambiado en clave '{k}': '{current}', '{last}'")
					return True
			except Exception as ex:
				print (f"EXCEPCION: Clave '{k}' no existe")

		return False
			
	#-------------------------------------------------------------------
	#-- Set constant values for the BYZA cliente
	#-- Overloaded in sublclasses
	#-------------------------------------------------------------------
	def initDocumentValues (self, request):
		print ("+++ DEBUG: initDocumentValues")
		self.pais    = request.session.get ("pais")
		self.usuario = request.user
		codigoPais   = Utils.getCodigoPaisFromPais (self.pais)
		self.inputParams ["txt0a"]["value"] = codigoPais


#	def setInitialValuesToInputs (self, documentParams):
#		global LAST_SAVED_VALUES
#		LAST_SAVED_VALUES = None
#		# Importacion/Exportacion code for BYZA
#		pais       = documentParams ["pais"]
#		codigoPais = Utils.getCodigoPaisFromPais (pais)
#		self.inputParams ["txt0a"]["value"] = codigoPais

	#-------------------------------------------------------------------
	#++ INCOMPLETE: pais?
	#-------------------------------------------------------------------
	def getDocumentParams (self, request, *args, **kwargs):
		documentParams = {}
		documentParams ["docType"]       = self.docType
		documentParams ["pais"]          = request.session.get ("pais")
		documentParams ["user"]          = request.user
		documentParams ["url"]           = resolve (request.path_info).url_name
		documentParams ["pk"]            = kwargs.get ('pk')

		return documentParams


	#-------------------------------------------------------------------
	#-- Return a dic with the texts from the document form (e.g. txt00,)
	#-------------------------------------------------------------------
	def getInputValuesFromForm (self, request):
		inputValues = {}
		requestValues = request.POST 

		for key in requestValues:
			if "boton" in key:
				continue

			inputValues [key] = requestValues [key].replace ("\r\n", "\n")

		return inputValues

	#-------------------------------------------------------------------
	#-- Set saved or default values to inputs
	#-------------------------------------------------------------------
	def copySavedValuesToInputs (self, recordId):
		instanceDoc = None
		if (self.docType.upper() == "CARTAPORTE"):
			instanceDoc = CartaporteDoc.objects.get (id=recordId)
		elif (self.docType.upper() == "MANIFIESTO"):
			instanceDoc = ManifiestoDoc.objects.get (id=recordId)
		elif (self.docType.upper() == "DECLARACION"):
			instanceDoc = DeclaracionDoc.objects.get (id=recordId)
		else:
			print (f"Error: Tipo de documento '{self.docType}' no soportado")
			return None

		# Iterating over fields
		for field in instanceDoc._meta.fields:	# Not include "numero" and "id"
			value = getattr (instanceDoc, field.name)
			self.inputParams [field.name]["value"] = value if value else ""

		return self.inputParams

	#-------------------------------------------------------------------
	#-- Save document to DB
	#-------------------------------------------------------------------
	#-- Save document if form's values have changed
	def updateDocumentToDB (self, sessionInfo, documentParams):
		if self.hasChangedDocumentValues (sessionInfo):
			print ("+++ DEBUG: updateDocumentToDB:hasChangedDocumentValues")
			currentInputValues = sessionInfo.get ("currentInputValues")
			savedtInputValues  = sessionInfo.get ("savedInputValues")
			sessionInfo.set ("savedInputValues", currentInputValues)
			print (sessionInfo)
			self.saveDocumentToDB (currentInputValues, documentParams)
			self.inputValues = currentInputValues

			print ("+++ updateDoc:", sessionInfo)
			return True
		else:
			return False

	#-------------------------------------------------------------------
	# Check if document input values has changed from the saved ones
	#-------------------------------------------------------------------
	def hasChangedDocumentValues (self, sessionInfo):
		print ("+++ DEBUG: hasChangedDocumentValues")
		currentInputValues = sessionInfo.get ("currentInputValues")
		savedInputValues  = sessionInfo.get ("savedInputValues")

		if savedInputValues == None and currentInputValues == None:
			return False
		elif savedInputValues == None:
			return True

		# Check key by key
		for k in currentInputValues.keys ():
			try:
				current, saved = currentInputValues [k], savedInputValues [k]
				if current != saved:
					print (f"+++ Documento ha cambiado en clave '{k}': '{current}', '{last}'")
					print ("+++ DEBUG: hasChangedDocumentValues", len(current), len (last)) 
					print ("+++ DEBUG: hasChangedDocumentValues", type(current), type (last)) 
					return True
			except Exception as ex:
				print (f"EXCEPCION: Clave '{k}' no existe")

		return False

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def saveDocumentToDB (self, inputValues, documentParams):
		# Create formModel and save it to get id
		docNumber	= inputValues ["numero"]
		print ("+++ DEBUG: docNumber:", docNumber)

		if docNumber == "":
			docId, docNumber, formModel, docModel = self.saveNewDocToDB (inputValues)
			inputValues ["id"]     = docId
			inputValues ["numero"] = docNumber
			inputValues ["txt00"]  = docNumber
		else:
			docId, docNumber, formModel, docModel = self.saveExistingDocToDB (inputValues)

		# Save docModel
		docFields	= Utils.getAzureValuesFromInputsValues (self.docType, inputValues)
		docModel.setValues (formModel, docFields, self.pais,  self.usuario)
		docModel.save ()

		return docId, docNumber

	#-- Save new document
	def saveNewDocToDB (self, inputValues):
		print (">>> Guardando documento nuevo en la BD...")
		FormModel, DocModel = self.getFormAndDocClass (self.docType)

		# First: save DocModel
		docModel  = DocModel (pais=self.pais, usuario=self.usuario)
		docModel.save ()
		docNumber = docModel.numero

		# Second, save FormModel
		formModel = FormModel (id=docModel.id, numero=docModel.numero)
		inputValues ["txt00"] = formModel.numero

		# Third, set FormModel values from input form values
		for key, value in inputValues.items():
			if key not in ["id", "numero"]:
				setattr (formModel, key, value)

		# Fourth, save FormModel and update DocModel with FormModel
		formModel.save ()
		docModel.documento = formModel
		docModel.save ()

		# Update user quota
		self.actualizarNroDocumentosCreados (self.usuario, self.docType)

		return docModel.id, docModel.numero, formModel, docModel

#	def old_saveNewDocToDB (self, inputValues, username):
#		print (">>> Guardando documento nuevo en la BD...")
#		FormModel, DocModel = self.getFormAndDocClass (self.docType)
#		paisCode  = inputValues ["txt0a"]		
#
#		formModel = FormModel ()
#		formModel.save ()
#		formModel.numero = self.createDocNumber (formModel.id, paisCode)
#
#		# Set document values from form values
#		for key, value in inputValues.items():
#			if key not in ["id", "numero"]:
#				setattr (formModel, key, value)
#
#		# Replace old by new number
#		formModel.txt00 = formModel.numero
#
#		# Save corresponding doc model 
#		docId, docNumber = formModel.id, formModel.numero
#		docModel = DocModel (id=docId, numero=docNumber, documento=formModel)
#		docModel.save ()
#
#		# Update user quota
#		self.actualizarNroDocumentosCreados (username, self.docType)
#
#		return docId, docNumber, formModel, docModel

	#-- Save existing document
	def saveExistingDocToDB (self, inputValues):
		print (">>> Guardando documento existente en la BD...")
		FormModel, DocModel = self.getFormAndDocClass (self.docType)
		docId	    = inputValues ["id"]
		docNumber = inputValues ["numero"]
		docModel  = get_object_or_404 (FormModel, id=docId)

		# Assign values to docModel from form values
		for key, value in inputValues.items():
			setattr (docModel, key, value)

		#docModel.numero = inputValues ["txt00"]
		docModel.numero = inputValues ["txt00"]
		docModel.save ()
		regModel = get_object_or_404 (DocModel, id=docId)

		return docId, docNumber, docModel, regModel


	#-- Create doc number
	def createDocNumber (self, id, paisCode):
		initRange = EcuData.configuracion ["numero_documento_inicio"]
		docNumber = f"{paisCode}{initRange + id}"
		return docNumber
	#-------------------------------------------------------------------
	# Return form document class and register class from document type
	#-------------------------------------------------------------------
	def getFormAndDocClass (self, docType):
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
	# Handle assigned documents for "externo" user profile
	#-------------------------------------------------------------------
	#-- Return if user has reached his max number of asigned documents
	def checkLimiteDocumentos (self, username, docType):
		user = get_object_or_404 (UsuarioEcuapass, username=username)
		print (f"+++ User: '{username}'. '{docType}'.  Creados: {user.nro_docs_creados}. Asignados: {user.nro_docs_asignados}")
		
		if (user.perfil == "externo" and user.nro_docs_creados	>= user.nro_docs_asignados):
			return True

		return False

	#-- Only for "cartaportes". Retrieve the object from the DB, increment docs, and save
	def actualizarNroDocumentosCreados (self, username, docType):
		if (docType.upper() != "CARTAPORTE"):
			return

		user = get_object_or_404 (UsuarioEcuapass, username=username)
		user.nro_docs_creados += 1	# or any other value you want to increment by
		user.save()		

	#-------------------------------------------------------------------
	#-- Return a new instance for a FormModel 
	#-- Create a formated document number ranging from 2000000 
	#-- Uses "codigo pais" as prefix (for NTA, BYZA)
	#-------------------------------------------------------------------
	def newFormModelInstance (self, FormModel, paisCode):
		print ("+++ Creating FormModel for system id")
		formModel  = FormModel ()
		formModel.save ()
		docNumberInit    = EcuData.configuracion ["numero_documento_inicio"]
		formModel.numero = f"{paisCode}{docNumberInit + formModel.id}"
		print ("+++ FormModel id, number: ", formModel.id, formModel.numero)
		return formModel

