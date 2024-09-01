

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

# For test
from app_cartaporte.models_cpi import Cartaporte

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

	def get (self, request):
		pais	 = request.session.get ("pais")
		usuario  = request.session.get ("usuario")
		documentos  = self.DOCMODEL.objects.filter (pais=pais)
		form		= self.DOCFORM (request.GET)

		if form.is_valid():
			numero		  = form.cleaned_data.get('numero')
			fecha_emision = form.cleaned_data.get('fecha_emision')
			
			if numero:
				documentos = documentos.filter (numero__icontains=numero)
			if fecha_emision:
				documentos = documentos.filter (fecha_emision=fecha_emision)
			else:
				current_datetime = timezone.now()
				documentos = documentos.filter (fecha_emision__lte=current_datetime).order_by ('-fecha_emision')

			table = self.DOCTABLE (documentos)
		else:
			return ("Forma inválida")

		return render(request, 'documento_listado.html',
				   {'docsTipo': self.docsTipo, 'docsLista': documentos, 'docsForma': form, 'docsTabla': table})

##----------------------------------------------------------
## Base table for Ecuapass docs tables used in listing
##----------------------------------------------------------
class DocTable (tables.Table):
	template = "django_tables2/bootstrap4.html"

	class Meta:
		abstract = True

	#-- Define links for document table columns: numero, acciones (actualizar, eliminar)
	def __init__ (self, *args, **kwargs):
		super().__init__ (*args, **kwargs)
		urlActualizar                  = getattr (self.Meta, 'urlActualizar', 'default-url')
		self.base_columns ['numero']   = tables.LinkColumn (urlActualizar, args=[A('pk')])
		# Column for apply actions in the current item document
		self.base_columns ['acciones'] = tables.TemplateColumn(
			template_code='''
			(<a href="{{ record.get_link_actualizar }}">{{ record.get_link_actualizar_display }}</a>),
			(<a href="{{ record.get_link_eliminar }}">{{ record.get_link_eliminar_display }}</a>)
			''',
			verbose_name='Acciones'
		)

	#-- Create a link on doc number
	def render_numero (self, value, record):
		# Generate a URL for each record
		return format_html('<a href="{}" target="_blank" >{}</a>', reverse('cartaporte-editar', args=[record.pk]), value)

	#-- Change format to agree with form date format
	def render_fecha_emision(self, value):
		# Ensure value is a datetime object before formatting
		if isinstance(value, (datetime, (date, datetime))):
			return value.strftime('%m/%d/%Y')  # Format to 'dd/mm/yyyy'
		return ''

