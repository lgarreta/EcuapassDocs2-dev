"""
Scripts for read/write models into DB
"""
from datetime import timedelta
from django.utils import timezone # For getting recent cartaportes

from ecuapassdocs.info.ecuapass_utils import Utils
from ecuapassdocs.info.ecuapass_info import EcuInfo
from ecuapassdocs.info.ecuapass_data import EcuData
import app_cartaporte.models_cpi as cpiModels
from ecuapassdocs.info.ecuapass_info_cartaporte_BYZA import CartaporteByza
from app_docs.models_Entidades import Cliente

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
# Get cartaporte from doc fields and save to DB
#-------------------------------------------------------------------
def getCartaporteInstance (docKey, docFields, docType):
	cartaporte = None
	try:
		cartaporteNumber    = EcuInfo.getNumeroCartaporte (docFields, docType)
		print (f"+++ DEBUG: getCartaporteInstance:cartaporteNumber '{cartaporteNumber}'")
		
		cartaporte = cpiModels.Cartaporte.objects.get (numero=cartaporteNumber)
		return cartaporte
	except cpiModels.Cartaporte.DoesNotExist:
		Utils.printException (f"No existe cartaporte nro: '{cartaporteNumber}'!")
	except cpiModels.Cartaporte.MultipleObjectsReturned:
		Utils.printException (f"Múltiples instancias de cartaporte nro: '{cartaporteNumber}'!")
	return cartaporte
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


#-- Return recent cartaportes (within the past week)
def getRecentDocuments (DOCMODEL):
	diasRecientes = EcuData.configuracion ["dias_cartaportes_recientes"]
	oneWeekAgo = timezone.now () - timedelta (days=diasRecientes)
	recentDocuments = DOCMODEL.objects.filter (fecha_emision__gte=oneWeekAgo)
	for doc in recentDocuments:
		print (doc.numero, doc.fecha_emision)
	return recentDocuments

