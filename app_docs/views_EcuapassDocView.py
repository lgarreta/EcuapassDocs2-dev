
import json, os, re, sys
from os.path import join

from django.utils.timezone import now
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

from app_cartaporte.models_cpi import Cartaporte, CartaporteForm
from app_manifiesto.models_mci import Manifiesto, ManifiestoForm
from app_declaracion.models_dti import Declaracion, DeclaracionForm
import app_docs.models_Scripts as Scripts

from app_usuarios.models import UsuarioEcuapass

from .pdfcreator import CreadorPDF 


#--------------------------------------------------------------------
#-- Handle URL request for new doc template with iframes
#-- Basically, render the document template to be put in the iframe
#--------------------------------------------------------------------
def docView(request, *args, **kwargs):
	docType = request.path.strip('/').split('/')[0]
	if "pk" in kwargs:
		context = {"requestType":f"{docType}-editar", "pk":kwargs ["pk"]}
	else:
		context = {f"requestType":f"{docType}-nuevo"}

	return render(request, 'documento_main.html', context)

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de manifiesto
#--------------------------------------------------------------------
LAST_SAVED_VALUES = None
class EcuapassDocView (LoginRequiredMixin, View):

	def __init__(self, docType, background_image, parameters_file, *args, **kwargs):
		super().__init__ (*args, **kwargs)
		self.empresa          = "BYZA"
		self.pais	          = None				 
		self.docType	      = docType
		self.template_name    = "documento_forma.html"
		self.background_image = background_image
		self.parameters_file  = parameters_file
		self.inputParams      = ResourceLoader.loadJson ("docs", self.parameters_file)
		self.inputValues      = Utils.getFormFieldsFromInputParams (self.inputParams)
		self.empresaInfo      = EcuData.empresas [self.empresa] 

	#-------------------------------------------------------------------
	# Usado para llenar una forma (manifiesto) vacia
	# Envía los parámetros o restricciones para cada campo en la forma de HTML
	#-------------------------------------------------------------------
	def get (self, request, *args, **kwargs):
		print ("\n\n+++ GET : EcuapassDocView +++")
		self.initDocumentConstants (request)
		command = resolve (request.path_info).url_name
		print ("+++ URLs :", request.path_info, command)

		response = self.getResponseForCommand (command, request, *args, **kwargs)
		return response

	#-------------------------------------------------------------------
	# Used to receive a filled manifiesto form and create a response
	# Get doc number and create a PDF from document values.
	#-------------------------------------------------------------------
	@method_decorator(csrf_protect)
	def post (self, request, *args, **kwargs):
		print ("\n\n+++ POST : EcuapassDocView +++")
		self.initDocumentConstants (request)
		command = resolve (request.path_info).url_name
		print ("+++ URLs :", request.path_info, command)

		self.inputValues = self.getInputValuesFromForm (request)		  # Values without CPI number
		commandButton    = request.POST.get ('boton_seleccionado', '').lower()
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
			self.inputValues = Utils.getFormFieldsFromInputParams (self.inputParams)
	
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
		documentParams = self.getDocumentParams (request, *args, **kwargs)
		pk = documentParams ["pk"]

		# Check if new or existing document
		if pk:
			self.inputParams = self.copySavedValuesToInputs (pk)
		else:
			self.inputParams ["txt0a"]["value"] = Utils.getCodigoPaisFromPais (self.pais)
			
		# Send input fields parameters (bounds, maxLines, maxChars, ...)
		docUrl = self.docType.lower()
		docNumber = self.inputParams ["numero"]["value"]
		docTitle  = Utils.getDocPrefix (self.docType) + " : " + docNumber
		print (f"+++ DEBUG:  '{self.background_image}'")
		contextDic = {
			"docTitle"         : docTitle,
			"docType"          : self.docType, 
			"pais"             : documentParams ["pais"],
			"input_parameters" : self.inputParams, 
			"background_image" : self.background_image,
			"document_url"	   : docUrl,
			"timestamp"        : now().timestamp ()
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
			self.inputValues = Utils.getFormFieldsFromInputParams (self.inputParams)

		docId, docNumber, formModel, docModel = self.saveNewDocToDB (self.inputValues)

		url = f"/{docType.lower()}/editar/{docId}"
		return redirect (url)

	#-------------------------------------------------------------------
	# Save document to DB checking max docs for user
	#-------------------------------------------------------------------
	def onSaveCommand (self, request, *args, **kwargs):
		print ("+++ Guardando documento...")
		documentParams = self.getDocumentParams (request, *args, **kwargs)

		# Check if user has reached his total number of documents
		if self.checkLimiteDocumentos (documentParams ["user"], self.docType):
			messages.add_message (request, messages.ERROR, "Límite alcanzado para crear nuevos documentos.")
			return render (request, 'messages.html')
		else:
			docId, docNumber = self.saveDocumentToDB (self.inputValues)
			return docId

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def onPdfCommand (self, pdfType, request, *args, **kwargs):
		print ("+++ onPdfCommand...")
		documentParams    = self.getDocumentParams (request, *args, **kwargs)
		
		self.saveDocumentToDB (self.inputValues)

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
				docManifiesto  = ManifiestoForm.objects.get (id=reg.id)
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
	#-- Overloaded in sublclasses (Manifiesto)
	#-------------------------------------------------------------------
	def initDocumentConstants (self, request):
		self.pais    = request.session.get ("pais")
		self.usuario = request.user
		print (f"+++ initDocumentConstants:pais '{self.pais}'")
		print (f"+++ initDocumentConstants:usuario '{self.usuario}'")

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
			instanceDoc = CartaporteForm.objects.get (id=recordId)
		elif (self.docType.upper() == "MANIFIESTO"):
			instanceDoc = ManifiestoForm.objects.get (id=recordId)
		elif (self.docType.upper() == "DECLARACION"):
			instanceDoc = DeclaracionForm.objects.get (id=recordId)
		else:
			print (f"Error: Tipo de documento '{self.docType}' no soportado")
			return None

		# Iterating over fields
		for field in instanceDoc._meta.fields:	# Not include "numero" and "id"
			text = getattr (instanceDoc, field.name)
			maxChars = self.inputParams [field.name]["maxChars"]
			#print (f"+++ maxChars: {maxChars}. Field: {field.name}. Field value {self.inputParams [field.name]['value']}")
			newText = Utils.breakLongLinesFromText (text, maxChars)
			self.inputParams [field.name]["value"] = newText if newText else ""

		return self.inputParams

	#-------------------------------------------------------------------
	#-- Save document to DB
	#-------------------------------------------------------------------
	#-- Save document if form's values have changed
	def updateDocumentToDB (self, sessionInfo, documentParams):
		if self.hasChangedDocumentValues (sessionInfo):
			currentInputValues = sessionInfo.get ("currentInputValues")
			savedtInputValues  = sessionInfo.get ("savedInputValues")
			sessionInfo.set ("savedInputValues", currentInputValues)
			print (sessionInfo)
			self.saveDocumentToDB (currentInputValues)
			self.inputValues = currentInputValues

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
	def saveDocumentToDB (self, inputValues):
		# Create formModel and save it to get id
		docNumber	= inputValues ["numero"]

		if docNumber == "":
			#or docNumber == "SUGERIDO":
			docId, docNumber, formModel, docModel = self.saveNewDocToDB (inputValues)
			inputValues ["id"]     = docId
			inputValues ["numero"] = docNumber
			inputValues ["txt00"]  = docNumber
		else:
			docId, docNumber, formModel, docModel = self.saveExistingDocToDB (inputValues)

		# Update docModel with inputValues
		docFields	= Utils.getAzureValuesFromInputsValues (self.docType, inputValues)
		docModel.setValues (formModel, docFields, self.pais,  self.usuario)
		docModel.save ()

		if (self.docType == "CARTAPORTE"):
			self.createUpdateSuggestedManifiesto (docModel)

		return docId, docNumber

	#-- Save new document
	def saveNewDocToDB (self, inputValues):
		print (f">>> Guardando '{self.docType}' nuevo en la BD...")
		FormModel, DocModel = Scripts.getFormAndDocClass (self.docType)

		# First: save DocModel
		#docNumber = docModel.generateDocNumber ()
		docNumber = Scripts.generateDocNumber (DocModel, self.pais)
		docModel  = DocModel (numero=docNumber, pais=self.pais, usuario=self.usuario)
		docModel.save ()

		# Second, save FormModel
		formModel = FormModel (id=docModel.id, numero=docNumber)
		inputValues ["txt00"] = docNumber

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

	#-- Save existing document
	def saveExistingDocToDB (self, inputValues):
		print (f">>> Guardando '{self.docType}' existente en la BD...")
		FormModel, DocModel = Scripts.getFormAndDocClass (self.docType)

		docId	            = inputValues ["id"]
		formModel           = get_object_or_404 (FormModel, id=docId)
		docModel            = get_object_or_404 (DocModel, id=docId)
		docNumber           = inputValues ["numero"]

		if docNumber== "SUGERIDO":
			docNumber = Scripts.generateDocNumber (DocModel, self.pais)
			docModel.numero       = docNumber
			formModel.numero      = docNumber
			inputValues ["txt00"] = docNumber

		# Assign values to formModel from form values
		for key, value in inputValues.items():
			if key not in ["id", "numero"]:
				setattr (formModel, key, value)

		formModel.save ()
		docModel.save ()

		return docId, docNumber, formModel, docModel


	#-- Create doc number
	def createDocNumber (self, id, paisCode):
		initRange = EcuData.configuracion ["numero_documento_inicio"]
		docNumber = f"{paisCode}{initRange + id}"
		return docNumber

	#-------------------------------------------------------------------
	#-- Create or update suggested Manifiesto according to Cartaporte values
	#-------------------------------------------------------------------
	def createUpdateSuggestedManifiesto (self, cartaporteDoc):
		if cartaporteDoc.hasManifiesto ():
			return

		print ("+++ Creando manifiesto sugerido. ")
		cartaporteForm  = cartaporteDoc.documento    # CPI form
		manifiestoInfo  = cartaporteForm.getManifiestoInfo (self.empresa, self.pais)
		inputValues     = ManifiestoForm.getInputValuesFromInfo (manifiestoInfo)
		self.saveSuggestedManifiesto (cartaporteDoc, inputValues)

	#-- Save suggested manifiesto
	#-- TO OPTIMIZE: It is similar to EcuapassDocView::saveNewDocToDB
	def saveSuggestedManifiesto (self, cartaporteDoc, inputValues):
		print ("+++ Guardando manifiesto sugerido en la BD...")
		print ("+++ Pais:", self.pais, ". Usuario:", self.usuario)
		# First: save DocModel
		docModel        = Manifiesto (pais=self.pais, usuario=self.usuario)
		docModel.numero = "SUGERIDO"
		docModel.save ()

		# Second, save FormModel
		formModel = ManifiestoForm (id=docModel.id, numero=docModel.numero)
		inputValues ["txt00"] = formModel.numero

		# Third, set FormModel values from input form values
		for key, value in inputValues.items():
			if key not in ["id", "numero"]:
				setattr (formModel, key, value)

		# Fourth, save FormModel and update DocModel with FormModel
		formModel.save ()
		docModel.documento  = formModel
		docModel.cartaporte = cartaporteDoc
		docModel.save ()
		return docModel

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

