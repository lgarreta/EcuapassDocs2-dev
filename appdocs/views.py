import json

from django.shortcuts import render
from django.views import View
from django.views import generic

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from app_cartaportes.models_cpi import Cartaporte, CartaporteDoc
from app_manifiestos.models_mci import Manifiesto, ManifiestoDoc
from app_declaraciones.models_dti import Declaracion, DeclaracionDoc
from .models_Entidades import Empresa, Conductor, Vehiculo

def index(request):
	"""
	Función vista para la página inicio del sitio.
	"""
	# Genera contadores de algunos de los objetos principales
	num_empresas = Empresa.objects.all().count()
	num_conductors = Conductor.objects.all().count()
	num_vehiculos = Vehiculo.objects.all().count()
	num_cartaportes = Cartaporte.objects.all().count()
	num_manifestos = Manifiesto.objects.all().count()
	release        = getRelease ()
	
	
	# Number of visits to this view, as counted in the session variable.
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	# Renderiza la plantilla HTML index.html con los datos en la variable contexto
	return render( request, 'index.html',
		context={'release': release,
		         'num_empresas':num_empresas,
				 'num_conductors':num_conductors,
				 'num_vehiculos':num_vehiculos,
				 'num_cartaportes':num_cartaportes, 
				 'num_manifiestos':num_manifestos,
				 'num_visits': num_visits
				 })

def getRelease ():
	infoFile = settings.STATIC_ROOT + "/appdocs/json/ecuapassdocs-info.json"
	with open (infoFile) as fp:
		info = json.load (fp)
	return info ["release"]
	

# Decorador personalizado para requerir autenticación en una vista basada en clase
def login_required_class(view_func):
	return method_decorator(login_required, name='dispatch')(view_func)

#--------------------------------------------------------------------
#-- Empresa
#--------------------------------------------------------------------
class EmpresaListView(generic.ListView):
	model = Empresa

class EmpresaDetailView(generic.DetailView):
	model = Empresa
	
class EmpresaCreate(login_required_class(CreateView)):
	model = Empresa
	fields = '__all__'

class EmpresaUpdate(login_required_class(UpdateView)):
	model = Empresa
	fields = ['tipoId','nombre','direccion','ciudad', 'pais']

class EmpresaDelete(login_required_class(DeleteView)):
	model = Empresa
	success_url = reverse_lazy('empresas')


#--------------------------------------------------------------------
#-- Vehiculo
#--------------------------------------------------------------------
class VehiculoListView(generic.ListView):
	model = Vehiculo

class VehiculoDetailView(generic.DetailView):
	model = Vehiculo

#class ManifiestoListView(generic.ListView):
#	model = Manifiesto
#
#class ManifiestoDetailView (generic.DetailView):
#	model = Manifiesto

#--------------------------------------------------------------------
#-- Vehiculo
#--------------------------------------------------------------------
class VehiculoCreate(login_required_class(CreateView)):
	model = Vehiculo
	fields = '__all__'

class VehiculoUpdate(login_required_class(UpdateView)):
	model = Vehiculo
	fields = ['pais','marca','chasis','anho']

class VehiculoDelete(login_required_class(DeleteView)):
	model = Vehiculo
	success_url = reverse_lazy('vehiculos')

#--------------------------------------------------------------------
#-- Conductor
##--------------------------------------------------------------------
class ConductorListView(generic.ListView):
	model = Conductor

class ConductorDetailView(generic.DetailView):
	model = Conductor

class ConductorCreate(login_required_class(CreateView)):
	model = Conductor
	fields = '__all__'

class ConductorUpdate(login_required_class(UpdateView)):
	model = Conductor
	fields = ['nombre','nacionalidad','licencia','fecha_nacimiento']

class ConductorDelete(login_required_class(DeleteView)):
	model = Conductor
	success_url = reverse_lazy('conductors')

#--------------------------------------------------------------------
#-- Manifiesto
#--------------------------------------------------------------------
#class ManifiestoCreate(login_required_class(CreateView)):
#	model = Manifiesto
#	fields = '__all__'
#
#class ManifiestoUpdate(login_required_class(UpdateView)):
#	model = Manifiesto
#	fields = ['vehiculo', 'cartaporte']
#
#class ManifiestoDelete (login_required_class(DeleteView)):
#	model = Manifiesto
#	success_url = reverse_lazy('manifiestos')

class InfoView(View):
	template_name = 'info_view.html'

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)

#--------------------------------------------------------------------
#-- Declaraciones
#--------------------------------------------------------------------
class DeclaracionListView(generic.ListView):
	model = Declaracion

#--------------------------------------------------------------------
#-- Declaracion
#--------------------------------------------------------------------

#class DeclaracionListView(generic.ListView):
#	model = Declaracion
#
#class DeclaracionDetailView(generic.DetailView):
#	model = Declaracion
#
#class DeclaracionCreate(login_required_class(CreateView)):
#	model = Declaracion
#	fields = '__all__'
#
#class DeclaracionDoc(login_required_class(UpdateView)):
#	model = Declaracion
#	fields = '__all__'
#	#fields = ['tipo','remitente','destinatario','fecha_emision']
#
#class DeclaracionUpdate(login_required_class(UpdateView)):
#	model = Declaracion
#	fields = '__all__'
#	#fields = ['tipo','remitente','destinatario','fecha_emision']
#
#class DeclaracionDelete(login_required_class(DeleteView)):
#	model = Declaracion
#	success_url = reverse_lazy('declaraciones')

#--------------------------------------------------------------------
# Messages view
#--------------------------------------------------------------------
def messagesView (request):
	if request.method == 'POST':
		# Process your form data... (replace with your actual logic)
		if form.is_valid():
			# Success message
			message = constants.SUCCESS
			get_messages(request).add(message, "Your form has been submitted successfully!")
		else:
			# Error message
			message = constants.ERROR
			get_messages(request).add(message, "There were errors in your form data. Please try again.")
	# Render your template
	return render(request, 'my_template.html')
