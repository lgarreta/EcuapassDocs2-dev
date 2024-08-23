from datetime import date

from django.db import models

from app_usuarios.models import UsuarioEcuapass
from ecuapassdocs.info.ecuapass_utils import Utils 

#--------------------------------------------------------------------
# Model Cartaporte Document
#--------------------------------------------------------------------
class EcuapassDoc (models.Model):
	numero        = models.CharField (max_length=20)
	fecha_emision = models.DateField (default=date.today)
	pais          = models.CharField (max_length=30)
	usuario       = models.ForeignKey (UsuarioEcuapass, on_delete=models.SET_NULL, null=True)

	class Meta:
		abstract = True

	#-- Save by incrementing the last doc number in the DB
	def save (self, *args, **kwargs):
		if not self.numero:
			self.numero = self.generateDocNumber ()
		super().save (*args, **kwargs)

	#-- Generate doc number from last doc number saved in DB
	def generateDocNumber (self):
		lastDoc = self._meta.model.objects.filter (pais=self.pais).order_by ("-id").first ()
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
	def delete(self, *args, **kwargs):
		print ("-- EcuapassDoc delete")
		DocumentClass = type (self.documento)
		DocumentClass.objects.filter (numero=self.numero).delete()
		super().delete(*args, **kwargs)	

	#-- Return user instance by username
	def getUserByUsername (self, username):
		user = UsuarioEcuapass.objects.get (username=username)
		return user

#--------------------------------------------------------------------
# Model Cartaporte Form
#--------------------------------------------------------------------
class EcuapassForm (models.Model):
	numero = models.CharField (max_length=20)

#	def get_absolute_url(self):
#		"""Returns the url to access a particular language instance."""
#		#return reverse('empresa-detail', args=[str(self.id)])

	def __str__ (self):
		return f"{self.numero}, {self.txt02}, {self.txt03}"
	
	def getNumberFromId (self):
		numero = 2000000+ self.numero 
		numero = f"CI{numero}"
		return (self.numero)
		
