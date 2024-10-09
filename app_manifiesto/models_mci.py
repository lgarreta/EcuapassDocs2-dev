import os, tempfile, json

from django.db import models
from django.urls import reverse  # To generate URLS by reversing URL patterns

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info import EcuInfo
from ecuapassdocs.info.ecuapass_info_manifiesto_BYZA import ManifiestoByza

from app_docs.models_EcuapassDoc import EcuapassDoc
from app_cartaporte.models_cpi import Cartaporte
from app_docs.models_Entidades import Vehiculo, Conductor
import app_docs.models_Scripts as Scripts

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
	conductor     = models.ForeignKey (Conductor, on_delete=models.SET_NULL, related_name='conductor', null=True)
	cartaporte    = models.ForeignKey (Cartaporte, on_delete=models.SET_NULL, null=True)

	def get_absolute_url (self):
		"""Returns the url to access a particular language instance."""
		return reverse('manifiesto-detalle', args=[str(self.id)])

	def setValues (self, manifiestoForm, docFields, pais, username):
		# Base values
		super().setValues (manifiestoForm, docFields, pais, username)

		# Document values
		jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
		manifiestoInfo     = ManifiestoByza (jsonFieldsPath, runningDir)
		self.cartaporte    = self.getCartaporteInstance (manifiestoInfo)

		self.getSaveVehiculoConductorInstance (manifiestoInfo)
		self.fecha_emision = EcuInfo.getFechaEmision (docFields, "MANIFIESTO")

		#self.updateFieldRelations ()

	#-- Get and save info vehiculo/remolque/conductor/auxiliar
	def getSaveVehiculoConductorInstance (self, manifiestoInfo):
		# Vehiculo
		veinfo = manifiestoInfo.extractVehiculoInfo ()
		vehiculo, changeFlag = self.getSaveUpdateInstance ("vehiculo", veinfo)

		# Remolque
		reinfo = manifiestoInfo.extractVehiculoInfo (type="REMOLQUE")
		remolque, changeFlag = self.getSaveUpdateInstance ("vehiculo", reinfo)
		if not Scripts.areEqualsInstances (vehiculo.remolque, remolque):
			vehiculo.remolque = remolque
			vehiculo.save ()

		# Conductor
		coinfo = manifiestoInfo.extractConductorInfo ()
		conductor, changeFlag = self.getSaveUpdateInstance ("conductor", coinfo)
		if not Scripts.areEqualsInstances (vehiculo.conductor, conductor):
			vehiculo.conductor = conductor
			vehiculo.save ()

		self.vehiculo = vehiculo
		self.save ()

	#-- Get or create, and save instance and flags if it was created or it has changed
	def getSaveUpdateInstance (self, instanceName, info):
		instance,  changeFlag = None, False
		try:
			if instanceName == "vehiculo":
				instance, createFlag = Vehiculo.objects.get_or_create (placa=info['placa'])
			elif instanceName == "conductor":
				instance, createFlag = Conductor.objects.get_or_create (documento=info['documento'])
			else:
				raise Exception (f"Tipo entidad '{instanceName}' no existe")

			for key in info.keys ():
				if getattr (instance, key) != info [key]:
					setattr (instance, key, info [key])
					changeFlag = True

			if createFlag or changeFlag:
				instance.save ()
		except:
			Utils.printException (f"Error con nombre de instancia '{instanceName}'")
		return instance, changeFlag


	#-- Get cartaporte from manifiesto info
	def getCartaporteInstance (self, manifiestoInfo):
		numeroCartaporte = None
		try:
			numeroCartaporte = manifiestoInfo.getNumeroCartaporte ()
			record = Cartaporte.objects.get (numero=numeroCartaporte)
			return record
		except: 
			Utils.printx (f"ALERTA: Cartaporte número '{numeroCartaporte}' no encontrado.")
			#Utils.printException ()
		return None

	#-- Get a 'conductor' instance from extracted info
	def getSaveConductorInstance (self, manifiestoInfo, vehicleType):
		try:
			info = manifiestoInfo.extractConductorInfo ()
			print (f"+++ DEBUG: info conductor '{info}'")
			if any (Utils.isEmptyFormField (text) for text in info.values()):
				return None
			else:
				conductor, created  = Conductor.objects.get_or_create (documento=info['id'])
				conductor.pais            = info ["pais"]
				conductor.tipoId          = info ["tipoId"]
				conductor.id              = info ["id"]
				conductor.sexo            = info ["sexo"]
				conductor.fecha_nacimiento = info ["fecha_nacimiento"]
				conductor.licencia        = info ["licencia"]
				conductor.save ()
				return conductor
		except:
			Utils.printException (f"Obteniedo información del vehiculo.")
			return None

	#-- Get a 'vehiculo' instance from extracted info
	def getSaveVehiculoInstance (self, manifiestoInfo, vehicleType):
		print ("+++ Tipo vehiculo:", vehicleType)
		try:
			info = manifiestoInfo.extractVehiculoInfo (vehicleType)
			if any (value is None for value in info.values()):
				return None
			else:
				vehiculo, createdFlag = Vehiculo.objects.get_or_create (placa=info['placa'])
				vehiculo.marca        = info ["marca"]
				vehiculo.placa        = info ["placa"]
				vehiculo.pais         = info ["pais"]
				vehiculo.chasis       = info ["chasis"]
				vehiculo.anho         = info ["anho"]
				vehiculo.certificado  = info ["certificado"]
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


