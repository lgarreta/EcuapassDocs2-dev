

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
from app_docs.listing_doc import DocumentosListadoView, DocTable
from .models_mci import Manifiesto

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class ManifiestosListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Manifiestos", Manifiesto, ManifiestosListadoForm, ManifiestosListadoTable)

#----------------------------------------------------------
#-- Forma
#----------------------------------------------------------
class ManifiestosListadoForm (forms.Form):
	numero		   = forms.CharField(required=False)
	fecha_emision  = forms.DateField(required=False,
								  widget=forms.DateInput (attrs={'type':'date'}))
	#remitente		= forms.ModelChoiceField (queryset=Cliente.objects.all(), required=False)

	def __init__(self, *args, **kwargs):
		super (ManifiestosListadoForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'GET'
		self.helper.layout = Layout(
			Row (
				Column ('numero', css_class='col'),
				Column ('fecha_emision', css_class='col'),
				css_class='row'
			),
			Submit ('submit', 'Filtrar', css_class='btn btn-primary')
		)

#----------------------------------------------------------
# Table
#----------------------------------------------------------
class ManifiestosListadoTable (DocTable):
	class Meta:
		model         = Manifiesto
		urlActualizar = "manifiesto-editar"
		fields        = ("numero", "fecha_emision", "acciones")
		template_name = DocTable.template
		attrs         = {'class': 'table table-striped table-bordered'}		

