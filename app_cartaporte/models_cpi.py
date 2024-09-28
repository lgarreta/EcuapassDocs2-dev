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
	txt12 = models.CharField (max_length=1400, null=True)  # Descripcion
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
	txt19 = models.CharField (max_length=100, null=True)     #19:Lugar, fecha emision
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
									   on_delete=models.CASCADE, null=True,
									   related_name="docs")
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
		return reverse('cartaporte-detalle', args=[str(self.id)])

	def setValues (self, cartaporteForm, docFields, pais, username):
		# Base values
		super().setValues (cartaporteForm, docFields, pais, username)

		# Document values
		self.remitente     = Scripts.getSaveClienteInstance ("02_Remitente", docFields)
		self.destinatario  = Scripts.getSaveClienteInstance ("03_Destinatario", docFields)
		self.fecha_emision = EcuInfo.getFechaEmision (docFields, "CARTAPORTE")
		
