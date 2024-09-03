import os, tempfile, json
from datetime import date

from django.db import models
from django.urls import reverse  # To generate URLS by reversing URL patterns

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info_manifiesto_BYZA import ManifiestoByza

from app_docs.models_EcuapassDoc import EcuapassDoc
from app_cartaporte.models_cpi import Cartaporte
from app_docs.models_Entidades import Vehiculo

#--------------------------------------------------------------------
# Model ManifiestoDoc
#--------------------------------------------------------------------
class ManifiestoDoc (models.Model):
	class Meta:
		db_table = "manifiestodoc"

	numero = models.CharField (max_length=20)

	txt0a = models.CharField (max_length=20, null=True)
	txt01 = models.CharField (max_length=20, null=True)
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
	txt10 = models.CharField (max_length=200, null=True)
	txt11 = models.CharField (max_length=200, null=True)
	txt12 = models.CharField (max_length=200, null=True)
	txt13 = models.CharField (max_length=200, null=True)
	txt14 = models.CharField (max_length=200, null=True)
	txt15 = models.CharField (max_length=200, null=True)
	txt16 = models.CharField (max_length=200, null=True)
	txt17 = models.CharField (max_length=200, null=True)
	txt18 = models.CharField (max_length=200, null=True)
	txt19 = models.CharField (max_length=200, null=True)
	txt20 = models.CharField (max_length=200, null=True)
	txt21 = models.CharField (max_length=200, null=True)
	txt22 = models.CharField (max_length=200, null=True)
	txt23 = models.CharField (max_length=200, null=True)
	txt24 = models.CharField (max_length=200, null=True)
	txt25_1 = models.CharField (max_length=200, null=True)
	txt25_2 = models.CharField (max_length=200, null=True)
	txt25_3 = models.CharField (max_length=200, null=True)
	txt25_4 = models.CharField (max_length=200, null=True)
	txt25_5 = models.CharField (max_length=200, null=True)
	txt26 = models.CharField (max_length=200, null=True)
	txt27 = models.CharField (max_length=200, null=True)
	#-- Info mercancia (cartaporte, descripcion, ...totales ----
	txt28 = models.CharField (max_length=200, null=True)    # Cartaporte
	txt29 = models.CharField (max_length=800, null=True)    # Descripcion
	txt30 = models.CharField (max_length=200, null=True)    # Cantidad
	txt31 = models.CharField (max_length=200, null=True)    # Marca
	txt32_1 = models.CharField (max_length=200, null=True)  # Peso bruto
	txt32_2 = models.CharField (max_length=200, null=True)  # Peso bruto total
	txt32_3 = models.CharField (max_length=200, null=True)  # Peso neto
	txt32_4 = models.CharField (max_length=200, null=True)  # Peso neto total
	txt33_1 = models.CharField (max_length=200, null=True)  # Otra medida
	txt33_2 = models.CharField (max_length=200, null=True)  # Otra medida total
	txt34 = models.CharField (max_length=200, null=True)    # INCOTERMS
	#------------------------------------------------------------
	txt35 = models.CharField (max_length=200, null=True)
	txt37 = models.CharField (max_length=200, null=True)
	txt38 = models.CharField (max_length=200, null=True)
	txt40 = models.CharField (max_length=200, null=True)

	def getConductor (self):
		return self.txt13

	def __str__ (self):
		return f"{self.numero}, {self.txt03}"
	
#--------------------------------------------------------------------
# Model Manifiesto
#--------------------------------------------------------------------
class Manifiesto (EcuapassDoc):
	class Meta:
		db_table = "manifiesto"

	documento     = models.OneToOneField (ManifiestoDoc, on_delete=models.CASCADE, null=True)

	vehiculo      = models.ForeignKey (Vehiculo, on_delete=models.SET_NULL, related_name='vehiculo', null=True)
	cartaporte    = models.ForeignKey (Cartaporte, on_delete=models.SET_NULL, null=True)

	def get_absolute_url(self):
		"""Returns the url to access a particular language instance."""
		return reverse('manifiesto-detail', args=[str(self.id)])

	def setValues (self, manifiestoDoc, docFields, procedimiento, username):
		# Base values
		self.numero        = manifiestoDoc.numero
		self.documento     = manifiestoDoc
		self.procedimiento = procedimiento
		self.usuario       = self.getUserByUsername (username)

		# Document values
		jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
		manifiestoInfo     = ManifiestoByza (jsonFieldsPath, runningDir)

		self.vehiculo      = self.getVehiculo (manifiestoInfo, "vehiculo")
		self.remolque      = self.getVehiculo (manifiestoInfo, "remolque")
		self.cartaporte    = self.getCartaporte (manifiestoInfo)
		#print ("+++ ManifiestoInfo:", manifiestoInfo.fields)
		print ("+++ Cartaporte:", self.cartaporte)
		
	#-- Get cartaporte from manifiesto info
	def getCartaporte (self, manifiestoInfo):
		numeroCartaporte = None
		try:
			numeroCartaporte = manifiestoInfo.getNumeroCartaporte ()
			record = Cartaporte.objects.get (numero=numeroCartaporte)
			return record
		except: 
			Utils.printx (f"ALERTA: Cartaporte número '{numeroCartaporte}' no encontrado.")
		return None

	def getVehiculo (self, manifiestoInfo, vehicleType):
		try:
			info = manifiestoInfo.getVehiculoRemolqueInfo (vehicleType)

			if any (value is None for value in info.values()):
				return None
			else:
				vehiculo, created = Vehiculo.objects.get_or_create (placa=info['placa'])

				vehiculo.marca       = info ["marca"]
				vehiculo.placa       = info ["placa"]
				vehiculo.pais        = info ["pais"]
				vehiculo.chasis      = info ["chasis"]
				vehiculo.anho        = info ["anho"]
				vehiculo.certificado = info ["certificado"]

				vehiculo.save ()
				return vehiculo
		except:
			Utils.printException (f"Obteniedo información del vehiculo.")
			return None

	def createTemporalJson (self, docFields):
		tmpPath        = tempfile.gettempdir ()
		jsonFieldsPath = os.path.join (tmpPath, f"MANIFIESTO-{self.numero}.json")
		json.dump (docFields, open (jsonFieldsPath, "w"))
		return (jsonFieldsPath, tmpPath)

