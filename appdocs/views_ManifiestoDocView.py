
import json, os, re, datetime
from os.path import join

from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.urls import resolve   # To get calling URLs
from django.shortcuts import get_object_or_404, render
from django.views import View

# For CSRF protection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.urls import resolve   # To get calling URLs

# Own imports
from ecuapassdocs.info.resourceloader import ResourceLoader 
from .views_EcuapassDocView import EcuapassDocView
from .models import Cartaporte, CartaporteDoc, Manifiesto, Vehiculo, Conductor

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de manifiesto
#--------------------------------------------------------------------
class ManifiestoDocView (EcuapassDocView):
	document_type    = "MANIFIESTO"
	template_name    = "forma_documento.html"
	background_image = "appdocs/images/image-manifiesto-vacio-NTA-BYZA.png"
	parameters_file  = "manifiesto_input_parameters.json"

	def __init__(self, *args, **kwargs):
		# Load parameters from package
		self.inputParameters = ResourceLoader.loadJson ("docs", self.parameters_file)
		super().__init__ (self.document_type, self.template_name, self.background_image, 
		                  self.parameters_file, self.inputParameters, *args, **kwargs)

	#-- Set constant values for the BYZA company
	def setInitialValuesToInputs (self, request):
		super ().setInitialValuesToInputs (request)

		# Permisos values for BYZA 
		self.inputParameters ["txt02"]["value"] = "PO-CO-0033-22"
		self.inputParameters ["txt03"]["value"] = "PO-CO-0033-22"

		# Aduanas cruce/destino
		urlName = resolve(request.path_info).url_name
		aduanaCruce,  aduanaDestino = "", ""
		if "importacion" in urlName:
			aduanaCruce   = "IPIALES-COLOMBIA"
			aduanaDestino = "TULCAN-ECUADOR"
		elif "exportacion" in urlName:
			aduanaCruce   = "TULCAN-ECUADOR"
			aduanaDestino = "IPIALES-COLOMBIA"
		else:
			print (f"Alerta: No se pudo determinar aduana cruce/destino desde el URL: '{urlName}'")
		self.inputParameters ["txt37"]["value"] = aduanaCruce
		self.inputParameters ["txt38"]["value"] = aduanaDestino


