
import re, datetime

# For CSRF protection
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from django.views import View
from django.http import JsonResponse

from ecuapassdocs.info.resourceloader import ResourceLoader 
from ecuapassdocs.info.ecuapass_utils import Utils
from .models import Cartaporte, Vehiculo, Conductor, Empresa

#--------------------------------------------------------------------
# Show all 'cartaportes' from current date (selected in manifiesto)
# Fill from with "mercancia" info (cartaporte, descripcion, ..., totals
# It doesn't totalize peso "bruto", "neto", and "otras"
#--------------------------------------------------------------------
class CartaporteOptionsView (View):
	@method_decorator(csrf_protect)
	def post (self, request, *args, **kwargs):
		itemOptions = []
		try:
			# Get cartaporte docs from query
			query = request.POST.get ('query', '')

			cartaportes  = Cartaporte.getRecentCartaportes ()
			if not cartaportes.exists():
				cartaportes = Cartaporte.objects.filter (numero__startswith=query,
				 									 fecha_emision=current_date)

			docsCartaportes = [model.documento.__dict__ for model in cartaportes]

			for i, doc in enumerate (docsCartaportes):
				itemLine = f"{i}. {doc['numero']}"
				itemText = "%s||%s||%s||%s||%s||%s||%s||%s||%s||%s||%s" % ( 
							doc ['numero'],  # Cartaporte
							doc ["txt12"],   # Descripcion 
							doc ["txt10"],   # Cantidad
							doc ["txt11"],   # Marca
							doc ["txt13_2"], # Peso bruto
							doc ["txt13_1"], # Peso neto
							doc ["txt15"],   # Otras unidades
							re.sub (r'[\r\n]+\s*', '. ', doc ["txt16"]), # INCONTERMS
							doc ["txt13_2"], # Peso bruto total
							doc ["txt13_1"], # Peso neto total
							doc ["txt15"])   # Otras unidades total

				newOption = {"itemLine" : itemLine, "itemText" : itemText}
				itemOptions.append (newOption)
		except:
			Utils.printException (">>> Excepcion obteniendo opciones de cartaportes")
			
		return JsonResponse (itemOptions, safe=False)

#--------------------------------------------------------------------
# Show options when user types in "input_placaPais"
#--------------------------------------------------------------------
class VehiculoOptionsView (View):
	@method_decorator(csrf_protect)
	def post (self, request, *args, **kwargs):
		query = request.POST.get('query', '')
		options = Vehiculo.objects.filter (placa__istartswith=query).values()

		itemOptions = []
		for i, option in enumerate (options):
			itemLine = f"{i}. {option['placa']}"
			itemText = "%s||%s||%s. %s||%s" % (option["marca"], option["anho"], 
			            option["placa"], option ["pais"], option ["chasis"])
			newOption = {"itemLine" : itemLine, "itemText" : itemText}
			itemOptions.append (newOption)
		
		return JsonResponse (itemOptions, safe=False)

#--------------------------------------------------------------------
# Show options when user types in "input_placaPais"
#--------------------------------------------------------------------
class ConductorOptionsView (View):
	#@method_decorator(csrf_protect)
	def get (self, request, *args, **kwargs):
		query = request.GET.get('query', '')
		options = Conductor.objects.filter (nombre__istartswith=query).values()

		itemOptions = []
		for i, option in enumerate (options):
			itemLine = f"{i}. {option['nombre']}"
			itemText = "%s||%s||%s||%s||%s" % (option["nombre"], option["documento"], 
			           option["nacionalidad"], option ["licencia"], option ["fecha_nacimiento"])
			newOption = {"itemLine" : itemLine, "itemText" : itemText}
			itemOptions.append (newOption)
		
		return JsonResponse (itemOptions, safe=False)

#--------------------------------------------------------------------
# Options for autocomplete for "Ciudad-Pais. Fecha"
#--------------------------------------------------------------------
class CiudadPaisOptionsView (View):
	#@method_decorator(csrf_protect)
	def get (self, request, *args, **kwargs):
		query = request.GET.get('query', '')
		ciudadesPaises = self.getCiudadesPaisesFromQuery (query)

		itemOptions = []
		currentDate = self.getFormatedCurrentDate ()
		for i, item in enumerate (ciudadesPaises):
			itemLine = f"{i}. {item}"
			itemText = f"{item}. {currentDate}" if currentDate else f"{item}"
			newItem = {"itemLine" : itemLine, "itemText" : itemText}
			itemOptions.append (newItem)

		return JsonResponse (itemOptions, safe=False)

	#-- Return empty string for date
	def getFormatedCurrentDate (self):
		return ""

	def getCiudadesPaisesFromQuery (self, query):
		ciudadesPaises = ResourceLoader.loadText ("data_cartaportes", "ciudades-paises-colombia-ecuador.txt")
		ciudadesPaises = [x.upper().strip() for x in ciudadesPaises if x.upper().startswith (query)]
		return ciudadesPaises


class CiudadPaisFechaOptionsView (CiudadPaisOptionsView):
	#-- Return formated string for date
	def getFormatedCurrentDate (self):
		from datetime import datetime
		spanish_months = { "January": "ENERO", "February": "FEBRERO", "March": "MARZO", "April": "ABRIL",
			"May": "MAYO", "June": "JUNIO", "July": "JULIO", "August": "AGOSTO", "September": "SEPTIEMBRE",
			"October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"
		}
		current_time = datetime.now()

		# Format the current time as "YEAR-MONTH-DAY"
		formatted_time = current_time.strftime("%Y-{}-%d").format(spanish_months[current_time.strftime("%B")])

		return (formatted_time)

#--------------------------------------------------------------------
#--EmpresaOptionsView
#--------------------------------------------------------------------
class EmpresaOptionsView (View):
	#@method_decorator(csrf_protect)
	def get (self, request, *args, **kwargs):
		query = request.GET.get('query', '')
		options = Empresa.objects.filter (nombre__istartswith=query).values()

		itemOptions = []
		for i, option in enumerate (options):
			itemLine = f"{i}. {option['nombre']}"
			itemText = "%s\n%s\n%s-%s. %s:%s" % (
			              option ["nombre"], option ["direccion"], 
						  option ["ciudad"], option ["pais"],
						  option ["tipoId"], option ["numeroId"])

			newOption = {"itemLine" : itemLine, "itemText" : itemText}
			itemOptions.append (newOption)

		return JsonResponse (itemOptions, safe=False)


