from datetime import date

from django.db import models

from appusuarios.models import UsuarioEcuapass

#--------------------------------------------------------------------
# Model Cartaporte Document
#--------------------------------------------------------------------
class EcuapassDoc (models.Model):
	numero        = models.CharField (max_length=20)
	fecha_emision = models.DateField (default=date.today)
	procedimiento = models.CharField (max_length=30)
	usuario       = models.ForeignKey (UsuarioEcuapass, on_delete=models.SET_NULL, null=True)

	class Meta:
		abstract = True

	def __str__ (self):
		return f"{self.numero}, {self.fecha_emision}"

	#-- Delete related objects
	def delete(self, *args, **kwargs):
		print ("-- EcuapassDoc delete")
		DocumentClass = type (self.documento)
		DocumentClass.objects.filter (numero=self.numero).delete()
		super().delete(*args, **kwargs)	

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
		
