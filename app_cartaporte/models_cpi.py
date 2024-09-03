import os, tempfile, json

from django.db import models
from django.urls import reverse   # To generate URLS by reversing URL patterns

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_data import EcuData
from ecuapassdocs.info.ecuapass_info import EcuInfo
from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza

from app_docs.models_EcuapassDoc import EcuapassDoc
from app_docs.models_Entidades import Cliente
import app_docs.models_Scripts as Scripts

#--------------------------------------------------------------------
# Model CartaporteForm
#--------------------------------------------------------------------
class CartaporteDoc (models.Model):
	class Meta:
		db_table = "cartaportedoc"

	numero = models.CharField (max_length=20)

	txt0a = models.CharField (max_length=20, null=True)
	txt00 = models.CharField (max_length=20, null=True)
	txt01 = models.CharField (max_length=200, null=True)
	txt02 = models.CharField (max_length=200, null=True)
	txt03 = models.CharField (max_length=200, null=True)
	txt04 = models.CharField (max_length=200, null=True)
	txt05 = models.CharField (max_length=200, null=True)
	txt06 = models.CharField (max_length=200, null=True)
	txt07 = models.CharField (max_length=200, null=True)
	txt08 = models.CharField (max_length=200, null=True)
	txt09 = models.CharField (max_length=200, null=True)
	#-- Bultos
	txt10 = models.CharField (max_length=200, null=True)   # Cantidad/Clase 
	txt11 = models.CharField (max_length=200, null=True)   # Marcas/Numeros
	txt12 = models.CharField (max_length=900, null=True)   # Descripcion
	txt13_1 = models.CharField (max_length=200, null=True) # Peso Neto
	txt13_2 = models.CharField (max_length=200, null=True) # Peso Bruto
	txt14 = models.CharField (max_length=200, null=True)   # Volumen
	txt15 = models.CharField (max_length=200, null=True)   # Otras unidades
	txt16 = models.CharField (max_length=200, null=True)   # INCOTERMS
	#-- Tabla Gastos --------------------------------------
	txt17_11 = models.CharField (max_length=200, null=True)
	txt17_12 = models.CharField (max_length=200, null=True)
	txt17_13 = models.CharField (max_length=200, null=True)
	txt17_14 = models.CharField (max_length=200, null=True)
	txt17_21 = models.CharField (max_length=200, null=True) # USD
	txt17_22 = models.CharField (max_length=200, null=True) # USD
	txt17_23 = models.CharField (max_length=200, null=True) # USD
	txt17_24 = models.CharField (max_length=200, null=True) # USD
	txt17_31 = models.CharField (max_length=200, null=True)
	txt17_32 = models.CharField (max_length=200, null=True)
	txt17_33 = models.CharField (max_length=200, null=True)
	txt17_34 = models.CharField (max_length=200, null=True) 
	txt17_41 = models.CharField (max_length=200, null=True) # USD
	txt17_42 = models.CharField (max_length=200, null=True) # USD
	txt17_43 = models.CharField (max_length=200, null=True) # USD
	txt17_44 = models.CharField (max_length=200, null=True) # USD
	#-------------------------------------------------------
	txt18 = models.CharField (max_length=200, null=True)
	txt19 = models.CharField (max_length=50, null=True)
	txt21 = models.CharField (max_length=200, null=True)
	txt22 = models.CharField (max_length=300, null=True)
	txt24 = models.CharField (max_length=200, null=True)

#	def get_absolute_url(self):
#		"""Returns the url to access a particular language instance."""
#		#return reverse('cliente-detail', args=[str(self.id)])

	def __str__ (self):
		return f"{self.numero}, {self.txt02}, {self.txt03}"
	
	def getNumberFromId (self):
		numero = 2000000+ self.numero 
		numero = f"CI{numero}"
		return (self.numero)

	def getRemitente (self):
		return self.txt02

	def getDestinatario (self):
		return self.txt03

#--------------------------------------------------------------------
# Cartaporte Model
#--------------------------------------------------------------------
class Cartaporte (EcuapassDoc):
	class Meta:
		db_table = "cartaporte"

	documento     = models.OneToOneField (CartaporteDoc,
									   on_delete=models.CASCADE, null=True)
	remitente     = models.ForeignKey (Cliente, related_name="cartaportes_remitente",
	                                   on_delete=models.SET_NULL, null=True)
	destinatario  = models.ForeignKey (Cliente, related_name="cartaportes_destinatario",
	                                   on_delete=models.SET_NULL, null=True)
	def __str__ (self):
		return f"{self.numero}, {self.remitente}"

	def getDocType (self):
		return "CARTAPORTE"

	def get_absolute_url(self):
		"""Returns the url to access a particular language instance."""
		return reverse('cartaporte-detail', args=[str(self.id)])

	def setValues (self, cartaporteForm, docFields, pais, username):
		# Base values
		self.numero    = cartaporteForm.numero
		self.documento = cartaporteForm
		self.pais      = pais
		self.usuario   = self.getUserByUsername (username)

		# Document values
		self.remitente     = Scripts.getSaveClienteInstance ("02_Remitente", docFields)
		self.destinatario  = Scripts.getSaveClienteInstance ("03_Destinatario", docFields)
		self.fecha_emision = EcuInfo.getFechaEmision (docFields, "CARTAPORTE")
		# Get 'fecha recepcion'
		#self.fecha_emision = self.getFechaRecepcion ("31_FechaRecepcion", docFields)

		
#	#-- Get fecha de recepcion
#	def getFechaRecepcion (self, fieldName, docFields):
#		jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
#		cartaporteInfo    = CartaporteByza (jsonFieldsPath, runningDir)
#		ecuapassFields    = cartaporteInfo.getMainFields ()
#		ecuapassFieldsUpd = cartaporteInfo.updateEcuapassFields (ecuapassFields)
#		fechaRecepcion    = ecuapassFields ["31_FechaRecepcion"]
#		return datetime.datetime.strptime (fechaRecepcion, "%d-%m-%Y")

#----------------- MOVED TO SUPER ------------------
#	#-- Get fecha emision
#	def getFechaEmision (self, docFields):
#		fecha = Utils.getEcuapassFieldInfo (CartaporteByza, "61_FechaEmision", docFields)
#		print ("+++ DEBUG: fecha:", fecha)
#		fecha = fecha if fecha else datetime.today()
#		fecha_emision = Utils.formatDateStringToPGDate (fecha)
#		print ("+++ DEBUG: fecha_emision:", fecha_emision)
#		return fecha_emision

	#-- Get/Save subject info. Only works for BYZA
#	def getSubjectInstance (self, subjectType, docFields):
#		info = None
#		try:
#			jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
#			cartaporteInfo    = CartaporteByza (jsonFieldsPath, runningDir)
#			info              = cartaporteInfo.getSubjectInfo (subjectType)
#			print ("-- Subject info:", info)
#
#			if any (value is None for value in info.values()) or \
#			   any ("||LOW" in value for value in info.values()):
#				return None
#			else:
#				cliente, created = Cliente.objects.get_or_create (numeroId=info['numeroId'])
#
#				cliente.nombre    = info ["nombre"]
#				cliente.direccion = info ["direccion"]
#				cliente.ciudad    = info ["ciudad"]
#				cliente.pais      = info ["pais"]
#				cliente.tipoId    = info ["tipoId"]
#				cliente.numeroId  = info ["numeroId"]
#
#				cliente.save ()
#				return cliente
#		except:
#			Utils.printException (f"Obteniedo datos del remitente en la info: ", str (info))
#			return None

