
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.urls import reverse_lazy

from app_cartaportes.models_cpi import Cartaporte, CartaporteDoc

#--------------------------------------------------------------------
#--------------------------------------------------------------------
# Decorador personalizado para requerir autenticación en una vista basada en clase
def login_required_class (view_func):
	return method_decorator (login_required, name='dispatch') (view_func)

#--------------------------------------------------------------------
#-- Cartaporte
#--------------------------------------------------------------------

class CartaporteListView (generic.ListView):
	model = Cartaporte

class CartaporteDetailView (generic.DetailView):
	model = Cartaporte

class CartaporteCreate (login_required_class (CreateView)):
	model = Cartaporte
	fields = '__all__'

class CartaporteDoc (login_required_class (UpdateView)):
	model = Cartaporte
	fields = '__all__'
	#fields = ['tipo','remitente','destinatario','fecha_emision']

class CartaporteUpdate (login_required_class (UpdateView)):
	model = Cartaporte
	fields = '__all__'
	#fields = ['tipo','remitente','destinatario','fecha_emision']

class CartaporteDelete (login_required_class (DeleteView)):
	model = Cartaporte
	success_url = reverse_lazy ('cartaporte-listado')

#	def post (self, request, *args, **kwargs):
#		print ("-- On post...")
#		# Delete related objects or one-to-one relationships here
#		# Get the object to be deleted
#		self.object = self.get_object ()		
#		self.object.documento.delete ()
#
#		add_message (request, messages.ERROR, "Cartaporte borrada.")
#		#return return (request, 'messages.html')
#		return reverse ('cartaportes', args=[])
#		#return reverse ('empresa-detail', args=[str (self.id)])
#
	def delete (self, request, *args, **kwargs):
		print ("-- On delete...")
		# Delete related objects
		related_objects = self.object.related_objects.all ()
		for obj in related_objects:
			print ("--obj:", obj)

		related_objects.delete ()

		# Delete the object using the default behavior
		return super ().delete (request, *args, **kwargs)

