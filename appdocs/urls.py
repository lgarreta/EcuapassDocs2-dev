from django.urls import path

from . import views
from . import views_Filters

from .views import InfoView

from .views_CartaporteDocView import *
from .views_ManifiestoDocView import *
from .views_DeclaracionDocView import *
from .views_Entidades import *

from .views_ComandosView import *

#app_name = "appdocs"

urlpatterns = [
    path('', views.index, name='index'),

	#-- URLs cartaporte -----------------------------------------------
#    path("cartaporte/", CartaporteDocView.as_view(), name="cartaporte"),
#    path("cartaporte/importacion", CartaporteDocView.as_view(), name="cartaporte-importacion"),
#    path("cartaporte/exportacion", CartaporteDocView.as_view(), name="cartaporte-exportacion"),
#
#    path('cartaporte/opciones-empresa/', EmpresaOptionsView.as_view(), name='opciones-empresa'),
#    path('cartaporte/<pk>/opciones-empresa/', EmpresaOptionsView.as_view(), name='opciones-empresa'),
#    path('cartaporte/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
#    path('cartaporte/<pk>/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
#    path('cartaporte/opciones-lugar-fecha/', CiudadPaisFechaOptionsView.as_view(), name='opciones-lugar-fecha'),
#    path('cartaporte/<pk>/opciones-lugar-fecha/', CiudadPaisFechaOptionsView.as_view(), name='opciones-lugar-fecha'),
#
#    path('cartaporte/<pk>/', CartaporteDocView.as_view(), name='cartaporte-documento'),
#
#    #path('cartaportes/', views.CartaporteListView.as_view(), name='cartaportes'),
#    path('cartaportes/', views_Filters.cartaportesFilterView, name='cartaportes'),
#    path('cartaportes_filter/', views_Filters.cartaportesFilterView, name='cartaportes_filter'),
#    path('cartaportes/<pk>', views.CartaporteDetailView.as_view(), name='cartaporte-detail'),
#    path('cartaporte/create/', views.CartaporteCreate.as_view(), name='cartaporte-create'),
#    path('cartaporte/<pk>/update/', views.CartaporteUpdate.as_view(), name='cartaporte-update'),
#    path('cartaporte/<pk>/delete/', views.CartaporteDelete.as_view(), name='cartaporte-delete'),

	#-- URLs manifiesto -----------------------------------------------
    path("manifiesto/", ManifiestoDocView.as_view(), name="manifiesto"),
    path("manifiesto/importacion", ManifiestoDocView.as_view(), name="manifiesto-importacion"),
    path("manifiesto/exportacion", ManifiestoDocView.as_view(), name="manifiesto-exportacion"),

    path('manifiesto/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
    path('manifiesto/<pk>/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
    path('manifiesto/opciones-vehiculo/', VehiculoOptionsView.as_view(), name='opciones-vehiculo'),
    path('manifiesto/opciones-conductor/', ConductorOptionsView.as_view(), name='opciones-conductor'),
    path('manifiesto/opciones-cartaporte/', CartaporteOptionsView.as_view(), name='opciones-cartaporte'),

    path('manifiesto/<pk>/opciones-cartaporte/', CartaporteOptionsView.as_view(), name='opciones-cartaporte'),
    path('manifiesto/<pk>/opciones-vehiculo/', VehiculoOptionsView.as_view(), name='opciones-vehiculo'),
    path('manifiesto/<pk>/opciones-conductor/', ConductorOptionsView.as_view(), name='opciones-conductor'),

    path('manifiesto/<pk>/', ManifiestoDocView.as_view(), name='manifiesto-documento'),

    #path('manifiestos/', views.ManifiestoListView.as_view(), name='manifiestos'),
    path('manifiestos/', views_Filters.manifiestosFilterView, name='manifiestos'),
    path('manifiestos_filter/', views_Filters.manifiestosFilterView, name='manifiestos_filter'),
    path('manifiestos/<pk>', views.ManifiestoDetailView.as_view(), name='manifiesto-detail'),
    path('manifiesto/create/', views.ManifiestoCreate.as_view(), name='manifiesto-create'),
    path('manifiesto/<pk>/update/', views.ManifiestoUpdate.as_view(), name='manifiesto-update'),
    path('manifiesto/<pk>/delete/', views.ManifiestoDelete.as_view(), name='manifiesto-delete'),

	#-- URLs for comandos --------------------------------------------
    path('cartaporte/<pk>/<comando>/', ComandosCartaporteView.as_view(), name='cartaporte-comandos'),
    path('manifiesto/<pk>/<comando>/', ComandosManifiestoView.as_view(), name='manifiesto-comandos'),

	#-- URLs declaracion -----------------------------------------------
    path("declaracion/", DeclaracionDocView.as_view(), name="declaracion"),
    path('declaracion/opciones-empresa/', EmpresaOptionsView.as_view(), name='opciones-empresa'),
    path('declaracion/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
    path('declaracion/opciones-vehiculo/', VehiculoOptionsView.as_view(), name='opciones-vehiculo'),
    path('declaracion/opciones-conductor/', ConductorOptionsView.as_view(), name='opciones-conductor'),
    path('declaracion/opciones-cartaporte/', CartaporteOptionsView.as_view(), name='opciones-cartaporte'),

    path('declaracion/<pk>/opciones-empresa/', EmpresaOptionsView.as_view(), name='opciones-empresa'),
    path('declaracion/<pk>/opciones-lugar/', CiudadPaisOptionsView.as_view(), name='opciones-lugar'),
    path('declaracion/<pk>/opciones-vehiculo/', VehiculoOptionsView.as_view(), name='opciones-vehiculo'),
    path('declaracion/<pk>/opciones-conductor/', ConductorOptionsView.as_view(), name='opciones-conductor'),
    path('declaracion/<pk>/opciones-cartaporte/', CartaporteOptionsView.as_view(), name='opciones-cartaporte'),
    path('declaracion/<pk>/', DeclaracionDocView.as_view(), name='declaracion-documento'),

    path('declaraciones/', views.DeclaracionListView.as_view(), name='declaraciones'),
    path('declaraciones/<pk>', views.DeclaracionDetailView.as_view(), name='declaracion-detail'),
    path('declaracion/create/', views.DeclaracionCreate.as_view(), name='declaracion-create'),
    path('declaracion/<pk>/update/', views.DeclaracionUpdate.as_view(), name='declaracion-update'),
    path('declaracion/<pk>/delete/', views.DeclaracionDelete.as_view(), name='declaracion-delete'),

	#-- URLs entities --------------------------------------------------
    path('empresas/', views.EmpresaListView.as_view(), name='empresas'),
    path('empresa/<pk>', views.EmpresaDetailView.as_view(), name='empresa-detail'),
    path('empresa/create/', views.EmpresaCreate.as_view(), name='empresa-create'),
    path('empresa/<pk>/update/', views.EmpresaUpdate.as_view(), name='empresa-update'),
    path('empresa/<pk>/delete/', views.EmpresaDelete.as_view(), name='empresa-delete'),

    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculos'),
    path('vehiculo/<pk>', views.VehiculoDetailView.as_view(), name='vehiculo-detail'),
    path('vehiculo/create/', views.VehiculoCreate.as_view(), name='vehiculo-create'),
    path('vehiculo/<pk>/update/', views.VehiculoUpdate.as_view(), name='vehiculo-update'),
    path('vehiculo/<pk>/delete/', views.VehiculoDelete.as_view(), name='vehiculo-delete'),

    path('conductors/', views.ConductorListView.as_view(), name='conductors'),
    path('conductor/<pk>', views.ConductorDetailView.as_view(), name='conductor-detail'),
    path('conductor/create/', views.ConductorCreate.as_view(), name='conductor-create'),
    path('conductor/<pk>/update/', views.ConductorUpdate.as_view(), name='conductor-update'),
    path('conductor/<pk>/delete/', views.ConductorDelete.as_view(), name='conductor-delete'),

	#-- Other URLs  --------------------------------------------------
    path('info/', InfoView.as_view(), name='info_view'),
]

