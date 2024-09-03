
from django.urls import path

from app_manifiesto.views_ManifiestoDocView import *
from app_manifiesto import views_mci
from app_docs.views_Options import *
from app_docs import views_Filters 

from .listing_mci import ManifiestosListadoView

urlpatterns = [
	#-- URLs manifiesto -----------------------------------------------
    path("", ManifiestoDocView.as_view(), name="manifiesto"),
    path("nuevo/", ManifiestoDocView.as_view(), name="manifiesto-nuevo"),
    #path('listado/', views_Filters.manifiestosFilterView, name='manifiesto-listado'),
    path('listado/', ManifiestosListadoView.as_view(), name='manifiesto-listado'),

#	# Show autocomplete options
#    path('<pk>/opciones-cliente', ClienteOptionsView.as_view(), name='opciones-cliente'),
#	path('<pk>/opciones-lugar', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
#	path('<pk>/opciones-vehiculo', VehiculoOptionsView.as_view(), name='opciones-vehiculo'),
#	path('<pk>/opciones-conductor', ConductorOptionsView.as_view(), name='opciones-conductor'),
#	path('<pk>/opciones-cartaporte', CartaporteOptionsView.as_view(), name='opciones-cartaporte'),

	# Document options using <pk>
    path('detalle/<pk>', views_mci.ManifiestoDetailView.as_view(), name='manifiesto-detail'),
	path('editar/<int:pk>', ManifiestoDocView.as_view(), name='manifiesto-editar'),
	path('pdf_original/<int:pk>', ManifiestoDocView.as_view(), name='manifiesto-pdf_original'),
	path('pdf_copia/<int:pk>', ManifiestoDocView.as_view(), name='manifiesto-pdf_copia'),
	path('pdf_paquete/<int:pk>', ManifiestoDocView.as_view(), name='manifiesto-pdf_paquete'),
	path('clonar/<int:pk>', ManifiestoDocView.as_view(), name='manifiesto-clonar'),
	path('borrar/<int:pk>', views_mci.ManifiestoDelete.as_view(), name='manifiesto-delete'),

	# Update manifiesto with cartaporte and related info
	path('<pk>/actualizar-cartaporte/', views_mci.UpdateCartaporteView.as_view(), name='manifiesto-cartaporte')


	#OBSOLETE:
    #path('<pk>/', ManifiestoDocView.as_view(), name='manifiesto-documento'),
    #path('create/', views_mci.ManifiestoCreate.as_view(), name='manifiesto-create'),
    #path('comando', ManifiestoDocView.as_view(), name='manifiesto-comando'),
    #path('<pk>/update/', views_mci.ManifiestoUpdate.as_view(), name='manifiesto-update')
]

