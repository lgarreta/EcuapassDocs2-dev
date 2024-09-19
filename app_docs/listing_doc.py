"""
Base classes (View, Table) for listing ECUAPASS documents (Cartaporte, Manifiesto, Declaracion)

"""

# For views
from django.views import View
from django.shortcuts import render

# For forms
from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

# For tables
from datetime import datetime
from datetime import date

import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django_tables2.utils import A

from .models_EcuapassDoc import EcuapassDoc

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class DocumentosListadoView (View):
	def __init__ (self, docsTipo, DOCMODEL, DOCFORM, DOCTABLE):
		self.pais	   = None
		self.usuario   = None
		self.docsTipo  = docsTipo
		self.DOCMODEL  = DOCMODEL
		self.DOCFORM   = DOCFORM 
		self.DOCTABLE  = DOCTABLE

	# General and date search
	def get (self, request):
		form      = self.DOCFORM (request.GET)

		if form.is_valid():
			searchPattern = form.cleaned_data.get('buscar')
			if searchPattern:
				object    = self.DOCMODEL()
				instances = object.searchModelAllFields (searchPattern)
			else:
				firstField = self.DOCMODEL._meta.fields [1].name
				print (f"+++ DEBUG: firstField '{firstField}'")
				instances = self.DOCMODEL.objects.order_by (f"-{firstField}")
				#instances = self.DOCMODEL.objects.all ()

			table = self.DOCTABLE (instances)
		else:
			return ("Forma inválida")

		args =	{'itemsTipo':self.docsTipo, 'itemsLista': instances, 
				 'itemsForma': form, 'itemsTable': table}
		return render(request, 'app_docs/listing_entities.html', args)

#----------------------------------------------------------
#-- Forma
#----------------------------------------------------------
class DocumentosListadoForm (forms.Form):
	#numero		   = forms.CharField(required=False)
	buscar = forms.CharField(required=False,label="")
	fecha_emision  = forms.DateField(required=False, label=False,
								  widget=forms.DateInput (attrs={'type':'date'}))

	def __init__(self, *args, **kwargs):
		super ().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'GET'
		self.helper.layout = Layout(
			Row (
				Column(Field('buscar', placeholder="Digite texto a buscar...", label=False), css_class='search_field'),
				Column (Field ('fecha_emision', placeholder="Seleccione fecha a buscar...", label=False), css_class='search_field'),
				Column (Submit ('submit', 'Buscar'), css_class='search_button'),
				css_class='form-row'
				#Column ('numero', css_class='col'),
				#Column ('fecha_emision', css_class='col'),
				#css_class='row'
			)
			#Submit ('submit', 'Filtrar', css_class='btn btn-primary')
		)

##----------------------------------------------------------
## Base table used for listing Ecuapass docs 
##----------------------------------------------------------
class DocTable (tables.Table):
	template = "django_tables2/bootstrap4.html"
	fecha_emision = tables.Column (verbose_name="Fecha") # To show related info

	class Meta:
		abstract = True

	#-- Define links for document table columns: numero, acciones (actualizar, eliminar)
	def __init__ (self, *args, **kwargs):
		self.urlDoc               = getattr (self.Meta, 'urlDoc', 'default-url')
		self.urlEditar            = f"{self.urlDoc}-editar"
		self.urlDetalle           = f"{self.urlDoc}-detalle"

		self.base_columns ['numero']  = tables.LinkColumn (self.urlEditar, args=[A('pk')])
		# Column for apply actions in the current item document
		self.base_columns ['acciones'] = tables.TemplateColumn(
			template_code='''
			<a href="{{ record.get_link_actualizar }}" target='_blank'>Editar</a>,
			<a href="{{ record.get_link_eliminar }}" target='_blank'>Eliminar</a>
			''',
			verbose_name='Acciones'
		)
		super().__init__ (*args, **kwargs)

	#-- Create a link on doc number
	def render_numero (self, value, record):
		# Generate a URL for each record
		return format_html('<a href="{}" target="_blank" >{}</a>', 
					 reverse(self.urlEditar, args=[record.pk]), value)

	#-- Change format to agree with form date format
	def render_fecha_emision(self, value):
		# Ensure value is a datetime object before formatting
		if isinstance(value, (datetime, (date, datetime))):
			return value.strftime('%m/%d/%Y')  # Format to 'dd/mm/yyyy'
		return ''

