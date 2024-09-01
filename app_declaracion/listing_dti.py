

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
from .models_dti import Declaracion

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class DeclaracionesListadoView (DocumentosListadoView):
    def __init__ (self):
        super().__init__ ("Declaraciones", Declaracion, DeclaracionesListadoForm, DeclaracionesListadoTable)

#class DeclaracionesListadoView (View):
#	def get (self, request):
#		pais		= request.session.get ("pais")
#		documentos  = Declaracion.objects.filter (pais=pais)
#		form		= DeclaracionesListadoForm (request.GET)
#		table		= None
#
#		if form.is_valid():
#			numero		  = form.cleaned_data.get('numero')
#			fecha_emision = form.cleaned_data.get('fecha_emision')
#			
#			if numero:
#				documentos = documentos.filter (numero__icontains=numero)
#			if fecha_emision:
#				documentos = documentos.filter (fecha_emision=fecha_emision)
#			else:
#				current_datetime = timezone.now()
#				documentos = documentos.filter (fecha_emision__lte=current_datetime).order_by ('-fecha_emision')
#
#			table = DeclaracionesTable (documentos)
#		else:
#			return ("Forma inválida")
#
#		return render(request, 'documento_listado.html',
#				   {'docsTipo': "Declaraciones", 'docsLista': documentos, 'docsForma': form, 'docsTabla': table})
#
#----------------------------------------------------------
#-- Forma
#----------------------------------------------------------
class DeclaracionesListadoForm (forms.Form):
	numero		   = forms.CharField(required=False)
	fecha_emision  = forms.DateField(required=False,
								  widget=forms.DateInput (attrs={'type':'date'}))
	#remitente		= forms.ModelChoiceField (queryset=Cliente.objects.all(), required=False)

	def __init__(self, *args, **kwargs):
		super (DeclaracionesListadoForm, self).__init__(*args, **kwargs)
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
class DeclaracionesListadoTable (DocTable):
	class Meta:
		model         = Declaracion
		template_name = DocTable.template
		fields        = ("numero", "fecha_emision", "acciones")
		urlActualizar = "declaracion-editar"
		attrs         = {'class': 'table table-striped table-bordered'}		

