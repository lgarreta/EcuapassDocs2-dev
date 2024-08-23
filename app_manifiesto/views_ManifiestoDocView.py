from django.urls import resolve   # To get calling URLs

# Own imports
from ecuapassdocs.info.resourceloader import ResourceLoader 
from appdocs.views_EcuapassDocView import EcuapassDocView

#--------------------------------------------------------------------
#-- Vista para manejar las solicitudes de manifiesto
#--------------------------------------------------------------------
class ManifiestoDocView (EcuapassDocView):
	docType    = "MANIFIESTO"
	background_image = "appdocs/images/image-manifiesto-vacio-NTA-BYZA.png"
	parameters_file  = "manifiesto_input_parameters.json"

	def __init__(self, *args, **kwargs):
		super().__init__ (self.docType, self.background_image, 
		                  self.parameters_file, *args, **kwargs)

	#-- Set constant values for the BYZA company
	def initDocumentValues (self, request):
		super ().initDocumentValues (request)

		# Permisos values for BYZA 
		self.inputParams ["txt02"]["value"] = "PO-CO-0033-22"
		self.inputParams ["txt03"]["value"] = "PO-CO-0033-22"

		# Aduanas cruce/destino
		#urlName = resolve(request.path_info).url_name
		aduanaCruce,  aduanaDestino = "", ""
		#if "importacion" in urlName:
		if self.pais == "COLOMBIA":
			aduanaCruce   = "IPIALES-COLOMBIA"
			aduanaDestino = "TULCAN-ECUADOR"
		elif self.pais == "ECUADOR":
			aduanaCruce   = "TULCAN-ECUADOR"
			aduanaDestino = "IPIALES-COLOMBIA"
		else:
			print (f"Alerta: No se pudo determinar aduana cruce/destino desde país: '{self.pais}'")
		self.inputParams ["txt37"]["value"] = aduanaCruce
		self.inputParams ["txt38"]["value"] = aduanaDestino


