
from django.urls import path

from app_cartaporte.views_CartaporteDocView import *
from app_cartaporte import views_cpi
from app_docs.views_Events import *
from app_docs import views_Filters 

from .listing_cpi import CartaportesListadoView

urlpatterns = [
	#-- URLs cartaporte -----------------------------------------------
    path("", CartaporteDocView.as_view(), name="cartaporte"),
    path("nuevo/", CartaporteDocView.as_view(), name="cartaporte-nuevo"),
    #path('listado/', views_Filters.cartaportesFilterView, name='cartaporte-listado'),
    path('listado/', CartaportesListadoView.as_view(), name='cartaporte-listado'),

	# Show autocomplete options
    path('<pk>/opciones-cliente', ClienteOptionsView.as_view(), name='opciones-cliente'),
    path('<pk>/opciones-lugar-fecha', CiudadPaisFechaOptionsView.as_view(), name='opciones-lugar-fecha'),
    path('<pk>/opciones-lugar', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),

	# Document options using <pk>
    path('detalle/<pk>', views_cpi.CartaporteDetailView.as_view(), name='cartaporte-detail'),
	path('editar/<int:pk>', CartaporteDocView.as_view(), name='cartaporte-editar'),
	path('pdf_original/<int:pk>', CartaporteDocView.as_view(), name='cartaporte-pdf_original'),
	path('pdf_copia/<int:pk>', CartaporteDocView.as_view(), name='cartaporte-pdf_copia'),
	path('pdf_paquete/<int:pk>', CartaporteDocView.as_view(), name='cartaporte-pdf_paquete'),
	path('clonar/<int:pk>', CartaporteDocView.as_view(), name='cartaporte-clonar'),
	path('borrar/<int:pk>', views_cpi.CartaporteDelete.as_view(), name='cartaporte-delete')
]

