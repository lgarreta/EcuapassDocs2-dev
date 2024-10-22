import os, tempfile, json, re

from django.db import models
from django.urls import reverse   # To generate URLS by reversing URL patterns

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_data import EcuData
from ecuapassdocs.info.ecuapass_info import EcuInfo
from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza
import app_manifiesto as appMci
from app_docs.models_EcuapassDoc import EcuapassDoc
from app_docs.models_Entidades import Cliente
import app_docs.models_Scripts as Scripts

#--------------------------------------------------------------------
# Model CartaporteForm
#--------------------------------------------------------------------
class CartaporteForm (models.Model):
	class Meta:
		db_table = "cartaporteform"

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

	def getNumero (self):
		return self.txt00
	def getRemitente (self):
		return self.txt02
	def getDestinatario (self):
		return self.txt03

	def getMercanciaInfo (self):
		return {"cantidad":self.txt10, "marcas":self.txt11, "descripcion":self.txt12}

	def getManifiestoInfo (self, empresa, pais):
		empresaInfo = EcuData.empresas [empresa]

		if pais == "COLOMBIA":
			aduanaCruce, aduanaDestino  = "IPIALES-COLOMBIA", "TULCAN-ECUADOR" # "COLOMBIA" as default
		elif pais == "ECUADOR":
			aduanaCruce, aduanaDestino   = "TULCAN-ECUADOR", "IPIALES-COLOMBIA"
		else:
			raise Exception (f"Alerta: No se pudo determinar aduana cruce/destino desde país: '{pais}'")
			

		info = {
			"pais"              : pais[:2],
			"permisoOriginario" : empresaInfo ["permisos"]["originario"],
			"permisoServicios"  : empresaInfo ["permisos"]["servicios1"],
			"cartaporte"        : self.numero,
			"cantidad"          : self.txt10,
			"marcas"            : self.txt11,
			"descripcion"       : self.txt12,
			"pesoNeto"          : self.txt13_1,
			"pesoBruto"         : self.txt13_2,
			"volumen"           : self.txt14,
			"otrasUnd"          : self.txt15,
			"incoterms"         : re.sub (r'[\r\n]+\s*', '. ', self.txt16), # Plain INCONTERMS
			"fechaEmision"      : self.txt19,
			"aduanaCruce"       : aduanaCruce,
			"aduanaDestino"     : aduanaDestino
		}
		return info

#		doc ['numero'],  # Cartaporte
#		doc ["txt12"],   # Descripcion 
#		doc ["txt10"],   # Cantidad
#		doc ["txt11"],   # Marca
#		doc ["txt13_2"], # Peso bruto
#		doc ["txt13_1"], # Peso neto
#		doc ["txt15"],   # Otras unidades
#		re.sub (r'[\r\n]+\s*', '. ', doc ["txt16"]), # INCONTERMS
#		doc ["txt13_2"], # Peso bruto total
#		doc ["txt13_1"], # Peso neto total
#		doc ["txt15"],  # Otras unidades total
#		doc ["txt19"])   # Fecha emision


#--------------------------------------------------------------------
# Cartaporte Model
#--------------------------------------------------------------------
class Cartaporte (EcuapassDoc):
	class Meta:
		db_table = "cartaporte"

	documento     = models.OneToOneField (CartaporteForm,
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
		return reverse('cartaporte-editardoc', args=[str(self.id)])

	def setValues (self, cartaporteForm, docFields, pais, username):
		# Base values
		super().setValues (cartaporteForm, docFields, pais, username)

		# Document values
		self.remitente     = Scripts.getSaveClienteInstance ("02_Remitente", docFields)
		self.destinatario  = Scripts.getSaveClienteInstance ("03_Destinatario", docFields)
		self.fecha_emision = EcuInfo.getFechaEmision (docFields, "CARTAPORTE")
		
		# If not has, then create "suggested" manifiesto
		#self.createUpdateSuggestedManifiesto ()

#	#-- Create or update suggested Manifiesto according to Cartaporte values
#	def createUpdateSuggestedManifiesto (self):
#		#manifiesto, created = appMci.models_mci.Manifiesto.objects.get_or_create (numeroId=info['numeroId'])
#		if self.hasManifiesto ():
#			return
#
#		print ("+++ Creando manifiesto sugerido. ")
#		formCpi                      = self.documento    # CPI form
#		mercanciaInfo                = formCpi.getMercanciaInfo () # cantidad, descripcion, marcas
#		mercanciaInfo ["cartaporte"] = formCpi.numero
#
#		inputValues = {
#			"txt28": mercanciaInfo ["cartaporte"],
#			"txt29": mercanciaInfo ["descripcion"],
#			"txt30": mercanciaInfo ["cantidad"],
#			"txt31": mercanciaInfo ["marcas"],
#		}
#		manifiesto = self.saveSuggestedManifiesto (inputValues)
#
#	#-- Save suggested manifiesto
#	#-- TO OPTIMIZE: It is similar to EcuapassDocView::saveNewDocToDB
#	def saveSuggestedManifiesto (self, inputValues):
#		print ("+++ Guardando manifiesto sugerido en la BD...")
#
#		# First: save DocModel
#		docModel        = appMci.models_mci.Manifiesto (pais=self.pais, usuario=self.usuario)
#		docModel.numero = "SUGERIDO"
#		docModel.save ()
#
#		# Second, save FormModel
#		formModel = appMci.models_mci.ManifiestoForm (id=docModel.id, numero=docModel.numero)
#		inputValues ["txt00"] = formModel.numero
#
#		# Third, set FormModel values from input form values
#		for key, value in inputValues.items():
#			if key not in ["id", "numero"]:
#				setattr (formModel, key, value)
#
#		# Fourth, save FormModel and update DocModel with FormModel
#		formModel.save ()
#		docModel.documento  = formModel
#		docModel.cartaporte = self
#		docModel.save ()
#		return docModel
#
	#-- Check if the CPI has a "manifiesto"
	def hasManifiesto (self):
		cartaporteNumber = self.numero
		try:
			manifiesto = appMci.models_mci.Manifiesto.objects.get (cartaporte=self.id)
			return True
		except appMci.models_mci.Manifiesto.DoesNotExist:
			print (f"+++ No existe manifiesto para cartaporte nro: '{cartaporteNumber}´")
			return False

