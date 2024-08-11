from django.urls import resolve   # To get calling URLs

# Own imports
from ecuapassdocs.info.resourceloader import ResourceLoader 
from appdocs.views_EcuapassDocView import EcuapassDocView

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de manifiesto
#--------------------------------------------------------------------
class ManifiestoDocView (EcuapassDocView):
	document_type    = "MANIFIESTO"
	template_name    = "forma_documento.html"
	background_image = "appdocs/images/image-manifiesto-vacio-NTA-BYZA.png"
	parameters_file  = "manifiesto_input_parameters.json"

	def __init__(self, *args, **kwargs):
		self.inputParameters = ResourceLoader.loadJson ("docs", self.parameters_file)
		super().__init__ (self.document_type, self.template_name, self.background_image, 
		                  self.parameters_file, self.inputParameters, *args, **kwargs)

	#-- Set constant values for the BYZA company
	def setInitialValuesToInputs (self, requestParams):
		super ().setInitialValuesToInputs (requestParams)

		# Permisos values for BYZA 
		self.inputParameters ["txt02"]["value"] = "PO-CO-0033-22"
		self.inputParameters ["txt03"]["value"] = "PO-CO-0033-22"

		# Aduanas cruce/destino
		pais = requestParams ["pais"]
		#urlName = resolve(request.path_info).url_name
		aduanaCruce,  aduanaDestino = "", ""
		#if "importacion" in urlName:
		if pais == "CO":
			aduanaCruce   = "IPIALES-COLOMBIA"
			aduanaDestino = "TULCAN-ECUADOR"
		elif pais == "EC":
			aduanaCruce   = "TULCAN-ECUADOR"
			aduanaDestino = "IPIALES-COLOMBIA"
		else:
			print (f"Alerta: No se pudo determinar aduana cruce/destino desde país: '{pais}'")
		self.inputParameters ["txt37"]["value"] = aduanaCruce
		self.inputParameters ["txt38"]["value"] = aduanaDestino


