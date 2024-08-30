from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views as auth_views

from app_docs import views

admin.site.site_header = "Creación/Almacenamiento de Documentos del ECUAPASS"
admin.site.site_title  = "Creación/Almacenamiento de Documentos del ECUAPASS"
admin.site.index_title = "Creación/Almacenamiento de Documentos del ECUAPASS Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("usuarios/", include("app_usuarios.urls")),
    path("documentos/", include("app_docs.urls")),
    path("cartaporte/", include("app_cartaporte.urls_cpi")),
    path("manifiesto/", include("app_manifiesto.urls_mci")),
    path("declaracion/", include("app_declaracion.urls_dti")),
    path("reportes/", include("appreportes.urls")),
    path('', views.index, name='index'),
]

