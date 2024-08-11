
import json, os, re, sys
from os.path import join

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from django.contrib import messages
from django.contrib.messages import add_message

from django.forms.models import model_to_dict

# For CSRF protection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# For login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import resolve   # To get calling URLs

# Own imports
from ecuapassdocs.info.ecuapass_utils import Utils 
#from ecuapassdocs.ecuapassutils.pdfcreator import CreadorPDF 
from .pdfcreator import CreadorPDF 

from .models import Cartaporte, Manifiesto, Declaracion
from .models import CartaporteDoc, ManifiestoDoc, DeclaracionDoc

from appusuarios.models import UsuarioEcuapass
#from .pdfcreator import CreadorPDF

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de manifiesto
#--------------------------------------------------------------------
LAST_SAVED_VALUES = None
class EcuapassDocView (LoginRequiredMixin, View):

	def __init__(self, docType, template_name, background_image, parameters_file, 
				 inputParams, *args, **kwargs):
		super().__init__ (*args, **kwargs)
		self.empresa		  = "BYZA"
		self.procedimiento	  = None				 
		self.document_type	  = docType
		self.template_name	  = template_name
		self.background_image = background_image
		self.parameters_file  = parameters_file
		self.inputParams      = inputParams
		self.inputValues      = Utils.getInputValuesFromInputParams (self.inputParams)

	#-------------------------------------------------------------------
	# Usado para llenar una forma (manifiesto) vacia
	# Envía los parámetros o restricciones para cada campo en la forma de HTML
	#-------------------------------------------------------------------
	def get (self, request, *args, **kwargs):
		print ("\n\n+++ GET : EcuapassDocView +++")
		command = resolve(request.path_info).url_name
		print ("+++ URL :", request.path_info)
		print ("+++ URL name:", command)
		print ("+++ USER:", request.user)
		print ("+++ KWARGS:", kwargs)

		response = self.getResponseForCommand (command, request, *args, **kwargs)
		return response

	#-------------------------------------------------------------------
	# Used to receive a filled manifiesto form and create a response
	# Get doc number and create a PDF from document values.
	#-------------------------------------------------------------------
	@method_decorator(csrf_protect)
	def post (self, request, *args, **kwargs):
		print ("\n\n+++ POST : EcuapassDocView +++")
		urlName = resolve(request.path_info).url_name
		print ("+++ URL :", request.path_info)
		print ("+++ URL name:", urlName)

		# Get values from html form
		self.inputValues = self.getInputValuesFromForm (request)		  # Values without CPI number

		commandButton    = request.POST.get('boton_seleccionado', '').lower()
		print ("+++ Command button:", commandButton)
		docId            = self.inputValues ["id"]

		# Handle commandButton actions from doc menu
		print (f"+++ REDIRECT : {commandButton}")
		if commandButton == "boton_guardar":
			docId = self.onSaveCommand (request) 
			return redirect (f"editar/{docId}")
		elif commandButton == "boton_pdf_original":
			return redirect (f"pdf_original/{docId}")
		elif commandButton == "boton_pdf_copia":
			return redirect (f"pdf_copia/{docId}")
		elif commandButton == "boton_pdf_paquete":
			return redirect (f"pdf_paquete/{docId}")
		elif commandButton == "boton_clonar":
			self.onClonCommand (commandButton, request, *args, **kwargs)
			return redirect (f"clonar/{docId}")
		else:
			print ("ERROR: Boton de comando '{commandButton}' no existe")
			pdfResponse = self.getResponseForCommand (commandButton, request, *args, **kwargs)
			return pdfResponse

	#-------------------------------------------------------------------
	# Get response for document command (save, original, copia, clon, ...)
	#-------------------------------------------------------------------
	def getResponseForCommand (self, command, request, *args, **kwargs):
		response = None
		requestParams = self.getRequestInfo (request, *args, **kwargs)
		pk = requestParams ["pk"]
		# Check if new or existing document
		if pk and "clon" not in command:
			self.inputParams = self.copySavedValuesToInputs (pk)
			self.inputValues = Utils.getInputValuesFromInputParams (self.inputParams)

	
		if "guardar" in command:
			docId, docNumber = self.saveDocumentToDB (self.inputValues, requestParams)
			response = JsonResponse ({"id": docId, 'numero': docNumber}, safe=False)

		elif "editar" in command or "nuevo" in command:
			response = self.onEditCommand (command, request, *args, **kwargs)

		elif "clonar" in command:
			response = self.onClonCommand (command, request, *args, **kwargs)

		elif any (x in command for x in ["original", "copia", "paquete"]):
			response = self.onPdfCommand (command, request, *args, **kwargs)

		else:
			print (">>> Error: No se conoce opción del botón presionado:", command)

		return response

	#-------------------------------------------------------------------
	# Edit existing, new, or clon doc
	#-------------------------------------------------------------------
	def onEditCommand  (self, command, request, *args, **kwargs):
		print ("+++ onEditCommand:", command)
		requestParams = self.getRequestInfo (request, *args, **kwargs)
		pk = requestParams ["pk"]
		print ("+++ pk:", pk)
		# Check if new or existing document
		if pk:
			self.inputParams = self.copySavedValuesToInputs (pk)
			self.inputValues = Utils.getInputValuesFromInputParams (self.inputParams)
	
		self.setInitialValuesToInputs (requestParams)

		# Send input fields parameters (bounds, maxLines, maxChars, ...)
		docUrl = self.document_type.lower()
		contextDic = {
			"document_type"    : self.document_type, 
			"procedimiento"    : requestParams ["procedimiento"],
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
		print ("+++ URL: ", url)

		requestParams = self.getRequestInfo (request, *args, **kwargs)
		pk = requestParams ["pk"]
		print ("+++ pk:", pk)

		if request.POST:
			print ("+++ Clon from current doc (POST)")
			self.inputValues = self.getInputValuesFromForm (request)
			self.inputParams = Utils.setInputValuesToInputParams (self.inputValues, self.inputParams)
			if self.hasChangedDocument (self.inputValues):
				self.saveDocumentToDB (self.inputValues, requestParams)
		else:
			print ("+++ Clon from DB doc (GET)")
			self.inputParams = self.copySavedValuesToInputs (pk)
			self.inputValues = Utils.getInputValuesFromInputParams (self.inputParams)

		self.setInitialValuesToInputs (requestParams)

		self.inputParams ["txt00"]["value"]  = "CLON"
		self.inputParams ["numero"]["value"] = "CLON"

		# Send input fields parameters (bounds, maxLines, maxChars, ...)
		docUrl = self.document_type.lower()
		contextDic = {
			"document_type"    : self.document_type, 
			"procedimiento"    : requestParams ["procedimiento"],
			"input_parameters" : self.inputParams, 
			"background_image" : self.background_image,
			"document_url"	   : docUrl
		}
		return render (request, self.template_name, contextDic)
	#-------------------------------------------------------------------
	# Save document to DB checking max docs for user
	#-------------------------------------------------------------------
	def onSaveCommand (self, request, *args, **kwargs):
		print ("+++ Save command")
		requestParams    = self.getRequestInfo (request, *args, **kwargs)

		# Check if user has reached his total number of documents
		if self.checkLimiteDocumentos (requestParams ["user"], self.document_type):
			add_message (request, messages.ERROR, "Límite alcanzado para crear nuevos documentos.")
			return render (request, 'messages.html')
		else:
			docId, docNumber = self.saveDocumentToDB (self.inputValues, requestParams)
			return docId

	#-------------------------------------------------------------------
	#-------------------------------------------------------------------
	def onPdfCommand (self, pdfType, request, *args, **kwargs):
		print ("+++ PDF command:" '{pdfType}')
		requestParams    = self.getRequestInfo (request, *args, **kwargs)
		self.updateDocumentToDB (self.inputValues, requestParams)
		if self.hasChangedDocument (self.inputValues):
			self.saveDocumentToDB (self.inputValues, requestParams)

		# Create a single PDF or PDF with child documents (Cartaporte + Manifiestos)
		if "paquete" in pdfType:
			pdfResponse = self.createResponseForMultiDocument (self.inputValues)
		else:
			pdfResponse = self.createPdfResponseOneDocument (self.inputValues, pdfType)
		return pdfResponse

	#-------------------------------------------------------------------
	#++ INCOMPLETE: pais?
	#-------------------------------------------------------------------
	def getRequestInfo (self, request, *args, **kwargs):
		requestParams = {}
		#pais  = request.POST ["txt0a"]		# Auto "CO" or "EC"
		pais  = "CO"
		requestParams ["pais"]  = pais
		requestParams ["procedimiento"] = Utils.getProcedimientoFromPais (self.empresa, pais)
		requestParams ["user"] = request.user
		requestParams ["url"]  = resolve (request.path_info).url_name
		requestParams ["pk"]   = kwargs.get ('pk')

		return requestParams

	#-------------------------------------------------------------------
	# Create PDF for 'Cartaporte' plus its 'Manifiestos'
	#-------------------------------------------------------------------
	def createResponseForMultiDocument (self, inputValues):
		creadorPDF = CreadorPDF ("MULTI_PDF")

		# Get inputValues for Cartaporte childs
		id = inputValues ["id"]
		valuesList, typesList = self.getInputValuesForDocumentChilds (self.document_type, id)
		inputValuesList		  = [inputValues] + valuesList
		docTypesList		  = [self.document_type] + typesList

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
		except regCartaporte.DoesNotExist:
			print (f"'No existe {docType}' con id '{id}'")

		return outInputValuesList, outDocTypesList

	#-------------------------------------------------------------------
	#-- Create a PDF from document
	#-------------------------------------------------------------------
	def createPdfResponseOneDocument (self, inputValues, button_type):
		try:
			pdfResponse = None

			print (">>> Creando respuesta PDF...")
			creadorPDF = CreadorPDF ("ONE_PDF")

			outPdfPath, outJsonPath = creadorPDF.createPdfDocument (self.document_type, inputValues, button_type)

			# Respond with the output PDF
			with open(outPdfPath, 'rb') as pdf_file:
				pdfContent = pdf_file.read()

			# Prepare and return HTTP response for PDF
			#pdfResponse = HttpResponse (content_type='application/pdf')
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
	#-- Set constant values for the BYZA empresa
	#-- Overloaded in sublclasses
	#-------------------------------------------------------------------
	def setInitialValuesToInputs (self, requestParams):
		global LAST_SAVED_VALUES
		LAST_SAVED_VALUES = None
		# Importacion/Exportacion code for BYZA
		procedimiento = requestParams ["procedimiento"]
		codigoPais = Utils.getCodigoPaisFromProcedimiento (self.empresa, procedimiento)
		self.inputParams ["txt0a"]["value"] = codigoPais

	#-------------------------------------------------------------------
	#-- Get or set codigo pais: CO : importacion or EC : exportacion 
	#-------------------------------------------------------------------
	def getCodigoPaisFromURL (self, request):
		# Try to get previous
		codigoPais = self.inputParams ["txt0a"]["value"]

		if not codigoPais:
			urlName = resolve(request.path_info).url_name
			if "importacion" in urlName:
				codigoPais = "CO" 
			elif "exportacion" in urlName:
				codigoPais = "EC" 
			else:
				print (f"Alerta: No se pudo determinar código pais desde el URL: '{urlName}'")
				codigoPais = "" 

		return codigoPais
			
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
		if (self.document_type.upper() == "CARTAPORTE"):
			instanceDoc = CartaporteDoc.objects.get (id=recordId)
		elif (self.document_type.upper() == "MANIFIESTO"):
			instanceDoc = ManifiestoDoc.objects.get (id=recordId)
		else:
			print (f"Error: Tipo de documento '{self.document_type}' no soportado")
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
	def updateDocumentToDB (self, inputValues, requestParams):
		if self.hasChangedDocument (inputValues):
			self.saveDocumentToDB (inputValues, requestParams)
			self.inputValues  = inputValues 
			return True
		else:
			return False

	def saveDocumentToDB (self, inputValues, requestParams):
		global LAST_SAVED_VALUES
		# Create docModel and save it to get id
		docNumber	  = inputValues ["numero"]
		username	  = requestParams ["user"] 
		procedimiento = requestParams ["procedimiento"]

		if docNumber == "" or docNumber == "CLON":
			docId, docNumber, docModel, regModel = self.saveNewDocToDB (inputValues, username)
		else:
			docId, docNumber, docModel, regModel = self.saveExistingDocToDB (inputValues, username)

		# Save regModel
		docFields	= Utils.getAzureValuesFromInputsValues (self.document_type, inputValues)
		regModel.setValues (docModel, docFields, procedimiento,  username)
		regModel.save ()

		LAST_SAVED_VALUES = inputValues

		return docId, docNumber

	#-- Save new document
	def saveNewDocToDB (self, inputValues, username):
		print (">>> Guardando documento nuevo en la BD...")
		DocModel, RegModel = self.getDocumentAndRegisterClass (self.document_type)
		docModel = self.createValidDocModel (inputValues, DocModel)
		if not docModel:
			return None, None

		# Set document values from form values
		for key, value in inputValues.items():
			if key not in ["id", "numero"]:
				setattr(docModel, key, value)

		docModel.txt00 = docModel.numero
		docModel.save ()

		# Update user quota
		self.actualizarNroDocumentosCreados (username, self.document_type)

		# Save initial document register
		docId, docNumber = docModel.id, docModel.numero
		regModel = RegModel (id=docId, numero=docNumber, documento=docModel)

		return docId, docNumber, docModel, regModel
	

	#-- Save existing document
	def saveExistingDocToDB (self, inputValues, username):
		print (">>> Guardando documento existente en la BD...")
		DocModel, RegModel = self.getDocumentAndRegisterClass (self.document_type)
		docId	  = inputValues ["id"]
		docNumber = inputValues ["numero"]
		docModel  = get_object_or_404 (DocModel, id=docId)

		# Assign values to docModel from form values
		for key, value in inputValues.items():
			setattr(docModel, key, value)

		docModel.numero = inputValues ["txt00"]
		docModel.save ()
		regModel = get_object_or_404 (RegModel, id=docId)

		return docId, docNumber, docModel, regModel

	#-------------------------------------------------------------------
	# Return form document class and register class from document type
	#-------------------------------------------------------------------
	def getDocumentAndRegisterClass (self, document_type):
		DocModel, RegModel = None, None
		if document_type.upper() == "CARTAPORTE":
			DocModel, RegModel = CartaporteDoc, Cartaporte
		elif document_type.upper() == "MANIFIESTO":
			DocModel, RegModel = ManifiestoDoc, Manifiesto
		elif document_type.upper() == "DECLARACION":
			DocModel, RegModel = DeclaracionDoc, Declaracion 
		else:
			print (f"Error: Tipo de documento '{document_type}' no soportado")
			sys.exit (0)

		return DocModel, RegModel

	#-------------------------------------------------------------------
	# Handle assigned documents for "externo" user profile
	#-------------------------------------------------------------------
	#-- Return if user has reached his max number of asigned documents
	def checkLimiteDocumentos (self, username, document_type):
		user = get_object_or_404 (UsuarioEcuapass, username=username)
		print (f"+++ User: '{username}'. '{document_type}'.  Creados: {user.nro_docs_creados}. Asignados: {user.nro_docs_asignados}")
		
		if (user.perfil == "externo" and user.nro_docs_creados	>= user.nro_docs_asignados):
			return True

		return False

	#-- Only for "cartaportes". Retrieve the object from the DB, increment docs, and save
	def actualizarNroDocumentosCreados (self, username, document_type):
		if (document_type.upper() != "CARTAPORTE"):
			return

		user = get_object_or_404 (UsuarioEcuapass, username=username)
		user.nro_docs_creados += 1	# or any other value you want to increment by
		user.save()		

	#-------------------------------------------------------------------
	#-- Return a new instance for a DocModel checking if the id is free
	#-- Create a formated document number ranging from 2000000 
	#-- Uses "codigo pais" as prefix (for NTA, BYZA)
	#-------------------------------------------------------------------
	def createValidDocModel (self, inputValues, DocModel):
		docModel  = None
		docNumber = inputValues ["txt00"]

		# If number asigned by user
		if docNumber and docNumber != "CLON":
			print ("+++ Creating DocModel for number assigned by user")
			if DocModel.objects.filter (numero=docNumber).first():
				print (f"ERROR: Ya existe número de documento '{docNumber}'")
				return None
			else:
				docModel = DocModel ()
				docModel.numero = docNumber
				docModel.txt00  = docNumber
		else: # Then system id, but if it is free. Not assigned for another doc
			print ("+++ Creating DocModel by system id")
			codigoPais = inputValues ["txt0a"]
			while True:
				docModel  = DocModel ()
				docModel.save ()
				docNumber = f"{codigoPais}{2000000 + docModel.id}"
				if DocModel.objects.filter (numero=docNumber).first():
					docModel.delete () # if number exists then delete
				else:
					docModel.numero = docNumber
					docModel.txt00  = docNumber
					break
			print ("+++ DocModel number: ", docModel.numero)
		
		return docModel

	def getValidDocumentNumber (self, inputValues, DocModel, id, numero):
		outDocNumber = None
		
		if numero:			 # Assigned by user
			outDocNumber = numero
		else:				 # Assigned by system
			codigoPais = inputValues ["txt0a"]
			while True:
				outDocNumber = f"{codigoPais}{2000000 + id}"
				if DocModel.objects.filter (numero=outDocNumber).first():
					lastDoc = DocModel.objects.get (id=id)
					lastDoc.delete()


		# Check if exists a previous register with that number
		doc = DocModel.objects.filter (numero=outDocNumber).first()
		if doc: 
			outDocNumber = None

		return outDocNumber

