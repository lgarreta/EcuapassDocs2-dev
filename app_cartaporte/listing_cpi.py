# For models
from app_docs.listing_doc import DocumentosListadoView, DocTable, DocumentosListadoForm
from .models_cpi import Cartaporte

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class CartaportesListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Cartaportes", Cartaporte, DocumentosListadoForm, CartaportesListadoTable)

#----------------------------------------------------------
# Table
#----------------------------------------------------------
class CartaportesListadoTable (DocTable):
	class Meta:
		model         = Cartaporte
		urlDoc        = "cartaporte"
		fields        = ("numero", "fecha_emision", "remitente", "referencia", "acciones")
		template_name = DocTable.template
		attrs         = {'class': 'table table-striped table-bordered'}		

