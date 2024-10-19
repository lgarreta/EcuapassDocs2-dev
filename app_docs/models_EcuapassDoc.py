"""
Base model for doc models: Cartaporte, Manifiesto, Declaracion
"""

from datetime import date

from django.db import models
from django.urls import reverse

from app_usuarios.models import UsuarioEcuapass
from ecuapassdocs.info.ecuapass_utils import Utils 
from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza

from django.db.models import Q

from .models_Entidades import Cliente

#--------------------------------------------------------------------
# Base model for doc models: Cartaporte, Manifiesto, Declaracion
#--------------------------------------------------------------------
class EcuapassDoc (models.Model):
	numero         = models.CharField (max_length=20)
	fecha_emision  = models.DateField (null=True)
	pais           = models.CharField (max_length=30)
	usuario        = models.ForeignKey (UsuarioEcuapass, on_delete=models.SET_NULL, null=True)
	referencia     = models.CharField (max_length=30, null=True, blank=True)
	fecha_creacion = models.DateTimeField (auto_now_add=True, null=False)

	class Meta:
		abstract = True

	#----------------------------------------------------------------
	# Set base values to document
	# Overwritten in child classes
	#----------------------------------------------------------------
	def setValues (self, formInstance, docFields, pais, username):
		# Base values
		self.numero     = formInstance.numero
		self.documento  = formInstance
		self.pais       = pais
		self.usuario    = self.getUserByUsername (username)

		try:
			self.referencia = docFields ["referencia"]
		except:
			self.referencia = None

	#-- Returns document type as class model name ("cartaporte", "manifiesto", "declaracion")
	def getDocType(self):
		return self.__class__.__name__.upper ()

	#-- Get str for printing
	def __str__ (self):
		return f"{self.numero}, {self.fecha_emision}"

	#-- Delete related objects
	def delete (self, *args, **kwargs):
		print ("-- EcuapassDoc delete")
		DocumentClass = type (self.documento)
		DocumentClass.objects.filter (numero=self.numero).delete()
		super().delete(*args, **kwargs)	

	#-- Return user instance by username
	def getUserByUsername (self, username):
		user = UsuarioEcuapass.objects.get (username=username)
		return user

	#-------------------------------------------------------------------
	# Methods for special column "Acciones" when listing documents
	#-------------------------------------------------------------------
	def get_link_editar(self):
		docName = self.getDocType ().lower()
		url     = f"{docName}-editardoc"
		return reverse (url, args=[self.pk])

	def get_link_eliminar(self):
		docName = self.getDocType ().lower()
		url     = f"{docName}-delete"
		return reverse (url, args=[self.pk])

	def get_link_detalle(self):
		docName = self.getDocType ().lower()
		url     = f"{docName}-detalle"
		return reverse (url, args=[self.pk])


	#-------------------------------------------------------------------
	#-- Search a pattern in all 'FORMMODEL' fields of a model
	#-- Overwritten in some child classes
	#-------------------------------------------------------------------
	def searchModelAllFields (self, searchPattern):
		queries = Q()
		FORMMODEL = self._meta.get_field ('documento').related_model
		for field in FORMMODEL._meta.fields:
			field_name = field.name
			queries |= Q(**{f"{field_name}__icontains": searchPattern})
		
		formInstances = FORMMODEL.objects.filter (queries)
		DOCMODEL      = self.__class__
		docInstances  = DOCMODEL.objects.filter (documento__in=formInstances)
		return docInstances


