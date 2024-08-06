
import re
from datetime import date

# Own imports
from ecuapassdocs.info.resourceloader import ResourceLoader 
from appdocs.views_EcuapassDocView import EcuapassDocView

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de cartaporte
#--------------------------------------------------------------------
class CartaporteDocView (EcuapassDocView):
	document_type    = "CARTAPORTE"
	template_name    = "forma_documento.html"
	background_image = "appdocs/images/image-cartaporte-vacia-SILOG-BYZA.png"
	parameters_file  = "cartaporte_input_parameters.json"

	def __init__(self, *args, **kwargs):
		self.inputParameters = ResourceLoader.loadJson ("docs", self.parameters_file)
		super().__init__ (self.document_type, self.template_name, self.background_image, 
		                  self.parameters_file, self.inputParameters, *args, **kwargs)
	
	#----------------------------------------------------------------
	#-- Info is embedded according to Azure format
	#----------------------------------------------------------------
	def getFieldValuesFromBounds (self, inputValues):
		jsonFieldsDic = {}
		gastosDic = {"value": {"ValorFlete":{"value":{}}, 
		                       "Seguro":{"value":{}}, 
							   "OtrosGastos":{"value":{}}, 
							   "Total":{"value":{}}}}

		# Load parameters from package
		cartaporteParametersForInputs = ResourceLoader.loadJson ("docs", self.parameters_file)

		for key, params in cartaporteParametersForInputs.items():
			fieldName    = params ["ecudocsField"]
			value        = inputValues [key]
			if "Gastos" in fieldName:
				res = re.findall ("\w+", fieldName)   #e.g ["ValorFlete", "MontoDestinatario"]
				tableName, rowName, colName = res [0], res [1], res[2]
				if value != "":
					gastosDic ["value"][rowName]["value"][colName] = {"value": value, "content": value}
			else:
				jsonFieldsDic [fieldName] = {"value": value, "content": value}

		jsonFieldsDic [tableName] = gastosDic
		return jsonFieldsDic

