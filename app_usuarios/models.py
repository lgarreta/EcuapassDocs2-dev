from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class UsuarioEcuapassManager (BaseUserManager):
	def create_user (self, username, email, password=None, **extra_fields):
		if not email:
			raise ValueError ('El correo es obligatorio')

		email = self.normalize_email (email)
		user  = self.model (username=username.strip (), email=email, **extra_fields)
		user.set_password (password)
		user.save (using=self._db)
		return user

	def create_superuser (self, username, email, password=None, **extra_fields):
		extra_fields.setdefault ('is_staff', True)
		extra_fields.setdefault ('is_superuser', True)
		extra_fields.setdefault ('perfil', 'director')

		if extra_fields.get ('is_staff') is not True:
			raise ValueError ('Superuser must have is_staff=True.')
		if extra_fields.get ('is_superuser') is not True:
			raise ValueError ('Superuser must have is_superuser=True.')

		return self.create_user (username, email, password, **extra_fields)

class UsuarioEcuapass (AbstractUser):
	PAIS_CHOICES = (('ECUADOR', 'ECUADOR'), ('COLOMBIA','COLOMBIA'),('PERU','PERU'),('TODOS','TODOS'),)
	USER_CHOICES = (('externo', 'Externo'), ('funcionario', 'Funcionario'), ('director', 'Director'),)
	class Meta:
		db_table = "usuarioecuapass"

	nombre	           = models.CharField (_ ('nombre'), max_length=100)
	pais               = models.CharField (max_length=20, choices=PAIS_CHOICES)
	perfil             = models.CharField (max_length=20, choices=USER_CHOICES)
	is_active	       = models.BooleanField (_ ('activo'), default=True)
	is_staff	       = models.BooleanField (_ ('staff'), default=False)
	es_director	       = models.BooleanField (default=False)
	es_funcionario	   = models.BooleanField (default=False)
	es_externo	       = models.BooleanField (default=True)
	date_joined        = models.DateTimeField (_ ('fecha de registro'), auto_now_add=True)
	nro_docs_creados   = models.IntegerField (default=0)
	nro_docs_asignados = models.IntegerField (default=0)


	username = models.CharField (_ ('nombre de usuario'), max_length=30, unique=True,
		help_text='Requerido. Letras y digitos, sin espacios ni carácteres, tildes o eñes.',
		validators=[], error_messages={ 'unique': "Este nombre de usuario ya está registrado..",},
	)
	email = models.EmailField (_ ('correo electrónico'), unique=True,
		help_text='Requerido.', 
		validators=[], error_messages={ 'unique': "Este correo ya está registrado..",},
	)

	def get_pais (self):
		return self.pais

	#-------------------------------------------------------------------
	# Methods for special column "Acciones" when listing users
	#-------------------------------------------------------------------
	def get_link_actualizar(self):
		return reverse('actualizar', args=[self.pk])

	def get_link_eliminar(self):
		return reverse('eliminar', args=[self.pk])

	#-------------------------------------------------------------------

	objects = UsuarioEcuapassManager ()
