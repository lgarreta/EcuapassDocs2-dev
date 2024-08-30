

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
from app_docs.listing_doc import DocumentosListadoView
from .models_cpi import Cartaporte

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class CartaportesListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Cartaportes", Cartaporte, CartaportesListadoForm, CartaportesListadoTable)

#----------------------------------------------------------
#-- Forma
#----------------------------------------------------------
class CartaportesListadoForm (forms.Form):
	numero		   = forms.CharField(required=False)
	fecha_emision  = forms.DateField(required=False,
								  widget=forms.DateInput (attrs={'type':'date'}))
	#remitente		= forms.ModelChoiceField (queryset=Cliente.objects.all(), required=False)

	def __init__(self, *args, **kwargs):
		super (CartaportesListadoForm, self).__init__(*args, **kwargs)
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
class CartaportesListadoTable (tables.Table):
	class Meta:
		model = Cartaporte
		template_name = "django_tables2/bootstrap4.html"
		fields = ("numero", "fecha_emision", "remitente", "destinatario")

	#-- Create a link on doc number
	def render_numero (self, value, record):
		# Generate a URL for each record
		return format_html('<a href="{}" target="_blank">{}</a>', reverse('cartaporte-editar', args=[record.pk]), value)

	#-- Change format to agree with form date format
	def render_fecha_emision(self, value):
		# Ensure value is a datetime object before formatting
		if isinstance(value, (datetime, (date, datetime))):
			return value.strftime('%m/%d/%Y')  # Format to 'dd/mm/yyyy'
		return ''

