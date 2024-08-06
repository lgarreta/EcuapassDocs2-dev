"""
Conatins all general entities (models) used by the three ECUAPASS documents
"""

from django.db import models
from django.urls import reverse  # To generate URLS by reversing URL patterns

#--------------------------------------------------------------------
# Model Empresa
#--------------------------------------------------------------------
class Empresa (models.Model):
	numeroId     = models.CharField (max_length=30)
	nombre       = models.CharField (max_length=50)
	direccion    = models.CharField (max_length=100)
	ciudad       = models.CharField (max_length=50)
	pais         = models.CharField (max_length=20)
	tipoId       = models.CharField (max_length=20)

	def get_absolute_url(self):
		"""Returns the url to access a particular language instance."""
		return reverse('empresa-detail', args=[str(self.id)])

	def __str__ (self):
		return f"{self.nombre} {self.ciudad}-{self.pais}"
	
#--------------------------------------------------------------------
# Model Conductor
#--------------------------------------------------------------------
class Conductor (models.Model):
	documento        = models.CharField (max_length=20)
	nombre           = models.CharField (max_length=50)
	nacionalidad     = models.CharField (max_length=50)
	licencia         = models.CharField (max_length=50)
	fecha_nacimiento = models.CharField (max_length=50)

	class Meta:
		verbose_name_plural = "Conductores"

	def get_absolute_url(self):
		"""Returns the url to access a particular genre instance."""
		return reverse('conductor-detail', args=[str(self.id)])

	def __str__ (self):
		return f"{self.nombre}"

#--------------------------------------------------------------------
# Model Vehiculo
#--------------------------------------------------------------------
class Vehiculo (models.Model):
	placa       = models.CharField (max_length=50)
	marca       = models.CharField (max_length=100)
	pais        = models.CharField (max_length=20)
	chasis      = models.CharField (max_length=50)
	anho        = models.CharField (max_length=20)

	def get_absolute_url(self):
		"""Returns the url to access a particular language instance."""
		return reverse('vehiculo-detail', args=[str(self.id)])

	def __str__ (self):
		return f"{self.marca}, {self.placa}, {self.pais}"
	
