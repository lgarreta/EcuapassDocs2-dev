from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect

from .models import UsuarioEcuapass
from .tables import UserTable


class UserCreate (LoginRequiredMixin, CreateView):
	model = UsuarioEcuapass
	fields = ['username','email', 'first_name', 'last_name', 'password', 'perfil', 
	          'nro_docs_creados', 'nro_docs_asignados']
	template_name = 'user_create.html'
	success_url = reverse_lazy ('listar')

class UserDelete (LoginRequiredMixin, DeleteView):
	model = UsuarioEcuapass
	template_name = 'user_delete.html'
	success_url = reverse_lazy ('listar')

class UserUpdate (LoginRequiredMixin, UpdateView):
	model = UsuarioEcuapass
	fields = ['username','email', 'first_name', 'last_name', 'perfil', 
	          'nro_docs_creados', 'nro_docs_asignados']
	template_name = 'user_update.html'
	success_url = reverse_lazy ('listar')

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		form.fields['username'].widget.attrs['readonly'] = True  # Set username field as readonly
		return form	

def user_list(request):
	print ("--- user_list ---")
	if (not request.user.is_staff):
		url =  reverse_lazy ("index")
		return redirect (url)

	users = UsuarioEcuapass.objects.all()
	table = UserTable (users)
	return render(request, 'user_list.html', {'table': table})	

def registration (request):
	if request.method == 'POST':
		# Create a form that has request.POST
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = form.save (commit=False)
			# Set the user's password securely
			username  = form.cleaned_data['username']		 
			password1 = form.cleaned_data['password1']
			password2 = form.cleaned_data['password2']

			# Set user type flag
			perfil      = form.cleaned_data['perfil']		 
			user.es_director    = perfil == "director"
			user.es_funcionario = perfil == "funcionario"
			user.es_externo     = perfil == "externo"

			user.is_staff       = user.es_director

			if password1 == password2:
				print (">>> USER:", dir (user))
				user.set_password (password1)
				user.save()
				
				messages.success(request, f'Su cuenta ha sido creada {username} ! Proceda a ingresar')
				return redirect('login')  # Redirect to the login page
			else:
				# Handle password mismatch error here
				form.add_error('password2', 'Claves ingresadas no coinciden')

	else:
		form = RegistrationForm()
	return render(request, 'registration.html', {'form': form})

