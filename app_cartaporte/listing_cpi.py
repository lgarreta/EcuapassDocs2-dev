# For models
from app_docs.forms_docs import BuscarDocForm
from app_docs.listing_doc import DocumentosListadoView, DocumentosListadoTable
from .models_cpi import Cartaporte

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class CartaportesListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Cartaportes", Cartaporte, BuscarDocForm, CartaportesListadoTable)

#----------------------------------------------------------
# Table
#----------------------------------------------------------
class CartaportesListadoTable (DocumentosListadoTable):
	class Meta:
		model         = Cartaporte
		urlDoc        = "cartaporte"
		fields        = ("row_number", "numero", "fecha_emision", "remitente", "referencia", "acciones")
		template_name = DocumentosListadoTable.template
		attrs         = {'class': 'table table-striped table-bordered'}		

