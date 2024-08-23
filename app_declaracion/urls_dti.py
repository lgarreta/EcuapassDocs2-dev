from django.urls import path

from app_declaracion.views_DeclaracionDocView import *
from app_declaracion import views_dti
from appdocs.views_Events import *
from appdocs import views_Filters 

urlpatterns = [
	#-- URLs declaracion -----------------------------------------------
    path("", DeclaracionDocView.as_view(), name="declaracion"),
    path("nuevo/", DeclaracionDocView.as_view(), name="declaracion-nuevo"),
    path('listado/', views_Filters.declaracionesFilterView, name='declaracion-listado'),

	# Show autocomplete options
	path('<pk>/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
	path('<pk>/opciones-vehiculo/', VehiculoOptionsView.as_view(), name='opciones-vehiculo'),
	path('<pk>/opciones-conductor/', ConductorOptionsView.as_view(), name='opciones-conductor'),
	path('<pk>/opciones-cartaporte/', CartaporteOptionsView.as_view(), name='opciones-cartaporte'),

	# Document options using <pk>
    path('detalle/<pk>', views_dti.DeclaracionDetailView.as_view(), name='declaracion-detail'),
	path('editar/<int:pk>', DeclaracionDocView.as_view(), name='declaracion-editar'),
	path('pdf_original/<int:pk>', DeclaracionDocView.as_view(), name='declaracion-pdf_original'),
	path('pdf_copia/<int:pk>', DeclaracionDocView.as_view(), name='declaracion-pdf_copia'),
	path('pdf_paquete/<int:pk>', DeclaracionDocView.as_view(), name='declaracion-pdf_paquete'),
	path('clonar/<int:pk>', DeclaracionDocView.as_view(), name='declaracion-clonar'),
	path('borrar/<int:pk>', views_dti.DeclaracionDelete.as_view(), name='declaracion-delete')

]

