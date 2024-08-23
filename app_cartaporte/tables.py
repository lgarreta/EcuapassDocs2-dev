# tables.py
import django_tables2 as tables
from django_tables2.utils import A
from .models_cpi import Cartaporte

#----------------------------------------------------------
#----------------------------------------------------------
class CartaportesTable (tables.Table):
	class Meta:
		model = Cartaporte
		template_name = "django_tables2/bootstrap4.html"
		fields = ("numero", "fecha_emision", "remitente", "destinatario")

