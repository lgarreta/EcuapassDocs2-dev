
import json, os, re

from django.http import JsonResponse
from django.views import View

# For CSRF protection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# Own imports
from ecuapassdocs.info.resourceloader import ResourceLoader 
from .views_EcuapassDocView import EcuapassDocView
from .models import Vehiculo, Conductor

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de declaracion
#--------------------------------------------------------------------
class DeclaracionDocView (EcuapassDocView):
	document_type    = "declaracion"
	template_name    = "forma_documento.html"
	background_image = "appdocs/images/image-declaracion-vacia-NTA.png"
	parameters_file  = "declaracion_input_parameters.json"

	def __init__(self, *args, **kwargs):
		self.inputParameters = ResourceLoader.loadJson ("docs", self.parameters_file)
		super().__init__ (self.document_type, self.template_name, self.background_image, 
		                  self.parameters_file, self.inputParameters, *args, **kwargs)

#--------------------------------------------------------------------
#-- Class for autocomplete options while the user is typing
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# Show options when user types in "input_placaPais"
#--------------------------------------------------------------------
class VehiculoOptionsView (View):
	@method_decorator(csrf_protect)
	def get (self, request, *args, **kwargs):
		query = request.GET.get('query', '')
		options = Vehiculo.objects.filter (placa__icontains=query).values()

		itemOptions = []
		for i, option in enumerate (options):
			itemLine = f"{i}. {option['placa']}"
			itemText = "%s||%s||%s. %s||%s" % (option["marca"], option["anho"], option["placa"], option ["pais"], option ["chasis"])
			newOption = {"itemLine" : itemLine, "itemText" : itemText}
			itemOptions.append (newOption)
		
		return JsonResponse (itemOptions, safe=False)

#--------------------------------------------------------------------
# Show options when user types in "input_placaPais"
#--------------------------------------------------------------------
class ConductorOptionsView (View):
	@method_decorator(csrf_protect)
	def get (self, request, *args, **kwargs):
		query = request.GET.get('query', '')
		options = Conductor.objects.filter (nombre__icontains=query).values()

		itemOptions = []
		for i, option in enumerate (options):
			itemLine = f"{i}. {option['nombre']}"
			itemText = "%s||%s||%s||%s||%s" % (option["nombre"], option["documento"], 
			           option["nacionalidad"], option ["licencia"], option ["fecha_nacimiento"])
			newOption = {"itemLine" : itemLine, "itemText" : itemText}
			itemOptions.append (newOption)
		
		return JsonResponse (itemOptions, safe=False)

