# from django import forms
# from .models import UsuarioEcuapass
# from django.contrib.auth.forms import UserCreationForm

# class RegistrationForm (UserCreationForm):
#	  email = forms.EmailField (required=True)
#	  class Meta:
#		  model = UsuarioEcuapass
#		  fields = ['username', 'email', 'perfil', 'password1', 'password2']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from .models import UsuarioEcuapass

class RegistrationForm (UserCreationForm):
	email = forms.EmailField (required=False, widget=forms.EmailInput (attrs={'class': 'form-control'}))
	password1 = forms.CharField (
		label="Ingrese la Clave",
		widget=forms.PasswordInput (attrs={'class': 'form-control', 'id': 'password-input', 'autocomplete':'off'}),
		help_text=password_validation.password_validators_help_text_html (),
	)
	password2 = forms.CharField (
		label="Confirme la Clave",
		widget=forms.PasswordInput (attrs={'class': 'form-control', 'autocomplete':'off'}),
	)

	# Add an additional field for password strength
	password_strength = forms.CharField (
		widget=forms.HiddenInput (),
		required=False,
	)

	username = forms.CharField (
		label="Nombre Usuario",
		widget=forms.TextInput (attrs={'autocomplete':'off'}),
	)

	class Meta:
		model = UsuarioEcuapass
		fields =  ('username', 'email', 'first_name', 'last_name', 'perfil', 'nro_docs_asignados')

	def __init__ (self, *args, **kwargs):
		super().__init__ (*args, **kwargs)
		self.fields ["username"].label = "Usuario"
		self.fields ["email"].label = "Correo"
		self.fields ["perfil"].label = "Tipo de usuario"


