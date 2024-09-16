

# For views
from django.views import View
from django.shortcuts import render

# For forms
from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

# For tables
from datetime import datetime
from datetime import date

import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django_tables2.utils import A

# For models
from app_docs.listing_doc import DocumentosListadoView, DocTable, DocumentosListadoForm
from .models_mci import Manifiesto

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class ManifiestosListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Manifiestos", Manifiesto, DocumentosListadoForm, ManifiestosListadoTable)

#----------------------------------------------------------
# Table
#----------------------------------------------------------
class ManifiestosListadoTable (DocTable):
	#placa = tables.Column (accessor="documento.txt06", verbose_name="Placa") # To show related info
	class Meta:
		model         = Manifiesto
		urlDoc        = "manifiesto"
		fields        = ("numero", "fecha_emision", "vehiculo", "referencia", "acciones")
		template_name = DocTable.template
		attrs         = {'class': 'table table-striped table-bordered'}		



