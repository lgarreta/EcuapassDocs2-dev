import os, tempfile, json
from datetime import datetime, timedelta

from django.db import models
from django.urls import reverse   # To generate URLS by reversing URL patterns
from django.utils import timezone # For getting recent cartaportes

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_data import EcuData
from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza

from appusuarios.models import UsuarioEcuapass
from appdocs.models_Entidades import Empresa
from appdocs.models_EcuapassDoc import EcuapassDoc
from appusuarios.models import UsuarioEcuapass

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
#		#return reverse('empresa-detail', args=[str(self.id)])

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
# Model Cartaporte
#--------------------------------------------------------------------
class Cartaporte (EcuapassDoc):
	class Meta:
		db_table = "cartaporte"

	documento     = models.OneToOneField (CartaporteDoc, on_delete=models.CASCADE)
	remitente     = models.ForeignKey (Empresa, related_name="Empresa_cartaporte_set_remitente",
	                                   on_delete=models.SET_NULL, null=True)
	destinatario  = models.ForeignKey (Empresa, related_name="Empresa_cartaporte_set_destinatario",
	                                   on_delete=models.SET_NULL, null=True)

	def __str__ (self):
		return f"{self.numero}, {self.remitente}"

	def get_absolute_url(self):
		"""Returns the url to access a particular language instance."""
		return reverse('cartaporte-detail', args=[str(self.id)])

	def setValues (self, cartaporteForm, docFields, procedimiento, username):
		# General values
		self.numero        = cartaporteForm.numero
		self.documento     = cartaporteForm
		self.procedimiento = procedimiento
		self.usuario       = self.getUserByUsername (username)

		# Document values
		self.remitente     = self.getSubjectInstance ("02_Remitente", docFields)
		self.destinatario  = self.getSubjectInstance ("03_Destinatario", docFields)
		# Get 'fecha recepcion'
		#self.fecha_emision = self.getFechaRecepcion ("31_FechaRecepcion", docFields)
		fecha = Utils.getEcuapassFieldInfo (CartaporteByza, "61_FechaEmision", docFields)
		self.fecha_emision = fecha if fecha else datetime.today().strftime ("%Y-%m-%d")

		
#	#-- Get fecha de recepcion
#	def getFechaRecepcion (self, fieldName, docFields):
#		jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
#		cartaporteInfo    = CartaporteByza (jsonFieldsPath, runningDir)
#		ecuapassFields    = cartaporteInfo.getMainFields ()
#		ecuapassFieldsUpd = cartaporteInfo.updateEcuapassFields (ecuapassFields)
#		fechaRecepcion    = ecuapassFields ["31_FechaRecepcion"]
#		return datetime.datetime.strptime (fechaRecepcion, "%d-%m-%Y")

	#-- Get/Save subject info. Only works for BYZA
	def getSubjectInstance (self, subjectType, docFields):
		info = None
		try:
			jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
			cartaporteInfo    = CartaporteByza (jsonFieldsPath, runningDir)
			info              = cartaporteInfo.getSubjectInfo (subjectType)
			print ("-- Subject info:", info)

			if any (value is None for value in info.values()) or \
			   any ("||LOW" in value for value in info.values()):
				return None
			else:
				empresa, created = Empresa.objects.get_or_create (numeroId=info['numeroId'])

				empresa.nombre    = info ["nombre"]
				empresa.direccion = info ["direccion"]
				empresa.ciudad    = info ["ciudad"]
				empresa.pais      = info ["pais"]
				empresa.tipoId    = info ["tipoId"]
				empresa.numeroId  = info ["numeroId"]

				empresa.save ()
				return empresa
		except:
			Utils.printException (f"Obteniedo datos del remitente en la info: ", str (info))
			return None

	def createTemporalJson (self, docFields):
		tmpPath        = tempfile.gettempdir ()
		jsonFieldsPath = os.path.join (tmpPath, f"CARTAPORTE-{self.numero}.json")
		json.dump (docFields, open (jsonFieldsPath, "w"))
		return (jsonFieldsPath, tmpPath)

#	#-- Return user instance by username
#   
#	def getUserByUsername (self, username):
#		user = UsuarioEcuapass.objects.get (username=username)
#		return user
		
	#-- Return recent cartaportes (within the past week)
	def getRecentCartaportes ():
		diasRecientes = EcuData.configuracion ["dias_cartaportes_recientes"]
		oneWeekAgo = timezone.now () - timedelta (days=diasRecientes)
		recentCartaportes = Cartaporte.objects.filter (fecha_emision__gte=oneWeekAgo)
		for cartaporte in recentCartaportes:
			print (cartaporte.numero, cartaporte.fecha_emision)
		return recentCartaportes


 

