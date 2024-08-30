from django.urls import path

from . import views
from . import views_Filters

from .views import InfoView

from app_manifiesto.views_ManifiestoDocView import *
from app_cartaporte.views_CartaporteDocView import *
from app_declaracion.views_DeclaracionDocView import *
from .views_Events import *

urlpatterns = [
    path('', views.index, name='index'),

	#-- URLs entities --------------------------------------------------
    path('clientes/', views.ClienteListView.as_view(), name='clientes'),
    path('cliente/<pk>', views.ClienteDetailView.as_view(), name='cliente-detail'),
    path('cliente/create/', views.ClienteCreate.as_view(), name='cliente-create'),
    path('cliente/<pk>/update/', views.ClienteUpdate.as_view(), name='cliente-update'),
    path('cliente/<pk>/delete/', views.ClienteDelete.as_view(), name='cliente-delete'),

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

