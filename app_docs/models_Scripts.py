"""
Scripts for read/write models into DB
"""
from datetime import timedelta
from django.utils import timezone # For getting recent cartaportes

# For advance DB search on texts
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info import EcuInfo
from ecuapassdocs.info.ecuapass_data import EcuData

# For Cartaporte, Manifiesto, Declacion
import app_manifiesto
import app_cartaporte
import app_declaracion
#import app_cartaporte.models_cpi as models_cpi
#from app_manifiesto.models_mci import Manifiesto

from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza
from app_docs.models_Entidades import Cliente

#-------------------------------------------------------------------
#-- Generate doc number from last doc number saved in DB
#-------------------------------------------------------------------
def generateDocNumber (DocModel, pais):
	num_zeros = EcuData.configuracion ["num_zeros"]
	lastDoc   = DocModel.objects.filter (pais=pais).exclude (numero="SUGERIDO").order_by ("-id").first ()
	if lastDoc:
		lastNumber = Utils.getNumberFromDocNumber (lastDoc.numero)
		newNumber  = str (lastNumber + 1).zfill (num_zeros)
	else:
		newNumber  = str (1).zfill (num_zeros)

	docNumber = Utils.getCodigoPaisFromPais (pais) + newNumber
	return docNumber

#-------------------------------------------------------------------
# Return form document class and register class from document type
#-------------------------------------------------------------------
def getFormAndDocClass (docType):
	FormModel, DocModel = None, None
	if docType.upper() == "CARTAPORTE":
		FormModel, DocModel = app_cartaporte.models_cpi.CartaporteForm, app_cartaporte.models_cpi.Cartaporte
	elif docType.upper() == "MANIFIESTO":
		FormModel, DocModel = app_manifiesto.models_mci.ManifiestoForm, app_manifiesto.models_mci.Manifiesto
	elif docType.upper() == "DECLARACION":
		FormModel, DocModel = app_declaracion.models_dti.DeclaracionForm, app_declaracion.models_dti.Declaracion 
	else:
		print (f"Error: Tipo de documento '{docType}' no soportado")
		sys.exit (0)

	return FormModel, DocModel

#-------------------------------------------------------------------
# Search a pattern in all fields of a model
#-------------------------------------------------------------------
from django.db.models import Q
def searchModelAllFields (searchPattern, DOCMODEL):
    queries = Q()
    for field in DOCMODEL._meta.fields:
        field_name = field.name
        queries |= Q(**{f"{field_name}__icontains": searchPattern})
    
    results = DOCMODEL.objects.filter (queries)
    return results

#-------------------------------------------------------------------
#-- Get cartaporte instance
#-------------------------------------------------------------------
#-- Get cartaporte instance from DocFields
def getCartaporteInstanceFromDocFields (docFields, docType):
	cartaporteNumber = None
	try:
		cartaporteNumber = EcuInfo.getNumeroCartaporte (docFields, docType)
		cartaporte       = getCartaporteInstanceByNumero (cartaporteNumber)
		return cartaporte
	except: 
		Utils.printException (f"+++ ERROR: Obteniendo cartaporte número '{cartaporteNumber}'")
		return None


#-- Get cartaporte instance from number
def getCartaporteInstanceByNumero (cartaporteNumber):
	try:
		instance = app_cartaporte.models_cpi.Cartaporte.objects.get (numero=cartaporteNumber)
		return instance
	except app_cartaporte.models_cpi.Cartaporte.DoesNotExist:
		print (f"+++ No existe cartaporte nro: '{cartaporteNumber}'!")
	except app_cartaporte.models_cpi.Cartaporte.MultipleObjectsReturned:
		print (f"+++ Múltiples instancias de cartaporte nro: '{cartaporteNumber}'!")
	return None
#-------------------------------------------------------------------
#-- Get/Save cliente info. Only works for BYZA
#-- field keys correspond to: remitente, destinatario,... (Cartaporte)
#-------------------------------------------------------------------
def getSaveClienteInstance (docKey, docFields):
	clienteInfo  = getClienteInfo (docKey, docFields)
	if clienteInfo:
		cliente = saveClienteInfoToDB (clienteInfo)
		return cliente
	else:
		return None

#-- Get cliente info from full doc fields
def getClienteInfo (docKey, docFields):
	info = None
	try:
		jsonFieldsPath, runningDir = Utils.createTemporalJson (docFields)
		cartaporteInfo    = CartaporteByza (jsonFieldsPath, runningDir)
		info              = cartaporteInfo.getSubjectInfo (docKey)
		print ("-- Subject info:", info)

		if any (value is None for value in info.values()) or \
		   any ("||LOW" in value for value in info.values()):
			return None
	except:
		Utils.printException (f"Obteniedo info de cliente tipo: '{docKey}'")

	return info

#-- Get cleinte instance from DB by numeroId
def getClienteInstanceByNumeroId (numeroId):
	try:
		instance = Cliente.objects.get (numeroId=numeroId)
		return (instance)
	except Cliente.DoesNotExist:
		print (f"Cliente no encontrado con numeroId: '{numeroId}'")
		return None

#-- Get cleinte instance from DB by nombre
def getClienteInstanceByNombre (nombre):
	try:
		#instance = Cliente.objects.get (nombre=nombre)

		results = (
			Cliente.objects
			.annotate (similarity=TrigramSimilarity ('nombre', nombre))
			.filter (similarity__gt=0.3)  # Threshold for similarity
			.order_by ('-similarity')  # Optional: sort by most similar
		)
		if not results:
			return None
		else:
			return (results [0])
	except Cliente.DoesNotExist:
		print (f"Cliente no encontrado con nombre: '{nombre}'")
		return None


#-- Save instance of Cliente with info: id, nombre, direccion, ciudad, pais, tipoId, numeroId
def saveClienteInfoToDB (info):
	cliente = None
	try:
		cliente, created = Cliente.objects.get_or_create (numeroId=info['numeroId'])

		cliente.nombre    = info ["nombre"]
		cliente.direccion = info ["direccion"]
		cliente.ciudad    = info ["ciudad"]
		cliente.pais      = info ["pais"]
		cliente.tipoId    = info ["tipoId"]
		cliente.numeroId  = info ["numeroId"]

		cliente.save ()
	except:
		Utils.printException (f"Guardando cliente to DB")
	return cliente

##----------------------------------------------------------
## ------------------ Functions in models_mci -------------
##----------------------------------------------------------
##----------------------------------------------------------
## Get / Save Vehiculo info from docFields (formFields)
##----------------------------------------------------------
#def getSaveVehiculoInstance (docKey, docFields):
#	vehiculoInfo  = getVehiculoInfo (docKey, docFields)
#	if vehiculoInfo:
#		vehiculo = saveVehiculoInfo (vehiculoInfo)
#		return vehiculo
#	else:
#		return None
#
##-- Get a 'vehiculo' instance from extracted info
#def getVehiculoInfo (self, manifiestoInfo, vehicleType):
#	vehinfo = None
#	print ("+++ Tipo vehiculo:", vehicleType)
#	try:
#		jsonFieldsPath, runningDir = Utils.createTemporalJson (docFields)
#		manifiestoInfo  = ManifiestoInfo (jsonFieldsPath, runningDir)
#		vehinfo         = manifiestoInfo.extractVehiculoInfo (vehicleType)
#		if any (value is None for value in vehinfo.values()):
#			return None
#	except:
#		Utils.printException (f"Obteniedo info de cliente tipo: '{docKey}'")
#	return vehinfo
#
##-- Save instance of Vehiculo 
#def saveVehiculoInfo (vehinfo):
#	vehiculo = None
#	try:
#		vehiculo, created    = Vehiculo.objects.get_or_create (placa=vehinfo['placa'])
#		vehiculo.marca       = vehinfo ["marca"]
#		vehiculo.placa       = vehinfo ["placa"]
#		vehiculo.pais        = vehinfo ["pais"]
#		vehiculo.chasis      = vehinfo ["chasis"]
#		vehiculo.anho        = vehinfo ["anho"]
#		vehiculo.certificado = vehinfo ["certificado"]
#		vehiculo.save ()
#	except:
#		Utils.printException (f"Obteniedo información del vehiculo.")
#	return vehiculo
#

#----------------------------------------------------------
#-- Return recent cartaportes (within the past week)
#----------------------------------------------------------
def getRecentDocuments (DOCMODEL, days):
	diasRecientes = EcuData.configuracion ["dias_cartaportes_recientes"] + days
	daysAgo = timezone.now () - timedelta (days=diasRecientes)
	recentDocuments = DOCMODEL.objects.filter (fecha_emision__gte=daysAgo)
	if not recentDocuments.exists():
		print (f"+++ No existen documentos de más de '{days}' dias")

	return recentDocuments

#----------------------------------------------------------
#-- Compare whether two instances have the same values for all fields,
#----------------------------------------------------------
def areEqualsInstances (instance1, instance2):
	try:
		if instance1 is None and instance2 is None:
			return True  # Equals
		elif instance1 is None or instance2 is None:
			return False # Different

		if instance1._meta.model != instance2._meta.model:
			return False  # They are not even the same model

		# Compare field values
		for field in instance1._meta.fields:
			value1 = getattr(instance1, field.name)
			value2 = getattr(instance2, field.name)
			if value1 != value2:
				return False  # Return False if any field value is different

		return True  # All fields match
	except:
		return False


