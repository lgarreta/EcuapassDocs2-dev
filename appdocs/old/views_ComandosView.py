
from django.forms.models import model_to_dict

# For http
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

# For login
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# For CSRF protection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# Own imports
from ecuapassdocs.info.resourceloader import ResourceLoader 
from .models import Cartaporte, Manifiesto, Declaracion
from .models import CartaporteDoc, ManifiestoDoc, DeclaracionDoc
from .pdfcreator import CreadorPDF 

class ComandosView (LoginRequiredMixin, View):

	def __init__(self, docType, parameters_file, background_image, *args, **kwargs):
		super().__init__ (*args, **kwargs)

		self.docType	      = docType
		self.template_name    = "forma_documento.html"
		self.background_image = background_image
		self.parameters_file  = parameters_file
		self.inputParameters  = ResourceLoader.loadJson ("docs", self.parameters_file)

	#-------------------------------------------------------------------
	# Used to receive a filled manifiesto form and create a response
	# Get doc number and create a PDF from document values.
	#-------------------------------------------------------------------
	@method_decorator(csrf_protect)
	def get (self, request, *args, **kwargs):
		print ("+++ GET:ComandosView +++")
		print ("kwargs:", kwargs)
		# Get url parameters
		pk      = kwargs.get ('pk')
		command = kwargs.get ('comando')

		values          = self.getValuesFromDB (pk)
		inputValues     = values ["inputs"]
		fieldValues     = values ["fields"]
		inputParameters = values ["parameters"]

		# Create single PDF for documento 
		if "original" in command or "copia" in command:
			pdf_response = self.createPdfResponseOneDocument (inputValues, command)
			return pdf_response

		# Create single PDF for cartaporte and its manifiestos
		elif "paquete" in command:
			pdf_response = self.createPdfResponseMultiDocument (inputValues)
			return pdf_response

		elif "editar" in command:
			response_data = {'numero': "CLON"}
			if self.docType == "CARTAPORTE":
				return redirect (reverse ("cartaporte-documento", args=(pk,)))
			elif self.docType == "MANIFIESTO":
				return redirect (reverse ("manifiesto-documento", args=(pk,)))

		elif "eliminar" in command:
			response_data = {'numero': "CLON"}
			if self.docType == "CARTAPORTE":
				return redirect (reverse ("cartaporte-delete", args=(pk,)))
			elif self.docType == "MANIFIESTO":
				return redirect (reverse ("manifiesto-delete", args=(pk,)))

		elif "clon" in command:
			# Remove id
			inputParameters ["id"]["value"]     = ""
			inputParameters ["numero"]["value"] = "CLON"
			inputParameters ["txt00"]["value"]  = "CLON"
			# Send input fields parameters (bounds, maxLines, maxChars, ...)
			contextDic = {"document_type"	 : self.docType, 
						  "input_parameters" : inputParameters, 
						  "background_image" : self.background_image,
						  "document_url"     : self.docType.lower(),
						  "template_name"    : self.template_name
						 }
			return render (request, self.template_name, contextDic)


	#----------------------------------------------------------------
	# Return document values into input parameters from DB
	#----------------------------------------------------------------
	def getValuesFromDB (self, docId):
		outInputs, outParameters, outFields = {}, {}, {}

		instanceDoc = None
		if (self.docType == "CARTAPORTE"):
			instanceDoc = CartaporteDoc.objects.get (id=docId)
		elif (self.docType == "MANIFIESTO"):
			instanceDoc = ManifiestoDoc.objects.get (id=docId)
		else:
			raise Exception (f"ERROR: Tipo de documento '{self.docType}' no soportado")

		# Iterating over fields
		outParameters = self.inputParameters
		##print ("+++ outParameters:", outParameters)
		##input("")
		for field in instanceDoc._meta.fields:	# Not include "numero" and "id"
			key             = field.name
			value           = getattr (instanceDoc, key)

			outInputs [key]              = value
			outParameters [key]["value"] = value

			fieldName = outParameters [key]["ecudocsField"]
			if fieldName:
				outFields [fieldName] = {"value": value, "content": value}

		results = {"inputs":outInputs, "fields":outFields, "parameters":outParameters} 
		return results

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def getInputValuesFromDB (self, docId):
		inputValues = {}

		instanceDoc = None
		if (self.docType == "CARTAPORTE"):
			instanceDoc = CartaporteDoc.objects.get (id=docId)
		elif (self.docType == "MANIFIESTO"):
			instanceDoc = ManifiestoDoc.objects.get (id=docId)
		elif (self.docType == "DECLARACION"):
			instanceDoc = DeclaracionDoc.objects.get (id=docId)
		else:
			print (f"Error: Tipo de documento '{self.docType}' no soportado")
			return None

		# Iterating over fields
		for field in instanceDoc._meta.fields:	# Not include "numero" and "id"
			value = getattr (instanceDoc, field.name)
			inputValues [field.name] = value

		return inputValues

	#----------------------------------------------------------------
	#-- Embed fields info (key:value) into PDF doc
	#-- Info is embedded according to Azure format
	#----------------------------------------------------------------
	def getFieldValuesFromInputs (self, inputValues):
		jsonFieldsDic = {}
		# Load parameters from package
		inputParameters = ResourceLoader.loadJson ("docs", self.parameters_file)
		for key, params in inputParameters.items():
			fieldName	 = params ["ecudocsField"]
			if fieldName:
				value		 = inputValues [key]
				jsonFieldsDic [fieldName] = {"value": value, "content": value}


		return jsonFieldsDic

	#-------------------------------------------------------------------
	#-- Create a PDF from document
	#-------------------------------------------------------------------
	def createPdfResponseOneDocument (self, inputValues, button_type):
		pdf_response = None

		print (">>> Creando respuesta PDF...")
		creadorPDF = CreadorPDF ("ONE_PDF")

		outPdfPath, outJsonPath = creadorPDF.createPdfDocument (self.docType, inputValues, button_type)

		# Respond with the output PDF
		with open(outPdfPath, 'rb') as pdf_file:
			pdfContent = pdf_file.read()

		# Prepare and return HTTP response for PDF
		pdf_response = HttpResponse (content_type='application/pdf')
		pdf_response ['Content-Disposition'] = f'inline; filename="{outPdfPath}"'
		pdf_response.write (pdfContent)

		return pdf_response

	#-------------------------------------------------------------------
	# Create PDF for 'Cartaporte' plus its 'Manifiestos'
	#-------------------------------------------------------------------
	def createPdfResponseMultiDocument (self, inputValues):
		creadorPDF = CreadorPDF ("MULTI_PDF")

		# Get inputValues for Cartaporte childs
		docId                 = inputValues ["id"]
		valuesList, typesList = self.getInputValuesForCartaporteManifiestos (docId)
		inputValuesList       = [inputValues] + valuesList
		docTypesList          = [self.docType] + typesList

		# Call PDFCreator 
		outPdfPath = creadorPDF.createMultiPdf (inputValuesList, docTypesList)

		# Respond with the output PDF
		with open(outPdfPath, 'rb') as pdf_file:
			pdfContent = pdf_file.read()

		# Prepare and return HTTP response for PDF
		pdf_response = HttpResponse (content_type='application/pdf')
		pdf_response ['Content-Disposition'] = f'inline; filename="{outPdfPath}"'
		pdf_response.write (pdfContent)

		return pdf_response

	#-------------------------------------------------------------------
	# Get input values for cartaporte's manifistos (childs)
	#-------------------------------------------------------------------
	def getInputValuesForCartaporteManifiestos (self, docId):
		outInputValuesList = []
		outDocTypesList    = []
		try:
			regCartaporte   = Cartaporte.objects.get (id=docId)
			regsManifiestos = Manifiesto.objects.filter (cartaporte=regCartaporte)

			for reg in regsManifiestos:
				docManifiesto  = ManifiestoDoc.objects.get (id=reg.id)
				inputValues = model_to_dict (docManifiesto)
				inputValues ["txt41"] = "COPIA"

				outInputValuesList.append (inputValues)
				outDocTypesList.append ("MANIFIESTO")
		except regCartaporte.DoesNotExist:
			print (f"No existe cartaporte con id '{id}'")

		return outInputValuesList, outDocTypesList

	#-------------------------------------------------------------------
	# Show info from calling connection
	#-------------------------------------------------------------------
	def getRequestInfo (self, request, *args, **kwargs):
		print ("--request:", request)

		trigger_url = request.POST.get('trigger_url')
		print ("--- trigger_url:", trigger_url)

		print ("--args:", args)

		print ("--kwargs:", kwargs)

		pk = kwargs.get ('pk')
		print ("--pk:", pk)


#--------------------------------------------------------------------
# DocServicesCartaporteView class
#--------------------------------------------------------------------
class ComandosCartaporteView (ComandosView):
	docType          = "CARTAPORTE"
	parameters_file  = "cartaporte_input_parameters.json"
	background_image = "appdocs/images/image-cartaporte-vacia-SILOG-BYZA.png"

	def __init__(self, *args, **kwargs):
		super().__init__ (self.docType, self.parameters_file, self.background_image, *args, **kwargs)

class ComandosManifiestoView (ComandosView):
	docType          = "MANIFIESTO"
	parameters_file  = "manifiesto_input_parameters.json"
	background_image = "appdocs/images/image-manifiesto-vacio-NTA-BYZA.png"

	def __init__(self, *args, **kwargs):
		super().__init__ (self.docType, self.parameters_file, self.background_image, *args, **kwargs)

