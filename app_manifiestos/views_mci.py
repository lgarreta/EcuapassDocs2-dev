
from django.views import View, generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
#from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.urls import reverse_lazy

from app_manifiestos.models_mci import Manifiesto

#--------------------------------------------------------------------
#--------------------------------------------------------------------
# Decorador personalizado para requerir autenticación en una vista basada en clase
def login_required_class (view_func):
	return method_decorator (login_required, name='dispatch') (view_func)

#--------------------------------------------------------------------
#-- Manifiesto
#--------------------------------------------------------------------

class ManifiestoListView (generic.ListView):
	model = Manifiesto

class ManifiestoDetailView (generic.DetailView):
	model = Manifiesto

class ManifiestoCreate (login_required_class (CreateView)):
	model = Manifiesto
	fields = '__all__'

class ManifiestoUpdate (login_required_class (UpdateView)):
	model = Manifiesto
	fields = ['vehiculo', 'cartaporte']

class ManifiestoDelete (login_required_class (DeleteView)):
	model = Manifiesto
	success_url = reverse_lazy ('manifiestos')

#--------------------------------------------------------------------
# Update manifiesto with cartaporte number from form
#--------------------------------------------------------------------
class UpdateCartaporteView (View):
	@method_decorator(csrf_protect)
	def post (self, request, *args, **kwargs):
		cartaporteNumber = request.POST.get ("cartaporteNumber")
		print ("+++ cpiValue:", cartaporteNumber)
		if cartaporteNumber:
			print ("+++ Updating 'manifiesto' table with CPIC: ", cartaporteNumber)
			return JsonResponse ({'status': 'success'})

		return JsonResponse ({'status': 'error'})

	def updateCartaporte (self):
		from myapp.models import Product, Category

		# Assume you want to update the product's category to 'Electronics'
		new_category_name = 'Electronics'
		product_id = 1

		# Check if the category with the name 'Electronics' exists
		if Cartaporte.objects.filter (numero=cartaporteNumber).exists():
			# Get the category instance
			cartaporte = Cartaporte.objects.get (numero=cartaporteNumber)

			# Retrieve the product instance
			manifiesto = Manifiesto.objects.get (id=manifiestoId)

			# Update the product's category
			manifiesto.cartaporte = cartaporte

			# Save the changes
			manifiesto.save()
		else:
			# Handle the case where the category doesn't exist
			print(f"Cartaporte  '{cartaporteNumber}' no existe.")


