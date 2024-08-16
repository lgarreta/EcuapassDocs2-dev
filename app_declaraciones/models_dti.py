import os, tempfile, json
from datetime import date

from django.db import models
from django.urls import reverse  # To generate URLS by reversing URL patterns

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info_manifiesto_BYZA import ManifiestoByza

from appdocs.models import EcuapassDoc, Cartaporte

from appusuarios.models import UsuarioEcuapass
from appdocs.models_Entidades import Empresa, Conductor, Vehiculo
from appdocs.models_EcuapassDoc import EcuapassDoc

#--------------------------------------------------------------------
# Model DeclaracionDoc
#--------------------------------------------------------------------
class DeclaracionDoc (models.Model):
	class Meta:
		db_table = "declaraciondoc"

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
	txt10 = models.CharField (max_length=200, null=True)
	txt11 = models.CharField (max_length=200, null=True)
	txt12 = models.CharField (max_length=200, null=True)
	txt13 = models.CharField (max_length=200, null=True)
	txt14 = models.CharField (max_length=200, null=True)
	#-- Informacion mercancia
	txt15 = models.CharField (max_length=200, null=True)    # Cartaporte
	txt16 = models.CharField (max_length=800, null=True)    # Descripción
	txt17 = models.CharField (max_length=200, null=True)    # Cantidad Bultos
	txt18 = models.CharField (max_length=200, null=True)    # Embalaje/Marcas
	txt19_1 = models.CharField (max_length=200, null=True)  # Peso bruto
	txt19_2 = models.CharField (max_length=200, null=True)  # Peso bruto total
	txt19_3 = models.CharField (max_length=200, null=True)  # Peso neto
	txt19_4 = models.CharField (max_length=200, null=True)  # Peso neto total
	txt20_1 = models.CharField (max_length=200, null=True)  # Otra medida
	txt20_2 = models.CharField (max_length=200, null=True)  # Otra medida total
	txt21 = models.CharField (max_length=200, null=True)    # INCOTERM
	txt22 = models.CharField (max_length=200, null=True)
	txt23 = models.CharField (max_length=200, null=True)
	txt24 = models.CharField (max_length=200, null=True)
	txt25 = models.CharField (max_length=200, null=True)
	txt26 = models.CharField (max_length=200, null=True)

	def __str__ (self):
		return f"{self.numero}, {self.txt03}"
	
#--------------------------------------------------------------------
# Model Declaracion
#--------------------------------------------------------------------
class Declaracion (EcuapassDoc):
	class Meta:
		db_table = "declaracion"

	documento     = models.OneToOneField (DeclaracionDoc, on_delete=models.SET_NULL, null=True)

	cartaporte    = models.ForeignKey (Cartaporte, on_delete=models.SET_NULL, null=True)

	def get_absolute_url(self):
		"""Returns the url to access a particular language instance."""
		return reverse('declaracion-detail', args=[str(self.id)])

	def __str__ (self):
		return f"{self.numero}, {self.cartaporte}"

	def setValues (self, declaracionDoc, docFields, procedimiento, username):
		# Base values
		self.numero        = declaracionDoc.numero
		self.documento     = declaracionDoc
		self.procedimiento = procedimiento
		self.usuario       = self.getUserByUsername (username)

		# Document values
		jsonFieldsPath, runningDir = self.createTemporalJson (docFields)
		declaracionInfo            = Declaracion (jsonFieldsPath, runningDir)

		self.cartaporte = self.getCartaporte (declaracionInfo)
		
	def getCartaporte (self, declaracionInfo):
		numero = None
		try:
			numero = declaracionInfo.getNroDocumento ()
			record = Cartaporte.objects.get (numero=desired_value)
			return record
		except: 
			print (f"Exepcion: Cartaporte número '{numero}' no encontrado.")
		return None

	def createTemporalJson (self, fieldValues):
		tmpPath        = tempfile.gettempdir ()
		jsonFieldsPath = os.path.join (tmpPath, f"MANIFIESTO-{self.numero}.json")
		json.dump (fieldValues, open (jsonFieldsPath, "w"))
		return (jsonFieldsPath, tmpPath)

