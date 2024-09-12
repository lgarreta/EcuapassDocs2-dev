"""
Global forms
"""

# For forms
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

#----------------------------------------------------------
#-- Forma with "Buscar" field
#----------------------------------------------------------
class buscarForma (forms.Form):
	buscar = forms.CharField(required=False,label="")

	def __init__(self, *args, **kwargs):
		super ().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'GET'
		self.helper.layout = Layout(
			Row (
				Column(Field('buscar', placeholder="Digite texto a buscar...", label=False), css_class='search_field'),
				Column (Submit ('submit', 'Buscar'), css_class='search_button'),
				css_class='form-row'
			)
		)

