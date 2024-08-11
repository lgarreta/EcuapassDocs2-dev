from django.urls import path

from . import views
from . import views_Filters

from .views import InfoView

from app_manifiestos.views_ManifiestoDocView import *
from app_cartaportes.views_CartaporteDocView import *
from .views_DeclaracionDocView import *
from .views_Entidades import *

urlpatterns = [
    path('', views.index, name='index'),

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

