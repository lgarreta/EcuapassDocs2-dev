"""
Base classes (View, Table) for listing ECUAPASS documents (Cartaporte, Manifiesto, Declaracion)

"""

# For views
from django.views import View
from django.shortcuts import render

# For forms
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

# For tables
import django_tables2 as tables
from django_tables2.utils import A

# For models
from app_docs.forms_docs import buscarForma
from .models_Entidades import Vehiculo, Conductor, Cliente

#----------------------------------------------------------
#-- View
#----------------------------------------------------------
class EntidadesListadoView (View):
	def __init__ (self, entityType, DOCMODEL, DOCTABLE):
		self.entityType = entityType
		self.DOCMODEL   = DOCMODEL
		self.DOCTABLE   = DOCTABLE
		self.DOCFORM    = buscarForma

	def get (self, request):
		form      = self.DOCFORM (request.GET)

		if form.is_valid():
			searchPattern = form.cleaned_data.get('buscar')
			if searchPattern:
				instances = self.DOCMODEL.searchModelAllFields (searchPattern)
			else:
				instances = self.DOCMODEL.objects.all ()

			table = self.DOCTABLE (instances)
		else:
			return ("Forma inválida")

		args =	{'itemsTipo':self.entityType, 'itemsLista': instances, 
				 'itemsForma': form, 'itemsTable': table}
		return render(request, 'app_docs/listing_entities.html', args)

##----------------------------------------------------------
## Base table used for listing Ecuapass docs 
##----------------------------------------------------------
class DocTable (tables.Table):
	class Meta:
		abstract      = True
		template_name = "django_tables2/bootstrap4.html"
		attrs         = {'class': 'table table-striped table-bordered'}		

	#-- Define links for document table columns: numero, acciones (actualizar, eliminar)
	def __init__ (self, urlDoc, *args, **kwargs):
		self.urlEditar            = f"{urlDoc}-editar"
		self.urlEliminar          = f"{urlDoc}-eliminar"

		# Column for apply actions in the current item document
		self.base_columns ['acciones'] = tables.TemplateColumn(
			template_code='''
			<a href="{{ record.get_link_editar }}">{{ 'Editar' }}</a>,
			<a href="{{ record.get_link_eliminar }}">{{ 'Eliminar' }}</a>
			''',
			verbose_name='Acciones'
		)
		super().__init__ (*args, **kwargs)

#----------------------------------------------------------
#-- Vehiculos listing
#----------------------------------------------------------
class VehiculosListadoView (EntidadesListadoView):
	def __init__(self):
		super().__init__ ("vehiculos", Vehiculo, VehiculosListadoTable)

class VehiculosListadoTable (DocTable):
	class Meta  (DocTable.Meta):
		model         = Vehiculo
		fields        = ("placa", "pais", "conductor", "acciones")

	def __init__ (self, *args, **kwargs):
		super().__init__ ("vehiculo", *args, **kwargs)
		self.urlEditarConductor = "conductor-editar"
		self.base_columns ['placa']      = tables.LinkColumn (self.urlEditar, args=[A('pk')])
		self.base_columns ['conductor']  = tables.LinkColumn (self.urlEditarConductor, args=[A('pk')])
		super().__init__ ("vehiculo", *args, **kwargs) # To redraw the table

#----------------------------------------------------------
#-- Conductores listing
#----------------------------------------------------------
class ConductoresListadoView (EntidadesListadoView):
	def __init__(self):
		super().__init__ ("conductores", Conductor, ConductoresListadoTable)

class ConductoresListadoTable (DocTable):
	class Meta (DocTable.Meta):
		model         = Conductor
		fields        = ("documento", "nombre", "pais", "acciones")

	def __init__ (self, *args, **kwargs):
		super().__init__ ("conductor", *args, **kwargs)
		self.urlEditarConductor = "conductor-editar"
		self.base_columns ['documento']  = tables.LinkColumn (self.urlEditar, args=[A('pk')])
		super().__init__ ("conductor", *args, **kwargs)   # To redraw the table

#----------------------------------------------------------
#-- Clientes listing
#----------------------------------------------------------
class ClientesListadoView (EntidadesListadoView):
	def __init__(self):
		super().__init__ ("clientes", Cliente, ClientesListadoTable)

class ClientesListadoTable (DocTable):
	class Meta (DocTable.Meta):
		model         = Cliente
		fields        = ("numeroId","nombre","ciudad","pais","direccion","acciones")

	def __init__ (self, *args, **kwargs):
		super().__init__ ("cliente", *args, **kwargs)
		self.urlEditarCliente = "cliente-editar"
		self.base_columns ['numeroId']  = tables.LinkColumn (self.urlEditar, args=[A('pk')])
		super().__init__ ("cliente", *args, **kwargs) # To redraw the table

