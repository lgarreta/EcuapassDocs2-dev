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

	#-- Save by incrementing the last doc number in the DB
	def save (self, *args, **kwargs):
		if not self.numero:
			self.numero = self.generateDocNumber ()
		super().save (*args, **kwargs)

	#-- Generate doc number from last doc number saved in DB
	def generateDocNumber (self):
		lastDoc = self._meta.model.objects.filter (pais=self.pais).order_by ("-id").first ()
		print (f"+++ DEBUG: generateDocNumber:lastDoc '{lastDoc}'")
		if lastDoc:
			lastNumber = Utils.getNumberFromDocNumber (lastDoc.numero)
			newNumber  = str (lastNumber + 1).zfill (5)
		else:
			newNumber  = str (1).zfill (5)

		docNumber = Utils.getCodigoPaisFromPais (self.pais) + newNumber
		return docNumber

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

#	#-------------------------------------------------------------------
#	# Get cartaporte from doc fields and save to DB
#	#-------------------------------------------------------------------
#	def getCartaporteInstance (self, docKey, docFields):
#		cartaporte = None
#		try:
#			cartaporteNumber    = EcuInfo.getNumeroCartaporte (docFields)
#			cartaporte, created = Cartaporte.objects.get (numero=cartaporteNumber)
#			return cartaporte
#		except Cartaporte.DoesNotExists:
#			Utils.printException (f"No existe cartaporte nro: '{cartaporteNumber}'!")
#		except Cartaporte.MultipleObjectsReturned:
#			Utils.printException (f"Múltiples instancias de cartaporte nro: '{cartaporteNumber}'!")
#		return cartaporte
#	#-------------------------------------------------------------------
#	#-- Get/Save cliente info. Only works for BYZA
#	#-- field keys correspond to: remitente, destinatario,... (Cartaporte)
#	#-------------------------------------------------------------------
#	def getSaveClienteInfo (self, docKey, docFields):
#		clienteInfo  = self.getClienteInfo (docKey, docFields)
#		if clienteInfo:
#			cliente = self.saveClienteInfoToDB (clienteInfo)
#			return cliente
#		else:
#			return None
#
#	def getClienteInfo (self, docKey, docFields):
#		info = None
#		try:
#			jsonFieldsPath, runningDir = Utils.createTemporalJson (docFields)
#			cartaporteInfo    = CartaporteByza (jsonFieldsPath, runningDir)
#			info              = cartaporteInfo.getSubjectInfo (docKey)
#			print ("-- Subject info:", info)
#
#			if any (value is None for value in info.values()) or \
#			   any ("||LOW" in value for value in info.values()):
#				return None
#		except:
#			Utils.printException (f"Obteniedo info de cliente tipo: '{docKey}'")
#
#		return info
#
#	#-- Save instance of Cliente with info: id, nombre, direccion, ciudad, pais, tipoId, numeroId
#	def saveClienteInfoToDB (self, info):
#		cliente = None
#		try:
#			cliente, created = Cliente.objects.get_or_create (numeroId=info['numeroId'])
#
#			cliente.nombre    = info ["nombre"]
#			cliente.direccion = info ["direccion"]
#			cliente.ciudad    = info ["ciudad"]
#			cliente.pais      = info ["pais"]
#			cliente.tipoId    = info ["tipoId"]
#			cliente.numeroId  = info ["numeroId"]
#
#			cliente.save ()
#		except:
#			Utils.printException (f"Guardando cliente to DB")
#		return cliente

#--------------------------------------------------------------------
# Model Cartaporte Form
#--------------------------------------------------------------------
#class EcuapassForm (models.Model):
#	numero = models.CharField (max_length=20)
#
##	def get_absolute_url(self):
##		"""Returns the url to access a particular language instance."""
##		#return reverse('cliente-detail', args=[str(self.id)])
#
#	def __str__ (self):
#		return f"{self.numero}, {self.txt02}, {self.txt03}"
#	
#	def getNumberFromId (self):
#		numero = 2000000+ self.numero 
#		numero = f"CI{numero}"
#		return (self.numero)
#	#-------------------------------------------------------------------
#	#-- Search a pattern in all fields of a model
#	#-------------------------------------------------------------------
#	def searchModelAllFields (self, searchPattern):
#		queries = Q()
#		FORMMODEL = self.__class__
#		print (f"+++ DEBUG: FORMMODEL '{FORMMODEL}'")
#		for field in FORMMODEL._meta.fields:
#			field_name = field.name
#			print (f"+++ DEBUG: field_name '{field_name}'")
#			queries |= Q(**{f"{field_name}__icontains": searchPattern})
#		
#		results = DOCMODEL.objects.filter (queries)
#		return results
#

