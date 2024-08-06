
from django.urls import path

from appdocs import views
from appdocs.views import InfoView
from appdocs.views_CartaporteDocView import *
from appdocs.views_Entidades import *
from appdocs import views_Filters 

#from .views_ManifiestoDocView import *
#from .views_DeclaracionDocView import *

#from .views_ComandosView import *

#app_name = "appdocs"

urlpatterns = [
	#-- URLs cartaporte -----------------------------------------------
    path("", CartaporteDocView.as_view(), name="cartaporte"),
    path("nuevo/", CartaporteDocView.as_view(), name="cartaporte-nuevo"),
    path("exportacion", CartaporteDocView.as_view(), name="cartaporte-exportacion"),

	# Show autocomplete options
    path('opciones-empresa/', EmpresaOptionsView.as_view(), name='opciones-empresa'),
    path('editar/opciones-empresa/', EmpresaOptionsView.as_view(), name='opciones-empresa'),
    path('opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
    path('<pk>/editar/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
    path('opciones-lugar-fecha/', CiudadPaisFechaOptionsView.as_view(), name='opciones-lugar-fecha'),
    path('<pk>/editar/opciones-lugar-fecha/', CiudadPaisFechaOptionsView.as_view(), name='opciones-lugar-fecha'),

    path('<pk>/', CartaporteDocView.as_view(), name='cartaporte-documento'),

    path('listado', views_Filters.cartaportesFilterView, name='cartaportes_filter'),
    path('detalle/<pk>', views.CartaporteDetailView.as_view(), name='cartaporte-detail'),
    path('create/', views.CartaporteCreate.as_view(), name='cartaporte-create'),
    path('editar/<pk>', CartaporteDocView.as_view(), name='cartaporte-editar'),
    path('pdf_original/<pk>', CartaporteDocView.as_view(), name='cartaporte-pdf_original'),
    path('pdf_copia/<pk>', CartaporteDocView.as_view(), name='cartaporte-pdf_copia'),
    path('pdf_paquete/<pk>', CartaporteDocView.as_view(), name='cartaporte-pdf_paquete'),
    path('clonar/<pk>', CartaporteDocView.as_view(), name='cartaporte-clonar'),
    path('comando', CartaporteDocView.as_view(), name='cartaporte-comando'),
    path('<pk>/update/', views.CartaporteUpdate.as_view(), name='cartaporte-update'),
    path('borrar/<pk>', views.CartaporteDelete.as_view(), name='cartaporte-delete')
]

