# For models
from app_docs.listing_doc import DocumentosListadoView, DocTable, DocumentosListadoForm
from .models_dti import Declaracion

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class DeclaracionesListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Declaraciones", Declaracion, DocumentosListadoForm, DeclaracionesListadoTable)

#----------------------------------------------------------
# Table
#----------------------------------------------------------
class DeclaracionesListadoTable (DocTable):
	class Meta:
		model         = Declaracion
		urlDoc        = "declaracion"
		fields        = ("numero", "fecha_emision", "acciones")
		template_name = DocTable.template
		attrs         = {'class': 'table table-striped table-bordered'}		

